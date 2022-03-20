import unittest
import logging

logging.basicConfig(format='> %(filename)s:%(lineno)d %(message)s', level=logging.INFO)

from equation_parser import EquationParser

class EquationParserTest(unittest.TestCase):

    def setUp(self):
        self.equation_parser = EquationParser('test', 0)

    def test_numeric_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4*2+5')), '((4*2)+5)')

    def test_numeric_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4+2*5')), '(4+(2*5))')

    def test_numeric_equation3(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('(4+2)*5')), '((4+2)*5)')

    def test_numeric_equation4(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4+5*6**2//3-4')), '((4+((5*(6**2))//3))-4)')

    def test_numeric_equation5(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4+2*-5')), '(4+(2*-5))')

    def test_string_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('abc+cde')), '(abc+cde)')

    def test_string_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('abc+cde+fgh')), '((abc+cde)+fgh)')

    def test_mixed_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('abc+cde*3')), '(abc+(cde*3))')

    def test_mixed_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('abc+#cde*3')), '(abc+(#cde*3))')

    def test_mixed_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('abc+#cde*3==5')), '((abc+(#cde*3))==5)')


if __name__ == '__main__':
    unittest.main()
