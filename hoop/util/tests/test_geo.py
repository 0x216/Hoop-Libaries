from unittest import TestCase

from ..geo import get_postcode_district


class TestPostcodeDistrict(TestCase):
    def assertDistrict(self, postcode, expected):
        self.assertEqual(get_postcode_district(postcode), expected)

    def test_five_chars(self):
        self.assertDistrict('N7 7EL', 'N7')

    def test_six_chars(self):
        self.assertDistrict('RH2 8AL', 'RH2')

    def test_seven_chars(self):
        self.assertDistrict('RH12 1AE', 'RH12')

    def test_whitespace_removal(self):
        self.assertDistrict(' EC1R  4RB     ', 'EC1R')
        self.assertDistrict('EC1R\xa04RB', 'EC1R')
        self.assertDistrict('EC1R\u20004RB', 'EC1R')
