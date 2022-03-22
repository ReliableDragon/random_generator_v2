import unittest
import logging

logging.basicConfig(format='> %(filename)s:%(lineno)d %(message)s', level=logging.INFO)

from choice_parser import ChoiceParser
from equation_parser import EquationParser
from subchoice_counter import SubchoiceCounter

class EquationParserTest(unittest.TestCase):

    def setUp(self):
        choice_parser = ChoiceParser('test', 0)
        self.equation_parser = EquationParser(choice_parser.parse_single_fragment, SubchoiceCounter(), 'test', 0)

    def test_numeric_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4*2+5')), 'Equation[lhs: Equation[lhs: 4, op=*, rhs=2], op=+, rhs=5]')

    def test_numeric_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4+2*5')), 'Equation[lhs: 4, op=+, rhs=Equation[lhs: 2, op=*, rhs=5]]')

    def test_numeric_equation3(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('(4+2)*5')), 'Equation[lhs: Equation[lhs: 4, op=+, rhs=2], op=*, rhs=5]')

    def test_numeric_equation4(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4+5*6**2//3-4')), 'Equation[lhs: Equation[lhs: 4, op=+, rhs=Equation[lhs: Equation[lhs: 5, op=*, rhs=Equation[lhs: 6, op=**, rhs=2]], op=//, rhs=3]], op=-, rhs=4]')

    def test_numeric_equation5(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('4+2*-5')), 'Equation[lhs: 4, op=+, rhs=Equation[lhs: 2, op=*, rhs=-5]]')

    def test_string_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+"cde"')), 'Equation[lhs: abc, op=+, rhs=cde]')

    def test_string_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+"cde"+"fgh"')), 'Equation[lhs: Equation[lhs: abc, op=+, rhs=cde], op=+, rhs=fgh]')

    def test_var_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('#abc+"fgh"')), 'Equation[lhs: ChoiceFragment[value: "abc", type: VARIABLE, order: NONE], op=+, rhs=fgh]')

    def test_func_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('#gauss(1,2)++"fgh"')), 'Equation[lhs: ChoiceFragment[value: "Function[name: gauss, args: [ChoiceFragment[value: "1", type: TEXT, order: NONE], ChoiceFragment[value: "2", type: TEXT, order: NONE]]]", type: FUNCTION, order: NONE], op=++, rhs=fgh]')

    def test_reordering_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('#[2]gauss(1,2)++"fgh"')), 'Equation[lhs: ChoiceFragment[value: "Function[name: gauss, args: [ChoiceFragment[value: "1", type: TEXT, order: NONE], ChoiceFragment[value: "2", type: TEXT, order: NONE]]]", type: FUNCTION, order: 2], op=++, rhs=fgh]')

    def test_reordering_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('$[2]++"fgh"')), 'Equation[lhs: ChoiceFragment[value: "0", type: SUBCHOICE, order: 2], op=++, rhs=fgh]')

    def test_mixed_equation(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+"cde"*3')), 'Equation[lhs: abc, op=+, rhs=Equation[lhs: cde, op=*, rhs=3]]')

    def test_mixed_equation2(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+#cde*3')), 'Equation[lhs: abc, op=+, rhs=Equation[lhs: ChoiceFragment[value: "cde", type: VARIABLE, order: NONE], op=*, rhs=3]]')

    def test_mixed_equation3(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+#cde*3==5')), 'Equation[lhs: Equation[lhs: abc, op=+, rhs=Equation[lhs: ChoiceFragment[value: "cde", type: VARIABLE, order: NONE], op=*, rhs=3]], op===, rhs=5]')

    def test_mixed_equation4(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+#gauss(1, 2)*3==5')), 'Equation[lhs: Equation[lhs: abc, op=+, rhs=Equation[lhs: ChoiceFragment[value: "Function[name: gauss, args: [ChoiceFragment[value: "1", type: TEXT, order: NONE], ChoiceFragment[value: "2", type: TEXT, order: NONE]]]", type: FUNCTION, order: NONE], op=*, rhs=3]], op===, rhs=5]')

    def test_mixed_equation5(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+$(5)*3==5')), 'Equation[lhs: Equation[lhs: abc, op=+, rhs=Equation[lhs: ChoiceFragment[value: "Function[name: $, args: [ChoiceFragment[value: "5", type: TEXT, order: NONE]]]", type: FUNCTION, order: NONE], op=*, rhs=3]], op===, rhs=5]')

    def test_mixed_equation6(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+$(#gauss(1,2))*3==5')), 'Equation[lhs: Equation[lhs: abc, op=+, rhs=Equation[lhs: ChoiceFragment[value: "Function[name: $, args: [ChoiceFragment[value: "Function[name: gauss, args: [ChoiceFragment[value: "1", type: TEXT, order: NONE], ChoiceFragment[value: "2", type: TEXT, order: NONE]]]", type: FUNCTION, order: NONE]]]", type: FUNCTION, order: NONE], op=*, rhs=3]], op===, rhs=5]')

    def test_mixed_equation7(self):
        tested = self.equation_parser
        self.assertEqual(str(tested.parse_equation('"abc"+#gauss($(2), 3)*3==5')), 'Equation[lhs: Equation[lhs: abc, op=+, rhs=Equation[lhs: ChoiceFragment[value: "Function[name: gauss, args: [ChoiceFragment[value: "Function[name: $, args: [ChoiceFragment[value: "2", type: TEXT, order: NONE]]]", type: FUNCTION, order: NONE], ChoiceFragment[value: "3", type: TEXT, order: NONE]]]", type: FUNCTION, order: NONE], op=*, rhs=3]], op===, rhs=5]')


if __name__ == '__main__':
    unittest.main()
