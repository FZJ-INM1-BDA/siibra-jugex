from os import path
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.templating import Jinja2Templates
import nbformat
from nbconvert import HTMLExporter

from siibra_jugex_http.routes.common import PostReqModel, common_params, reverse_param

html_exporter = HTMLExporter(template_name="classic")
router = APIRouter()

root_dir=path.abspath(
    path.join((
        path.dirname(__file__),
        "../.."
    ))
)
templates = Jinja2Templates(directory=path.join(root_dir, "siibra_jugex_http/templates/"))

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
    
    return templates.TemplateResponse(
        "preview_nb.jinja",
        context={
            "request": request,
            "notebook_name": f"{get_notebook_name(post_req)}.ipynb",
            "download_notebook_url": f"download?{urlencode(reverse_param(post_req))}",
            "view_notebook_url": f"notebook?{urlencode(reverse_param(post_req))}",
            "user": None
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
