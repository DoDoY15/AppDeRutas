# app/services/priority_service.py

from typing import List, Tuple
from app.db.models import PointOfStop
from datetime import datetime, date

# ==============================================================
# =========== CONFIGURACION DE PESOS Y PRIORIDAD ===============
# ==============================================================
W_ATRASOS = 1.5
W_FREQUENCIA = 1.0
W_FLAG_PRIORIDAD = 1.0
# ==============================================================

class PriorityService:

    def calculate_global_priority_scores(
        self, pdv_pool: List[PointOfStop]
    ) -> List[Tuple[PointOfStop, float]]:
        """
        Recebe a lista completa de PDVs e retorna uma lista de
        tuplas (PDV, score), ordenada da maior pontuação para a menor.
        """
        weighted_list = []
        default_date = date(1970, 1, 1)
        today = datetime.now().date()

        for pdv in pdv_pool:
            last_visit_date = pdv.last_visited_at.date() if pdv.last_visited_at else default_date
            dias_desde_visita = (today - last_visit_date).days

            frequencia = pdv.visits_per_week
            flag_prioritaria = 1 if pdv.priority else 0

            priority_score = (dias_desde_visita * W_ATRASOS) + \
                             (frequencia * W_FREQUENCIA) + \
                             (flag_prioritaria * W_FLAG_PRIORIDAD)

            weighted_list.append((pdv, priority_score))

        weighted_list.sort(key=lambda item: item[1], reverse=True)
        
        return weighted_list