from app import api
from resources.team import Team, TeamList
from resources.month import Month, MonthList
from resources.payment import Payment, PaymentList
from resources.prize import Prize, PrizeList
from resources.round import Round, RoundList
from resources.winner import Winner, WinnerList, WinnerPrizesCalculation
from resources.score import Score, ScoreList

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
api.add_resource(WinnerPrizesCalculation, "/winners/auto_calculation")

api.add_resource(Score, "/score/<int:id>")
api.add_resource(ScoreList, "/scores/<int:year>")
