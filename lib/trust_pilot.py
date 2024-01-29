import requests


def _fetch_trustpilot_data(domeniu):
    url = f"https://www.trustpilot.com/_next/data/businessunitprofile-consumersite-2.71.0/review/{domeniu}.json"

    querystring = {"businessUnit": domeniu}

    payload = ""
    headers = {
        "authority": "www.trustpilot.com",
        "accept": "*/*",
        "accept-language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "dnt": "1",
        "pragma": "no-cache",
        "referer": f"https://www.trustpilot.com/review/{domeniu}",
        "sec-ch-ua": r"^\^Not",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": r"^\^Windows^^",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/121.0.0.0 Safari/537.36",
        "x-nextjs-data": "1"
    }

    response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
    return response.json()


def get_trustpilot_reviews(domeniu):
    data = _fetch_trustpilot_data(domeniu)
    toal_reviews = data['pageProps']['businessUnit']['numberOfReviews']
    reviews = [
        {
            'id': review['id'],
            'titlu': review['title'],
            'comentariu': review['text'],
            'nota': review['rating'],
            'nume': review['consumer']['displayName']
        } for review in data['pageProps']['reviews']
    ]
    return {
        'domeniu': domeniu,
        'toal_reviews': toal_reviews,
        'reviews': reviews
    }
