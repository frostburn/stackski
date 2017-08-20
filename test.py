# coding: utf-8

import unittest
from io import StringIO
from functools import reduce

from combinator import *
from stack import *


class TestCombinators(unittest.TestCase):

    def setUp(self):
        self.stack = Stack()

    def push(self, term):
        self.stack.push(term)

    def pop(self):
        return self.stack.pop()

    def apply(self):
        self.stack.apply()

    def reduce(self):
        return self.stack.reduce()

    def load(self, *args):
        for arg in args:
            self.push(arg)

    def test_I(self):
        self.load(K, I)
        assert (self.reduce() is K)

    def test_K(self):
        self.load(S, I, K)
        assert (self.reduce() is I)

    def test_S(self):
        self.load(K, S, K, S)
        assert (self.reduce() is K)

    def test_identity(self):
        x = K(I)  # can be anything
        term = S(K)
        self.load(term, x, K, S)
        assert (self.reduce() is term)

    def test_iota(self):
        i = iota(iota)
        k = iota(iota(i))
        s = iota(k)
        assert (i(iota).eval() is iota)
        assert (k.eval() is K)
        assert (s.eval() is S)

    def test_loop(self):
        self.load(I, I, S)
        self.apply()
        self.apply()
        self.load(I, I, S)
        self.apply()
        self.apply()
        self.apply()
        assert (len(self.stack) == 1)
        with self.assertRaises(RecursionError):
            self.reduce()

    def test_ignores_loop(self):
        self.load(I, I, S)
        self.apply()
        self.apply()
        self.load(I, I, S)
        self.apply()
        self.apply()
        self.apply()
        self.load(I, K)
        assert (self.reduce() is I)

    def test_Y(self):
        self.load(S, K)
        self.apply()
        self.push(Y)
        assert (self.reduce() is S)

    def test_steps(self):
        step = StepCombinator()
        self.load(I, step, Numeral(3))
        self.reduce()
        assert (step.steps == 3)

    def test_print(self):
        stream = StringIO()
        printer = PrintCombinator(stream)
        number = Numeral(65)
        self.load(number, printer)
        self.apply()
        assert (self.stack[-1] is printer)
        self.reduce()
        assert (ord(stream.getvalue()) == 65)

    def test_hello(self):
        stream = StringIO()
        printer = PrintCombinator(stream)
        message = "Hello, World!\n"
        for c in map(Character, reversed(message)):
            self.push(c)

        # Does nothing but makes it lazy
        self.load(K, K, S)
        self.apply()
        self.apply()
        self.apply()

        self.push(printer)
        self.reduce()
        assert (stream.getvalue() == message)

    def test_plus(self):
        step = StepCombinator()
        self.load(I, step, Numeral(3), Numeral(4), plus)
        self.reduce()
        assert (step.steps == 7)

    def test_succ(self):
        step = StepCombinator()
        self.load(I, step, Numeral(5), succ)
        self.reduce()
        assert (step.steps == 6)

    def test_mult(self):
        step = StepCombinator()
        self.load(I, step, Numeral(3), Numeral(4), mult)
        self.reduce()
        assert (step.steps == 12)

    def test_pred(self):
        step = StepCombinator()
        self.load(I, step, Numeral(5), pred)
        self.reduce()
        assert (step.steps == 4)

    def test_iszero(self):
        self.load(Numeral(3), iszero)
        self.apply()
        truth = BooleanEvaluator()
        self.push(truth)
        self.reduce()
        assert (not truth)

        self.load(Numeral(0), iszero)
        self.apply()
        truth = BooleanEvaluator()
        self.push(truth)
        self.reduce()
        assert (truth)

    def test_multi_extract(self):
        n = NumeralExtractor()
        self.load(Numeral(5), Numeral(10), Numeral(15), n)
        self.reduce()
        assert (n == [15, 10, 5])

    def test_branch(self):
        self.load(Numeral(42), Numeral(11), Numeral(5), iszero)
        self.apply()
        self.apply()
        self.apply()
        n = NumeralExtractor()
        self.push(n)
        self.reduce()
        assert (n[0] == 42)

    def test_exp(self):
        self.load(Numeral(3), Numeral(4))
        self.apply()
        n = NumeralExtractor()
        self.push(n)
        self.reduce()
        assert (n[0] == 3**4)

    def test_lazy_extract(self):
        self.load(Numeral(7), K, K, S)
        self.apply()
        self.apply()
        self.apply()
        n = NumeralExtractor()
        self.push(n)
        self.reduce()
        assert (n[0] == 7)


    def test_factorial(self):
        F = LambdaWrapper(lambda f: lambda n: iszero(n)(Numeral(1))(mult(n)(f(pred(n)))))

        for i in range(6):
            step = StepCombinator()
            self.push(I)
            self.push(step)

            self.push(Numeral(i))
            self.push(F)
            self.push(Y)
            self.reduce()
            fact = reduce(lambda a, b: a*b, range(1, i + 1), 1)
            assert (step.steps == fact)


if __name__ == '__main__':
    unittest.main()
