import unittest

from card import Card
from parameterized import parameterized


CLA = '20'
INS = 'A4'


class Tests(unittest.TestCase):

    @parameterized.expand([
        ['00', '01', 'EF08', '9000'],  # valid global pincode
        ['00', '02', 'EF10', '9000'],  # valid specific pincode
    ])
    def test_valid_pin_verification(self, p1, p2, pin, result):
        card = Card()
        header = CLA + INS + p1 + p2
        lc = "{:02X}".format(len(bytes.fromhex(pin)))
        response = card.send(header + lc + pin)
        self.assertEqual(response, result)

    def test_empty_pin_verification(self):
        card = Card()
        header = CLA + INS + '00' + '01'
        response = card.send(header)
        self.assertEqual(response, '6300')

    def test_empty_pin_verification_after_failed_attempts(self):
        card = Card()
        header = CLA + INS + '00' + '01'

        for i in range(card.get_max_retries()):
            card.send(header)

        response = card.send(header)
        self.assertEqual(response, '6983')

    @parameterized.expand([
        ['00', '00', 'EF08', '6986'],  # incorrect P2 parameter, because data will be sent
        ['01', '01', 'EF08', '6986'],  # incorrect P1 parameter, because P1='01' is RFU
        ['ewrwer', '01', 'EF08', '6986'],  # incorrect P1 parameter
        ['', '01', 'EF08', '6986'],  # incorrect P1 parameter
        ['   ', '01', 'EF08', '6986'],  # incorrect P1 parameter
        ['%^', '01', 'EF08', '6986'],  # incorrect P1 parameter
        ['00', '900', 'EF08', '6986'],  # incorrect P2 parameter
        ['00', 'ewrwer', 'EF08', '6986'],  # incorrect P2 parameter
        ['00', '', 'EF08', '6986'],  # incorrect P2 parameter
        ['00', '   ', 'EF08', '6986'],  # incorrect P2 parameter
        ['00', '%^', 'EF08', '6986'],  # incorrect P2 parameter
    ])
    def test_incorrect_parameters_p1_and_p2(self, p1, p2, pin, result):
        card = Card()
        header = CLA + INS + p1 + p2
        lc = "{:02X}".format(len(bytes.fromhex(pin)))
        response = card.send(header + lc + pin)
        self.assertEqual(response, result)

    def test_not_empty_length_parameter_for_empty_pin(self):
        card = Card()
        header = CLA + INS + '00' + '01'
        response = card.send(header + '0B')
        self.assertEqual(response, '6A87')

    def test_empty_length_parameter_for_pin(self):
        card = Card()
        header = CLA + INS + '00' + '01'
        response = card.send(header + 'EF08')
        self.assertEqual(response, '6A87')

    def test_incorrect_length_parameter_for_pin(self,):
        card = Card()
        header = CLA + INS + '00' + '01'
        response = card.send(header + '0B' + 'EF08')
        self.assertEqual(response, '6A87')

    def test_get_info_after_successfull_attempt(self):
        card = Card()

        # successfull attempt
        header = CLA + INS + '00' + '01'
        pin = 'EF08'
        lc = "{:02X}".format(len(bytes.fromhex(pin)))
        response = card.send(header + lc + pin)  # successfull verification
        self.assertEqual(response, '9000')

        # check info
        header = CLA + INS + '00' + '00'
        response = card.send(header)
        self.assertEqual(response, '9000')

    def test_get_info_before_all_attempts(self):
        card = Card()
        max_retries = card.get_max_retries()
        header = CLA + INS + '00' + '00'
        response = card.send(header)
        self.assertEqual(response, '63C' + str(max_retries))

    def test_get_info_about_retries_after_every_failed_attempt(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            header = CLA + INS + '00' + '01'
            pin = 'EF08'  # wrong pin
            lc = "{:02X}".format(len(bytes.fromhex(pin)))
            card.send(header + lc + pin)  # failed verification

            expected_response = '63C' + (max_retries - 1 - i)
            header = CLA + INS + '00' + '00'
            response = card.send(header)  # getting info about retries
            self.assertEqual(response, expected_response)

    def test_get_info_about_retries_after_all_failed_attempts(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            header = CLA + INS + '00' + '01'
            pin = 'EF08'  # wrong pin
            lc = "{:02X}".format(len(bytes.fromhex(pin)))
            card.send(header + lc + pin)  # failed verification

        header = CLA + INS + '00' + '00'
        response = card.send(header)  # getting info about retries
        self.assertEqual(response, '63C0')

    def test_get_info_about_retries_after_all_failed_attempts_with_empty_pin(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            header = CLA + INS + '00' + '01'
            card.send(header)  # failed verification

        header = CLA + INS + '00' + '00'
        response = card.send(header)  # getting info about retries
        self.assertEqual(response, '63C0')

    def test_every_failed_attempt_till_the_end_of_max_retries(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            header = CLA + INS + '00' + '01'
            pin = 'EF08'  # wrong pin
            lc = "{:02X}".format(len(bytes.fromhex(pin)))

            response = card.send(header + lc + pin)  # failed verification
            expected_response = '63C' + (max_retries - 1 - i)
            self.assertEqual(response, expected_response)

    def test_check_response_after_all_failed_attempt(self):
        card = Card()
        max_retries = card.get_max_retries()

        for i in range(max_retries):
            header = CLA + INS + '00' + '01'
            pin = 'EF08'  # wrong pin
            lc = "{:02X}".format(len(bytes.fromhex(pin)))
            card.send(header + lc + pin)  # failed verification

        header = CLA + INS + '00' + '01'
        pin = 'EF08'  # wrong pin
        lc = "{:02X}".format(len(bytes.fromhex(pin)))
        response = card.send(header + lc + pin)
        self.assertEqual(response, '6983')  # no more attempts, card is blocked

    @parameterized.expand([
        ['00', '01', 'EF08', '03', '6986'],  # valid global pincode
        ['00', '02', 'EF10', '03', '6986'],  # valid specific pincode
    ])
    def test_not_empty_le_field(self, p1, p2, pin, le, result):
        card = Card()
        header = CLA + INS + p1 + p2
        lc = "{:02X}".format(len(bytes.fromhex(pin)))
        response = card.send(header + lc + pin + le)
        self.assertEqual(response, result)

    def test_p1_or_p2_is_missed(self):
        card = Card()
        header = CLA + INS + '00'
        response = card.send(header)
        self.assertEqual(response, '6986')

    def test_empty_p_parameters(self):
        card = Card()
        header = CLA + INS
        response = card.send(header)
        self.assertEqual(response, '6986')

    @parameterized.expand([
        ['00', '01', '85fa3cad94330c5c8a42a73b20498fc6a40855b7c8bebb987879087ecc51829714490eb2d5f0d'
                     '1879af0e9b7ae46b750fb88aeec4433f6d293c6655e5a48d628a787e760d9987a5c6d85139a477'
                     'ca770ad72e0aa26e91cc2d5a3362d38378cdd231327bfe9bb149da6ee92da8ac9862aacb404068b03'
                     '9661c8e9bf6324893cc949815b8f784f8927d48e2b896218915ae4f7a221b95aa60f568c5b88ee9a7'
                     '93207580dfd3f296a9ace2af29b588ec6a1d2c1a42637ca4d21f03757e25453e75c362b0ed1705310a6'
                     '48ffce216ea19b46d1f159119da4f194077b80aa37e63ed76b1b04ca4a1f2a98dca8261cbbf2e6c4f13'
                     '24204578c9445976a1148c78d336e', '6A80'],  # length of data is more than 255
    ])
    def test_too_long_pin(self, p1, p2, pin, result):
        card = Card()
        header = CLA + INS + p1 + p2
        lc = "{:02X}".format(len(bytes.fromhex(pin)))
        response = card.send(header + lc + pin)
        self.assertEqual(response, result)

    @parameterized.expand([
        ['00', '01', '', '6300'],  # empty string
        ['00', '01', 'JJJJJlklklk', '6A80'],  # letters
        ['00', '01', '       ', '6A80'],  # spaces
        ['00', '01', '%^', '6A80'],  # special symbols
    ])
    def test_incorrect_values_of_pin(self, p1, p2, pin, result):
        card = Card()
        header = CLA + INS + p1 + p2
        lc = "{:02X}".format(len(pin.encode()))
        response = card.send(header + lc + pin)
        self.assertEqual(response, result)


if __name__ == '__main__':
    unittest.main()
