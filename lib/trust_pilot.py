import re

import requests


def _extract_version(sursa):
    pattern = r"businessunitprofile-consumersite-([0-9]+\.[0-9]+\.[0-9]+)"
    match = re.search(pattern, sursa)
    if match:
        version = match.group(1)
        print(version)
        return version
    else:
        print("[-] Versiunea nu a fost găsită")
        raise Exception("Versiunea nu a fost găsită")


def _get_trustpilot_api_version(domeniu):
    url = f'https://www.trustpilot.com/review/{domeniu}'

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
                  "application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
        "Connection": "keep-alive",
        "Dnt": "1",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/121.0.0.0 Safari/537.36"
    }

    response = requests.request("GET", url, headers=headers)

    if response.status_code == 200:
        sursa = response.text
        return _extract_version(sursa)
    else:
        print("[-] Eroare la obținerea versiunii API-ului TrustPilot", response.status_code)
        raise Exception("Eroare la obținerea versiunii API-ului TrustPilot")


def _fetch_trustpilot_data(domeniu):
    versiune = _get_trustpilot_api_version(domeniu)
    url = f"https://www.trustpilot.com/_next/data/businessunitprofile-consumersite-{versiune}/review/{domeniu}.json"

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
        'total_reviews': toal_reviews,
        'reviews': reviews
    }
