import json
import shlex
import subprocess
import re
import time
import pygetwindow as gw

from filelock import FileLock

from lib.constants import ERORI, LOCK_PATH, FWUID_PATH, APPIUM_ROOT_COMMAND, EMULATOR_PARTIAL_WINDOW_NAME, \
    TIMP_ASTEPTARE_INCARCARE_EMULATOR, TIMP_ASTEPTARE_VERIFICARE_STATUS_EMULATR, TIME_OUT_START_EMULATOR, \
    TIME_ASTEPTARE_FEREASTRA_START_EMULATOR, EMULATOR_STARTIGN_WINDOW_NAME

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


def _list_devices():
    # Definește comanda completă, inclusiv calea către executabil și argumentele necesare
    command = f"{APPIUM_ROOT_COMMAND} list"

    # Rulează comanda și captează output-ul
    process = subprocess.run(command, shell=True, text=True, capture_output=True)

    # Verifică dacă există erori
    if process.stderr:
        print("[-] Eroare:", process.stderr)
        raise Exception(
            "Eroare la interogarea device-lor"
        )
    else:
        # Afișează output-ul comenzi
        return process.stdout


def _extrage_uuid(output):
    # Definim un pattern pentru UUID folosind expresii regulate
    pattern_uuid = r'\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b'

    # Căutăm toate potrivirile pattern-ului în output
    uuids = re.findall(pattern_uuid, output, re.IGNORECASE)

    return uuids[0]


def _start_device(id):
    # Definește comanda completă, inclusiv calea către executabil și argumentele necesare
    command = f"{APPIUM_ROOT_COMMAND} start {id}"

    # # Rulează comanda și captează output-ul
    # process = subprocess.run(command, shell=True, text=True, capture_output=True)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # # Pentru a obține output-ul procesului după ce acesta s-a încheiat, poți folosi:
    # stdout, stderr = process.communicate()
    # print("Output:", stdout)
    # print("Error:", stderr if stderr else "Niciun mesaj de eroare.")
    #
    # # Verifică dacă există erori
    # if stderr:
    #     print("Eroare:", process.stderr)
    #     raise Exception("Nu s-a putut deschide emulatorul.")


def _extrage_status_pentru_uuid(output, uuid_cautat):
    # Definim un pattern care caută o linie întreagă care conține UUID-ul specificat
    # Acest pattern extrage de asemenea și statusul de la începutul liniei
    pattern_linie_cu_uuid = r'^\s*(\w+)\s*\|[^|]*\|[^|]*' + re.escape(uuid_cautat)

    # Căutăm pattern-ul în output, folosind re.MULTILINE pentru a trata fiecare linie ca un început nou
    potrivire = re.search(pattern_linie_cu_uuid, output, re.MULTILINE)

    # Dacă găsim o potrivire, returnăm statusul; altfel, returnăm None
    if potrivire:
        return potrivire.group(1)
    else:
        return None


def ensure_boot_is_complete():
    command = shlex.split("adb shell 'while [[ $(getprop sys.boot_completed) -ne 1 ]]; do sleep 1; done;'")
    process = subprocess.run(command, shell=True, text=True, capture_output=True)
    # Verifică dacă există erori
    if process.stderr:
        print("[-] Eroare:", process.stderr)
        raise Exception(
            "Eroare la obtinerea statusului de boot a device-uli"
        )
    # print(process.stdout)


def ensure_emulator_is_online():
    output = _list_devices()
    _id = _extrage_uuid(output)
    status = _extrage_status_pentru_uuid(output, _id)
    if status == "Off":
        print("[+] Emulatorul este inchis, se deschide....")
        _start_device(_id)
        while not _ensure_emulator_starting_window_appears():
            _start_device(_id)
        print("[+] Se asteapta descarcarea emulatorului")
        while True:
            output = _list_devices()
            # _id = _extrage_uuid(output)
            status = _extrage_status_pentru_uuid(output, _id)
            if status == "On":
                while True:
                    if _is_window_open(EMULATOR_PARTIAL_WINDOW_NAME):
                        print("[+] Emulatorul s-a deschis")
                        break
                    time.sleep(TIMP_ASTEPTARE_VERIFICARE_STATUS_EMULATR)
                print(f"[+] Se asteapta completare boot emulator")
                time.sleep(TIMP_ASTEPTARE_INCARCARE_EMULATOR)
                ensure_boot_is_complete()
                break

            time.sleep(TIMP_ASTEPTARE_VERIFICARE_STATUS_EMULATR)
        print("[+] Emulatorul este pregatit pentru utilizare")
    elif status == "On":
        print("[+] Emulatorul este deschis")
    else:
        print(status)
        raise Exception("Statusul emulatorului nu este cunoscut")


def _is_window_open(window_name):
    # Obține o listă cu toate ferestrele deschise
    ferestre = gw.getWindowsWithTitle(window_name)

    # Verifică dacă lista obținută este goală
    if not ferestre:
        return False
    else:
        return True


def _ensure_emulator_starting_window_appears():
    start_time = time.time()
    while True:
        if _is_window_open(EMULATOR_STARTIGN_WINDOW_NAME):
            print("[+] Ferestra de start a emulatorului detectată")
            return True
        time.sleep(TIME_ASTEPTARE_FEREASTRA_START_EMULATOR)

        if time.time() - start_time > TIME_OUT_START_EMULATOR:
            print("[-] Nu s-a detectat fereastra de start a emulatorului")
            return False
