from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from fastapi.exceptions import HTTPException

router = APIRouter()

# @router.get("/{repo}.git/info/refs")
# def info_refs():
#     return PlainTextResponse(
#         """db53a06240ccf01b51eefa3ee348a12e360db2bd\trefs/heads/master"""
#     )

# @router.get("/{repo}.git/HEAD")
# def head():
#     return PlainTextResponse(
#         """ref: refs/heads/master\n"""
#     )

# @router.get("/objects/{head}/{rest}")
# def get_obj():
#     print("foo")
#     raise HTTPException(404)