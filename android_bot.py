import time

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from lib.constants import APPIUM_SERVER_URL, TIMP_ASTEPTARE_IMPLICIT, CAPABILITIES, TIMP_ASTEPTARE_FEEDBACK_TOASTER, \
    TIMP_ASTEPTARE_EROARE_INPUT_VIN, TIMP_ASTEPTARE_COOLDOWN_ACTIUNE, TIMP_ASTEPTARE_DISPARITIE_TOASTER, \
    PACKAGE_NAME_DACIA, PACKAGE_NAME_RENAULT, TIMP_ASTEPTARE_DESCHIDERE_APLICATIE, TIMP_ASTEPTARE_ACTIVARE_APLICATIE
from lib.utils import cauta_mesaj_eroare, verifica_aplicatie_deschisa, ensure_emulator_is_online


class AndroidBot:
    def __init__(self):
        self.aplicatii = {
            'renault': PACKAGE_NAME_RENAULT,
            'dacia': PACKAGE_NAME_DACIA
        }
        ensure_emulator_is_online()
        print('[+] Inițializare driver...')
        self._driver = webdriver.Remote(APPIUM_SERVER_URL,
                                        options=UiAutomator2Options().load_capabilities(CAPABILITIES))
        self._driver.implicitly_wait(TIMP_ASTEPTARE_IMPLICIT)

    def __del__(self):
        print('[+] Închidere driver...')
        self._driver.quit()

    def get_radio_code(self, marca, vin):
        # Verifica daca marca exista
        if marca not in self.aplicatii.keys():
            print(f'[-] Marca {marca} nu există')
            raise Exception(f'Marca {marca} nu există')


        self._asigura_activarea_aplicatiei(marca=marca)

        print(f'[+] Obținere cod radio pentru {marca.capitalize()} VIN: {vin}...')
        self._asigura_vehicule_sterse(marca=marca)
        self._introdu_vin(marca=marca, vin=vin)
        self._verifica_disparitia_toasterului(marca=marca)
        self._submit_vin(marca=marca)
        if eroare := self._verifica_eroare(marca=marca):
            print(f'[-] Eroare: {eroare} pentru vin {vin}')
            raise Exception(eroare)
        self._confirma_adaugarea_masinii(marca=marca)
        code = self._get_radio_code(marca=marca)
        print(f'[+] Codul radio pentru {vin} este {code}')
        self._driver.back()
        self._delete_vehicle(marca=marca)
        return code

    def _asigura_activarea_aplicatiei(self, marca):
        aplicatie_curenta = self._driver.current_package
        if aplicatie_curenta != self.aplicatii[marca]:
            print(f'[-] Aplicatia {marca.capitalize()} nu este in focus')
            r = verifica_aplicatie_deschisa(package_name=self.aplicatii[marca])
            if r == 'deschide':
                print(f'[+] Deschidere aplicație {marca.capitalize()}...')
                self._driver.activate_app(self.aplicatii[marca])
                time.sleep(TIMP_ASTEPTARE_DESCHIDERE_APLICATIE)
            elif r == 'activeaza':
                print(f'[+] Activare aplicație {marca.capitalize()}...')
                self._driver.activate_app(self.aplicatii[marca])
                time.sleep(TIMP_ASTEPTARE_ACTIVARE_APLICATIE)

        else:
            print(f'[+] Aplicatia {marca.capitalize()} este in focus')

    def _asigura_vehicule_sterse(self, marca):
        while True:
            try:
                self._delete_vehicle(marca=marca)
            except NoSuchElementException:
                break

    def _swipe_pentru_stergere_vehicul(self):
        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(self._driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(554, 1754)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(558, 1078)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def _swipe_pentru_activare_buton_confirm(self):
        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(self._driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(900, 981)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(216, 943)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(self._driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(892, 981)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(123, 955)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def _swipe_pentru_vizualizare_radio_code(self):
        actions = ActionChains(self._driver)
        actions.w3c_actions = ActionBuilder(self._driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(529, 1547)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.move_to_location(532, 1099)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def _introdu_vin(self, marca, vin):
        vin_input = self._driver.find_element(by=AppiumBy.ID, value=f'{self.aplicatii[marca]}:id/edt_add_car')
        vin_input.send_keys(vin)

    def _submit_vin(self, marca):
        submit_button = self._driver.find_element(by=AppiumBy.ID,
                                                  value=f'{self.aplicatii[marca]}:id/add_car_button_validate')
        submit_button.click()

    def _get_mesaj_eroare_from_field(self, marca):
        try:
            mesaj_eroare = WebDriverWait(self._driver, TIMP_ASTEPTARE_EROARE_INPUT_VIN).until(
                EC.visibility_of_element_located((AppiumBy.ID, f'{self.aplicatii[marca]}:id/textinput_error')))
            return mesaj_eroare.text
        except TimeoutException:
            return None

    def _verifica_eroare(self, marca):
        if mesaj_field := self._get_mesaj_eroare_from_field(marca=marca):
            return mesaj_field

        mesaj = self._get_mesaj_informare(marca=marca)
        if mesaj:
            if eroare := cauta_mesaj_eroare(mesaj):
                return eroare
            return False
        else:
            return False

    def _get_mesaj_informare(self, marca):
        try:
            mesaj_informare = WebDriverWait(self._driver, TIMP_ASTEPTARE_FEEDBACK_TOASTER).until(
                EC.visibility_of_element_located((AppiumBy.ID, f'{self.aplicatii[marca]}:id/custom_snackbar_text')))
            return mesaj_informare.text
        except TimeoutException:
            return None

    def _confirma_adaugarea_masinii(self, marca):
        try:
            confirm_button = self._driver.find_element(by=AppiumBy.ID,
                                                       value=f'{self.aplicatii[marca]}:id/btn_continue')
            if confirm_button.get_attribute('enabled') == 'true':
                confirm_button.click()
            else:
                self._swipe_pentru_activare_buton_confirm()
                confirm_button.click()
        except NoSuchElementException:
            pass

    def _get_radio_code(self, marca):
        self._open_vehicle_info(marca=marca)
        self._swipe_pentru_vizualizare_radio_code()
        time.sleep(TIMP_ASTEPTARE_COOLDOWN_ACTIUNE)
        try:
            self._show_code(marca=marca)
        except NoSuchElementException:
            pass

        try:
            code = self._get_code(marca=marca)
            return code
        except NoSuchElementException:
            self._driver.back()
            self._delete_vehicle(marca=marca)
            raise Exception('[-] Code not found')

    def _open_vehicle_info(self, marca):
        vehicle_info = self._driver.find_element(by=AppiumBy.ID, value=f'{self.aplicatii[marca]}:id/charButton')
        vehicle_info.click()

    def _show_code(self, marca):
        show_code_button = self._driver.find_element(by=AppiumBy.ID,
                                                     value=f'{self.aplicatii[marca]}:id/radio_code_text')
        show_code_button.click()

    def _get_code(self, marca):
        code = self._driver.find_element(by=AppiumBy.ID, value=f'{self.aplicatii[marca]}:id/radio_code_value')
        # print(f'code.text)
        return code.text

    def _delete_vehicle(self, marca):
        self._swipe_pentru_stergere_vehicul()
        time.sleep(TIMP_ASTEPTARE_COOLDOWN_ACTIUNE)
        self._verifica_disparitia_toasterului(marca=marca)
        delete_button = self._driver.find_element(by=AppiumBy.ID,
                                                  value=f'{self.aplicatii[marca]}:id/tv_action_remove_vehicle')
        delete_button.click()
        time.sleep(TIMP_ASTEPTARE_COOLDOWN_ACTIUNE)

        confirm_delete_button = self._driver.find_element(by=AppiumBy.ID,
                                                          value=f'{self.aplicatii[marca]}:id/yes_btn')
        confirm_delete_button.click()
        # TODO: de implementat eroarea falsa la stergere
        if mesaj := self._get_mesaj_informare(marca=marca):
            if 'Your vehicle has been deleted'.lower() in mesaj.lower():
                pass
                # return True
            else:
                self._verifica_disparitia_toasterului(marca=marca)
                self._cancel_delete(marca=marca)
                self._adaugare_vehicul(marca=marca)
                # return False

    def _verifica_disparitia_toasterului(self, marca):
        try:
            WebDriverWait(self._driver, TIMP_ASTEPTARE_DISPARITIE_TOASTER).until(
                EC.invisibility_of_element_located(
                    (AppiumBy.ID, f'{self.aplicatii[marca]}:id/custom_snackbar_text')))
            return True
        except TimeoutException:
            return False

    def _cancel_delete(self, marca):
        cancel_button = self._driver.find_element(by=AppiumBy.ID,
                                                  value=f'{self.aplicatii[marca]}:id/no_tv')
        cancel_button.click()

    def _adaugare_vehicul(self, marca):
        add_vehicle_button = self._driver.find_element(by=AppiumBy.ID,
                                                       value=f'{self.aplicatii[marca]}:id/btn_action')
        add_vehicle_button.click()
