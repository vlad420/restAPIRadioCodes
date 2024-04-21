from flask import Flask
from flask_smorest import Api
from resources.radio_code import blp as RadioCodeBluePrint
from resources.trust_pilot_reviews import blp as TrustPilotReviewsBluePrint
app = Flask(__name__)

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['API_TITLE'] = 'Renault Radio Codes API'
app.config['API_VERSION'] = 'v1'
app.config['OPENAPI_VERSION'] = '3.0.3'
app.config['OPENAPI_URL_PREFIX'] = '/'
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

api.register_blueprint(RadioCodeBluePrint)
api.register_blueprint(TrustPilotReviewsBluePrint)

if __name__ == '__main__':
    # app.run(debug=True)
    from waitress import serve
    serve(app, host='0.0.0.0', port=80)
