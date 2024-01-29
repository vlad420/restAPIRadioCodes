import json
import urllib.parse
from json.decoder import JSONDecodeError

import requests
import urllib3

from lib.utils import analizeaza_raspuns_honda, obtine_cheie, obtine_noua_cheie, salveaza_cheie

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _request_honda(nr_serie):
    url = "https://mygarage.honda.com/s/sfsites/aura"

    querystring = {"r": "7", "aura.ApexAction.execute": "1"}

    data = {
        "message": {
            "actions": [
                {
                    "descriptor": "aura://ApexActionController/ACTION$execute",
                    "callingDescriptor": "UNKNOWN",
                    "params": {
                        "namespace": "",
                        "classname": "OwnAPIController",
                        "method": "getRadioCode",
                        "params": {
                            "code": nr_serie
                        },
                        "cacheable": False,
                        "isContinuation": False
                    }
                }
            ]
        },
        "aura.context": {
            "mode": "PROD",
            "fwuid": obtine_cheie(),
            "app": "siteforce:communityApp",
            "loaded": {
                "APPLICATION@markup://siteforce:communityApp": "xUUH_isHmNQqCOJ9yNTV7A",
                "COMPONENT@markup://instrumentation:o11ySecondaryLoader": "iVoI_RYCX4m4O5loBTnQfA"
            },
            "dn": [],
            "globals": {},
            "uad": False,
        },
        "aura.pageURI": "/s/radio-nav-code?brand=Honda",
        "aura.token": "null",
    }

    json_string = 'message=' + urllib.parse.quote(json.dumps(data["message"]))
    context_string = '&aura.context=' + urllib.parse.quote(json.dumps(data["aura.context"]))
    page_uri_string = '&aura.pageURI=' + urllib.parse.quote(data["aura.pageURI"])
    token_string = '&aura.token=' + urllib.parse.quote(data["aura.token"])

    payload = json_string + context_string + page_uri_string + token_string
    headers = {
        "authority": "mygarage.honda.com",
        "accept": "*/*",
        "accept-language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "dnt": "1",
        "origin": "https://mygarage.honda.com",
        "referer": "https://mygarage.honda.com/s/radio-nav-code?brand=Honda",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "x-sfdc-lds-endpoints": "ApexActionController.execute:OwnAPIController.getRadioCode"
    }

    return requests.request("POST", url, data=payload, headers=headers, params=querystring, verify=False)


def obtine_cod_radio_honda(nr_serie):
    response = _request_honda(nr_serie)
    try:
        return analizeaza_raspuns_honda(response.json())
    except JSONDecodeError:
        error = response.text.replace('*/', '').replace('/*ERROR', '')
        error_response = json.loads(error)
        cheie_noua = obtine_noua_cheie(error_response)
        salveaza_cheie(cheie_noua)
        response = _request_honda(nr_serie)
        return analizeaza_raspuns_honda(response.json())
