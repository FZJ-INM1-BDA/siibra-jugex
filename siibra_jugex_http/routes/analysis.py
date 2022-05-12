from enum import Enum
from typing import Dict, List, Optional
from fastapi import APIRouter
from pydantic import Field

from siibra_jugex_http.routes.common import PostReqModel, BModel
from siibra_jugex_http.scheduling.worker import analysis

router = APIRouter()

class PostRespModel(BModel):
    poll_url: str

class ResultStatus(str, Enum):
    SUCCESS="SUCCESS"
    FAILURE="FAILURE"
    PENDING="PENDING"


class JugexAnalysisResult(BModel):
    race: List[str]
    age: List[int]
    specimen: List[str]
    area: List[str]
    zscores: Dict[str, List[float]]
    p_values: Dict[str, float] = Field(..., alias="p-values")


class JugexMNICoord(BModel):
    roi: str
    mnicoord: List[List[float]]


class JugexResult(BModel):
    result: JugexAnalysisResult
    mnicoords: List[JugexMNICoord]


class ResultModel(BModel):
    status: ResultStatus
    result: Optional[JugexResult]


@router.post('/analysis', response_model=PostRespModel)
def post_analysis(post_req: PostReqModel):

    res = analysis.delay(**post_req.dict())
    return PostRespModel(
        poll_url=res.id
    )

@router.get('/analysis/{analysis_id}', response_model=ResultModel)
def get_analysis_with_id(analysis_id: str):

    res = analysis.AsyncResult(analysis_id)
    if res.state == "FAILURE":
        res.forget()
        return ResultModel(
            status=ResultStatus.FAILURE
        )
    if res.state == "SUCCESS":
        result = res.get()
        res.forget()
        return ResultModel(
            status=ResultStatus.SUCCESS,
            result=JugexResult(**result)
        )
    return ResultModel(
        status=ResultStatus.PENDING
    )