CAPABILITIES = dict(
    platformName='Android',
    automationName='uiautomator2',
    deviceName='Android',
    language='en',
    locale='US'
)
APPIUM_SERVER_URL = 'http://localhost:4723'
PACKAGE_NAME_RENAULT = 'com.renault.myrenault.one.fr'
PACKAGE_NAME_DACIA = 'com.dacia.mydacia.one.fr'
TIMP_ASTEPTARE_IMPLICIT = 3
TIMP_ASTEPTARE_FEEDBACK_TOASTER = 3
TIMP_ASTEPTARE_EROARE_INPUT_VIN = 1
TIMP_ASTEPTARE_COOLDOWN_ACTIUNE = 0.3
TIMP_ASTEPTARE_DESCHIDERE_APLICATIE = 6
TIMP_ASTEPTARE_ACTIVARE_APLICATIE = 1
TIMP_ASTEPTARE_DISPARITIE_TOASTER = 7

ERORI = [
    'An error has occurred',
    "The operation couldn't be completed",
    "Invalid VIN",
    "VIN format is incorrect",
    'Network error',
    'this vin was already added',
    'Vehicle already added',
]

FWUID_PATH = 'fwuid.json'
LOCK_PATH = FWUID_PATH + '.lock'
