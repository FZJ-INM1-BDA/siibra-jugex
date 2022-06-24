from typing import List
import os
import logging

CHANNEL = os.getenv("SIIBRA_JURGEX_CELERY_CHANNEL", "siibra_jugex_http")

logger = logging.getLogger(__name__)

try:
    from celery import Celery
except ImportError as e:
    logger.critical(f"Importing celery error")
    raise e

default_config="http_wrapper.conf.celeryconfig"
app = Celery(CHANNEL)
app.config_from_object(default_config)

@app.task
def analysis(parcellation_id: str, roi_1:str, roi_2: str, genes: List[str], permutations: int, threshold: float):
    from siibra_jugex import DifferentialGeneExpression
    import siibra
    import socket

    hostname = socket.gethostname()
    logger.info(f"{hostname}:task:rec")
    logger.debug(f"{hostname}:task:rec_param {parcellation_id} {roi_1} {roi_2}, {','.join(genes)}")

    try:
        parc = siibra.parcellations[parcellation_id]

        jugex = DifferentialGeneExpression(parc)
        jugex.add_candidate_genes(genes)
        jugex.define_roi1(roi_1, maptype=siibra.MapType.CONTINUOUS, threshold=threshold)
        jugex.define_roi2(roi_2, maptype=siibra.MapType.CONTINUOUS, threshold=threshold)
        
        result = jugex.run(permutations)
        
        mnicoords = [{
            "roi": roi,
            "mnicoord": [s["mnicoord"] for s in jugex.get_samples(roi).values()]
        } for roi in [roi_1, roi_2]]

        logger.info(f"{hostname}:task:success")
        logger.debug(f"{hostname}:task:success_result {result}")
        return {
            "result": result,
            "mnicoords": mnicoords
        }
    except Exception as e:
        logger.critical(f"{hostname}:task:failed {str(e)}")
        raise e
