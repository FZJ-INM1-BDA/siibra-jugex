from enum import Enum
from typing import Any, Dict, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from scheduling.worker import analysis, app

class BModel(BaseModel):
    class Config:
        use_enum_values: True
        allow_population_by_field_name = True

router = APIRouter()

class PostReqModel(BModel):
    parcellation_id: str
    roi_1: str
    roi_2: str
    genes: List[str]
    permutations: int = Field(1000)

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

class ResultModel(BModel):
    status: ResultStatus
    result: Optional[JugexAnalysisResult]


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
            result=JugexAnalysisResult(**result)
        )
    return ResultModel(
        status=ResultStatus.PENDING
    )