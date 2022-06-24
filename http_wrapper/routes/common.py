from typing import List
from pydantic import BaseModel, Field

class BModel(BaseModel):
    class Config:
        use_enum_values: True
        allow_population_by_field_name = True

class PostReqModel(BModel):
    parcellation_id: str
    roi_1: str
    roi_2: str
    genes: List[str]
    permutations: int = Field(1000)
    threshold: float = Field(0.2)

def reverse_param(post_req: PostReqModel):
    return {
        'parcellation_id': post_req.parcellation_id,
        'roi_1': post_req.roi_1,
        'roi_2': post_req.roi_2,
        'comma_delimited_genes': ','.join(post_req.genes),
        'permutations': post_req.permutations,
        'threshold': post_req.threshold,
    }

def common_params(
    parcellation_id:str,
    roi_1:str,
    roi_2:str,
    comma_delimited_genes:str,
    permutations:int=100,
    threshold:float=0.2,
):
    return PostReqModel(
        parcellation_id=parcellation_id,
        roi_1=roi_1,
        roi_2=roi_2,
        genes=comma_delimited_genes.split(','),
        permutations=permutations,
        threshold=threshold,
    )
