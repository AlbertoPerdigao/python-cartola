from typing import Dict
import requests
from app.messages import ERROR_GETTING_CARTOLA_STATUS, ERROR_GETTING_CARTOLA_TEAM_SCORE

CARTOLA_STATUS_URI = "https://api.cartolafc.globo.com/mercado/status"
CARTOLA_TEAM_SCORE_URI = "https://api.cartola.globo.com/time/id/{}"  # [team id_tag]


class CartolaApi:
    @classmethod
    def get_cartola_status(cls) -> Dict:
        try:
            return requests.get(CARTOLA_STATUS_URI).json()
        except:
            return {"message": ERROR_GETTING_CARTOLA_STATUS}, 500

    @classmethod
    def get_cartola_team_by_team_id_tag(
        cls, id_tag: int
    ) -> Dict:
        try:
            return requests.get(
                CARTOLA_TEAM_SCORE_URI.format(id_tag)
            ).json()
        except:
            return {"message": ERROR_GETTING_CARTOLA_TEAM_SCORE}, 500
