from threading import Lock

from flask.views import MethodView
from flask_smorest import Blueprint, abort

from android_bot import AndroidBot
from lib.honda import obtine_cod_radio_honda
from schemas import RadioCodeSchema

blp = Blueprint('Radio Code', __name__, description='Get radio codes for Renault cars')
bot_lock = Lock()


@blp.route('/radio_code/<string:marca>/<string:vin>')
class RadioCode(MethodView):
    @blp.response(200, RadioCodeSchema)
    def get(self, marca, vin):
        try:
            if marca.lower() == 'honda':
                print(f'[+] Obținere cod radio pentru {marca.capitalize()} Serial: {vin}...')
                coduri = obtine_cod_radio_honda(vin)
                print(f'[+] Coduri radio obținute: {coduri}')
                return RadioCodeSchema().dump({'serie': vin, 'marca': marca.capitalize(), 'radio_code': coduri})
            with bot_lock:
                bot = AndroidBot()
                cod = bot.get_radio_code(marca=marca, vin=vin)
                return RadioCodeSchema().dump({'vin': vin, 'marca': marca.capitalize(), 'radio_code': [cod]})
        except Exception as e:
            abort(500, message=str(e))
