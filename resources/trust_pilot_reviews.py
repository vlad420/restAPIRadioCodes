from flask.views import MethodView
from flask_smorest import Blueprint, abort

from lib.trust_pilot import get_trustpilot_reviews
from schemas import TrustPilotReviewsSchema

blp = Blueprint('TrustPilot reviews', __name__, description='Get first 20 TrustPilot reviews')


@blp.route('/trustpilot_reviews/<string:domeniu>')
class TrustPilotReviews(MethodView):
    @blp.response(200, TrustPilotReviewsSchema)
    def get(self, domeniu):
        try:
            return TrustPilotReviewsSchema().dump(get_trustpilot_reviews(domeniu))
        except Exception as e:
            abort(500, message=str(e))
