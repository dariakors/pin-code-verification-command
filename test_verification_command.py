import unittest

from card import Card
from parameterized import parameterized

from constants import VERIFICATION_OK, INCORRECT_P1_OR_P2, NO_INFORMATION_GIVEN, INCORRECT_DATA_FIELD, \
    AUTH_METHOD_BLOCKED, INCONSISTENT_LC
from utils import build_header, get_lc


class Tests(unittest.TestCase):

    @parameterized.expand([
        ['00', '01', 'EF08', VERIFICATION_OK],  # valid global pincode
        ['00', '02', 'EF10', VERIFICATION_OK],  # valid specific pincode
    ])
    def test_valid_pin_verification(self, p1: str, p2: str, pin: str, result: str):
        card = Card()
        response = card.send(build_header(p1=p1, p2=p2) + get_lc(pin) + pin)
        self.assertEqual(response, result)

    def test_empty_pin_verification(self):
        card = Card()
        response = card.send(build_header(p1='00', p2='01'))
        self.assertEqual(response, NO_INFORMATION_GIVEN)

    def test_empty_pin_verification_after_failed_attempts(self):
        card = Card()

        for i in range(card.get_max_retries()):
            card.send(build_header(p1='00', p2='01'))

        response = card.send(build_header(p1='00', p2='01'))
        self.assertEqual(response, AUTH_METHOD_BLOCKED)

    def test_not_empty_length_parameter_for_empty_pin(self):
        card = Card()
        response = card.send(build_header(p1='00', p2='01') + '0B')
        self.assertEqual(response, INCONSISTENT_LC)

    def test_empty_length_parameter_for_pin(self):
        card = Card()
        response = card.send(build_header(p1='00', p2='01') + 'EF08')
        self.assertEqual(response, INCONSISTENT_LC)

    def test_incorrect_length_parameter_for_pin(self):
        card = Card()
        response = card.send(build_header(p1='00', p2='01') + '0B' + 'EF08')
        self.assertEqual(response, INCONSISTENT_LC)

    def test_get_info_after_successfull_attempt(self):
        card = Card()

        # successfull attempt
        pin = 'EF08'
        response = card.send(build_header(p1='00', p2='01') + get_lc(pin) + pin)  # successfull verification
        self.assertEqual(response, VERIFICATION_OK)

        # check info
        response = card.send(build_header(p1='00', p2='00'))
        self.assertEqual(response, VERIFICATION_OK)

    def test_get_info_before_all_attempts(self):
        card = Card()
        max_retries = card.get_max_retries()
        response = card.send(build_header(p1='00', p2='00'))
        self.assertEqual(response, '63C' + str(max_retries))

    def test_get_info_about_retries_after_every_failed_attempt(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            pin = 'EF08'  # wrong pin
            card.send(build_header(p1='00', p2='01') + get_lc(pin) + pin)  # failed verification

            expected_response = '63C' + (max_retries - 1 - i)
            response = card.send(build_header(p1='00', p2='00'))  # getting info about retries
            self.assertEqual(response, expected_response)

    def test_get_info_about_retries_after_all_failed_attempts(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            pin = 'EF08'  # wrong pin
            card.send(build_header(p1='00', p2='01') + get_lc(pin) + pin)  # failed verification

        response = card.send(build_header(p1='00', p2='00'))  # getting info about retries
        self.assertEqual(response, '63C0')

    def test_get_info_about_retries_after_all_failed_attempts_with_empty_pin(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            card.send(build_header(p1='00', p2='01'))  # failed verification

        response = card.send(build_header(p1='00', p2='00'))  # getting info about retries
        self.assertEqual(response, '63C0')

    def test_every_failed_attempt_till_the_end_of_max_retries(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            pin = 'EF08'  # wrong pin
            response = card.send(build_header(p1='00', p2='01') + get_lc(pin) + pin)  # failed verification
            expected_response = '63C' + (max_retries - 1 - i)
            self.assertEqual(response, expected_response)

    def test_check_response_after_all_failed_attempt(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            pin = 'EF08'  # wrong pin
            card.send(build_header(p1='00', p2='01') + get_lc(pin) + pin)  # failed verification

        pin = 'EF08'  # wrong pin
        response = card.send(build_header(p1='00', p2='01') + get_lc(pin) + pin)
        self.assertEqual(response, AUTH_METHOD_BLOCKED)  # no more attempts, card is blocked

    @parameterized.expand([
        ['00', '01', 'EF08', '03', INCORRECT_P1_OR_P2],  # valid global pincode
        ['00', '02', 'EF10', '03', INCORRECT_P1_OR_P2],  # valid specific pincode
    ])
    def test_not_empty_le_field(self, p1: str, p2: str, pin: str, le: str, result: str):
        card = Card()
        response = card.send(build_header(p1=p1, p2=p2) + get_lc(pin) + pin + le)
        self.assertEqual(response, result)

    def test_p1_or_p2_is_missed(self):
        card = Card()
        response = card.send(build_header(p1='00'))
        self.assertEqual(response, INCORRECT_P1_OR_P2)

    def test_empty_p_parameters(self):
        card = Card()
        response = card.send(build_header())
        self.assertEqual(response, INCORRECT_P1_OR_P2)

    @parameterized.expand([
        ['00', '00', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P2 parameter, because data will be sent
        ['01', '01', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P1 parameter, because P1='01' is RFU
        ['ewrwer', '01', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P1 parameter
        ['', '01', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P1 parameter
        ['   ', '01', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P1 parameter
        ['%^', '01', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P1 parameter
        ['00', '900', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P2 parameter
        ['00', 'ewrwer', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P2 parameter
        ['00', '', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P2 parameter
        ['00', '   ', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P2 parameter
        ['00', '%^', 'EF08', INCORRECT_P1_OR_P2],  # incorrect P2 parameter
    ])
    def test_incorrect_parameters_p1_and_p2(self, p1: str, p2: str, pin: str, result: str):
        card = Card()
        response = card.send(build_header(p1=p1, p2=p2) + get_lc(pin) + pin)
        self.assertEqual(response, result)

    @parameterized.expand([
        ['00', '01', '85fa3cad94330c5c8a42a73b20498fc6a40855b7c8bebb987879087ecc51829714490eb2d5f0d'
                     '1879af0e9b7ae46b750fb88aeec4433f6d293c6655e5a48d628a787e760d9987a5c6d85139a477'
                     'ca770ad72e0aa26e91cc2d5a3362d38378cdd231327bfe9bb149da6ee92da8ac9862aacb404068b03'
                     '9661c8e9bf6324893cc949815b8f784f8927d48e2b896218915ae4f7a221b95aa60f568c5b88ee9a7'
                     '93207580dfd3f296a9ace2af29b588ec6a1d2c1a42637ca4d21f03757e25453e75c362b0ed1705310a6'
                     '48ffce216ea19b46d1f159119da4f194077b80aa37e63ed76b1b04ca4a1f2a98dca8261cbbf2e6c4f13'
                     '24204578c9445976a1148c78d336e', INCORRECT_DATA_FIELD],  # length of data is more than 255
    ])
    def test_too_long_pin(self, p1: str, p2: str, pin: str, result: str):
        card = Card()
        response = card.send(build_header(p1=p1, p2=p2) + get_lc(pin) + pin)
        self.assertEqual(response, result)

    @parameterized.expand([
        ['00', '01', '', NO_INFORMATION_GIVEN],  # empty string
        ['00', '01', 'JJJJJlklklk', INCORRECT_DATA_FIELD],  # letters
        ['00', '01', '       ', INCORRECT_DATA_FIELD],  # spaces
        ['00', '01', '%^', INCORRECT_DATA_FIELD],  # special symbols
    ])
    def test_incorrect_values_of_pin(self, p1: str, p2: str, pin: str, result: str):
        card = Card()
        lc = "{:02X}".format(len(pin.encode()))
        response = card.send(build_header(p1=p1, p2=p2) + lc + pin)
        self.assertEqual(response, result)


if __name__ == '__main__':
    unittest.main()
