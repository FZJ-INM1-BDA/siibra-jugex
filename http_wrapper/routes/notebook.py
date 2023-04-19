from os import path
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, Response, RedirectResponse
from fastapi.templating import Jinja2Templates
import nbformat
from nbconvert import HTMLExporter
from enum import Enum
import os
from uuid import uuid4
from urllib.parse import quote, quote_plus
from http_wrapper.routes.common import PostReqModel, common_params, reverse_param

HBP_GITLAB_HOST = os.getenv("HBP_GITLAB_HOST") 
HBP_GITLAB_TOKEN = os.getenv("HBP_GITLAB_TOKEN")
HBP_GITLAB_PROJECT_ID = os.getenv("HBP_GITLAB_PROJECT_ID")

run_now_enabled = HBP_GITLAB_HOST is not None and HBP_GITLAB_TOKEN is not None and HBP_GITLAB_PROJECT_ID is not None

class NotebookExecutionSite(Enum):
    EBRAINS_LAB="EBRAINS_LAB"
    MY_BINDER="MY_BINDER"

def get_jupyterhub_link(site: NotebookExecutionSite, git_url: str, branch: str, filename: str) -> str:
    if site == NotebookExecutionSite.EBRAINS_LAB:
        return "https://lab.ebrains.eu/hub/user-redirect/git-pull?repo={repo}&urlpath={urlpath}&branch={branch}&targetPath={branch}".format(
            repo=quote(git_url),
            urlpath=quote(f'lab/tree/{branch}/{filename}'),
            branch=quote(branch),
        )
    if site == NotebookExecutionSite.MY_BINDER:
        return "https://mybinder.org/v2/git/{repo}/{branch}?labpath={filename}".format(
            repo=quote_plus(git_url),
            branch=quote_plus(branch),
            filename=quote_plus(filename)
        )
    raise ValueError(f"site {site} not defined.")

html_exporter = HTMLExporter(template_name="classic")
router = APIRouter()

root_dir=path.abspath(
    path.join(
        path.dirname(__file__),
        "../.."
    )
)
templates = Jinja2Templates(directory=path.join(root_dir, "http_wrapper/templates/"))

def get_notebook(post_req:PostReqModel):
    path_to_notebook = path.join(root_dir, "examples/siibra-jugex.ipynb")
    with open(path_to_notebook, "r") as fp:
        notebook = nbformat.read(fp, as_version=4)

    for cell in notebook.cells:
        if cell.get("cell_type") != "code":
            continue
        if "# set analysis parameters" not in cell.get("source"):
            continue
        cell_source = cell["source"]
        import re, json
        cell_source = re.sub(r"\ncandidate_regions.*?\n", f"\ncandidate_regions = { json.dumps([post_req.roi_1, post_req.roi_2]) }\n", cell_source)
        cell_source = re.sub(r"\ncandidate_genes.*?\n", f"\ncandidate_genes = { json.dumps(post_req.genes) }\n", cell_source)
        cell_source = re.sub(r"\nthreshold.*?\n", f"\nthreshold = { post_req.threshold }\n", cell_source)
        cell_source = re.sub(r"\npermutations.*?\n", f"\npermutations = { post_req.permutations }\n", cell_source)
        cell["source"] = cell_source
        break
    return notebook

TAGS = ["notebook"]

def get_notebook_name(post_req: PostReqModel):
    def sanitize(input: str):
        import re
        return re.sub(r"\W", "_", input)
    return_dict = {
        "r1": sanitize(post_req.roi_1),
        "r2": sanitize(post_req.roi_2),
        "g": sanitize('_'.join(post_req.genes)),
        "p": sanitize(str(post_req.permutations)),
        "th": sanitize(str(post_req.threshold)),
    }
    return "__".join([f"{key}_{return_dict[key]}" for key in return_dict])

@router.get('/view', response_class=HTMLResponse, tags=TAGS)
def show_notebook(request: Request, post_req:PostReqModel = Depends(common_params)):
    from urllib.parse import urlencode
    
    run_now_context = {
        "run_ebrains_lab": f"run?site=EBRAINS_LAB&{urlencode(reverse_param(post_req))}",
        "run_my_binder": f"run?site=MY_BINDER&{urlencode(reverse_param(post_req))}",
    } if run_now_enabled else {}
    return templates.TemplateResponse(
        "preview_nb.jinja",
        context={
            "request": request,
            "notebook_name": f"{get_notebook_name(post_req)}.ipynb",
            "download_notebook_url": f"download?{urlencode(reverse_param(post_req))}",
            "view_notebook_url": f"notebook?{urlencode(reverse_param(post_req))}",
            "user": None,
            **run_now_context,
        }
    )


@router.get('/notebook', response_class=HTMLResponse, tags=TAGS)
def show_notebook(post_req:PostReqModel = Depends(common_params)):
    notebook = get_notebook(post_req)
    (body, resources) = html_exporter.from_notebook_node(notebook)
    return HTMLResponse(content=body)


@router.get('/download', response_class=FileResponse, tags=TAGS)
def download_notebook(post_req:PostReqModel = Depends(common_params)):
    notebook = get_notebook(post_req)
    import json
    resp = Response(
        content=json.dumps(notebook, indent=4),
        headers={
            "Content-Disposition": f"attachment; filename={get_notebook_name(post_req)}.ipynb"
        },
        status_code=200,
        media_type="application/json"
    )
    return resp

# Only add run endpoint if the necesary env vars are defined
if run_now_enabled:

    # Do not use async, or else it will be blocking
    def delete_branch(branch: str):
        from datetime import datetime
        from http_wrapper.server import kill_event
        from time import sleep

        start = datetime.now()

        diff_seconds = 0
        while not kill_event.is_set() and diff_seconds < 600:
            
            diff_seconds = (datetime.now() - start).seconds
            sleep(5)
        
        from gitlab import Gitlab
        gl = Gitlab(url=HBP_GITLAB_HOST, private_token=HBP_GITLAB_TOKEN)
        project = gl.projects.get(HBP_GITLAB_PROJECT_ID)
        project.branches.delete(branch)
        

    @router.get("/run", tags=TAGS)
    def run_notebook(background_tasks: BackgroundTasks, site: NotebookExecutionSite, post_req:PostReqModel = Depends(common_params)):
        notebook = get_notebook(post_req)
        notebook_filename = f"{get_notebook_name(post_req)}.ipynb"

        from gitlab import Gitlab
        import json

        gl = Gitlab(url=HBP_GITLAB_HOST, private_token=HBP_GITLAB_TOKEN)
        project = gl.projects.get(HBP_GITLAB_PROJECT_ID)

        branch_name = f"tmp-{uuid4()}"
        project.branches.create({
            'branch': branch_name,
            'ref': 'main'
        })

        project.files.create({
            'file_path': notebook_filename,
            'branch': branch_name,
            'content': json.dumps(notebook, indent=4),
            # 'encoding': 'utf-8',
            'commit_message': 'creating file'
        })
        redirect_url = get_jupyterhub_link(site, project.attributes.get("http_url_to_repo"), branch_name, notebook_filename)

        background_tasks.add_task(delete_branch, branch_name)
        return RedirectResponse(redirect_url)
