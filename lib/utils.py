import json
import subprocess

from filelock import FileLock

from lib.constants import ERORI, LOCK_PATH, FWUID_PATH

lock = FileLock(LOCK_PATH, timeout=10)


def cauta_mesaj_eroare(text):
    for eroare in ERORI:
        if eroare.lower() in text.lower():
            return text
    return False


def _executa_comanda(comanda):
    process = subprocess.Popen(comanda, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8')


def verifica_aplicatie_deschisa(package_name):
    commanda_exista_in_proces = f"adb shell ps | findstr {package_name}"
    commanda_verifica_deschidere_reala = f'adb shell dumpsys activity activities | findstr {package_name}'
    raspuns = _executa_comanda(commanda_exista_in_proces)
    if package_name in raspuns:
        raspuns = _executa_comanda(commanda_verifica_deschidere_reala)
        if not raspuns:
            return 'deschide'
        else:
            return 'activeaza'
    else:
        return 'deschide'


def analizeaza_raspuns_honda(data):
    # Verificăm dacă există erori în răspuns
    if 'error' in data and data['error']:
        print(f"[-] Eroare: {data['error']}")
        raise Exception(f"Eroare: {data['error']}")

    # Inițializăm o listă pentru a stoca codurile radio
    radio_codes = []

    # Extragerea codurilor radio
    actions = data.get('actions', [])
    for action in actions:
        if action.get('state') == 'SUCCESS':
            return_value = action.get('returnValue', {}).get('returnValue', {})
            radio_code_bodies = return_value.get('RadioCodeBody', [])
            for item in radio_code_bodies:
                if 'Code' in item:
                    radio_codes.append(item['Code'])
    if radio_codes:
        return radio_codes
    else:
        print("[-] Nu s-au găsit coduri radio!")
        raise Exception("Nu s-au găsit coduri radio!")


def obtine_cheie():
    with lock:
        with open(FWUID_PATH, 'r') as file:
            data = json.load(file)
        # Procesați datele aici
        return data['fwuid']


def salveaza_cheie(cheie):
    with lock:
        # Scrierea fișierului JSON
        try:
            with open(FWUID_PATH, 'w') as file:
                json.dump({'fwuid': cheie}, file)
        except Exception as e:
            print(f"An error occurred: {e}")


def obtine_noua_cheie(data):
    # Verificăm dacă există un mesaj de excepție și căutăm cheia
    exception_message = data.get("exceptionMessage", "")
    marker = "Expected: "
    start_idx = exception_message.find(marker)
    if start_idx != -1:
        # Extragem șirul de caractere după "Expected: " până la următorul spațiu
        start_idx += len(marker)
        end_idx = exception_message.find(" ", start_idx)
        key = exception_message[start_idx:end_idx]
        return key
    else:
        print("[-] Markerul 'Expected:' nu a fost găsit în mesajul de excepție.")
        raise Exception("Marker 'Expected:' not found in the exception message.")
