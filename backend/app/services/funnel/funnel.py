from sqlalchemy.orm import Session
from .priority_filter import filter_pdvs_by_haversine
from .priority_filter import calculate_priority_scores
from .priority_filter import get_data_pool

def run_optimization_funnel(db: Session):
    all_pdvs, all_workers = get_data_pool(db)

    worker_pdv_map = {}
    for worker in all_workers:

        geo_candidates = filter_pdvs_by_haversine(worker, all_pdvs)
        prioritized_candidates = calculate_priority_scores(geo_candidates)

        MAX_PDVS_PARA_OTIMIZAR_POR_TRABALHADOR = 50

        optimized_pdv_list = [
            pdv for (pdv, score) in prioritized_candidates[:MAX_PDVS_PARA_OTIMIZAR_POR_TRABALHADOR]
        ]
        worker_pdv_map[worker.id] = optimized_pdv_list
    
    return worker_pdv_map