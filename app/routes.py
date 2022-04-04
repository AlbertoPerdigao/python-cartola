from app import api
from resources.team import Team, TeamList
from resources.month import Month, MonthList
from resources.payment import Payment, PaymentList
from resources.prize import Prize, PrizeList
from resources.round import Round, RoundList
from resources.winner import Winner, WinnerList
from resources.score import Score, ScoreList, ScoreCartolaUpdate
from resources.winner_prizes_calculation import WinnerPatrimonioCalculation, WinnerPrizesCalculation, WinnerCampeonatoCalculation, WinnerTurnoCalculation

api.add_resource(Team, "/team/<int:id>")
api.add_resource(TeamList, "/teams")

api.add_resource(Month, "/month/<int:id>")
api.add_resource(MonthList, "/months/<int:year>")

api.add_resource(Payment, "/payment/<int:id>")
api.add_resource(PaymentList, "/payments/<int:year>")

api.add_resource(Prize, "/prize/<int:id>")
api.add_resource(PrizeList, "/prizes/<int:year>")

api.add_resource(Round, "/round/<int:id>")
api.add_resource(RoundList, "/rounds/<int:year>")

api.add_resource(Winner, "/winner/<int:id>")
api.add_resource(WinnerList, "/winners/<int:year>")
api.add_resource(WinnerPrizesCalculation, "/winners/prizes_calculation")
api.add_resource(WinnerCampeonatoCalculation, "/winners/campeonato_calculation")
api.add_resource(WinnerTurnoCalculation, "/winners/turno_calculation")
api.add_resource(WinnerPatrimonioCalculation, "/winners/patrimonio_calculation")

api.add_resource(Score, "/score/<int:id>")
api.add_resource(ScoreList, "/scores/<int:year>")
# api.add_resource(ScoreCartolaUpdate, "/scores/cartola_update_teams_scores")
