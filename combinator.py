# coding: utf-8
import sys


__all__ = [
    "S", "K", "I", "iota", "Y",
    "StepCombinator", "Numeral", "PrintCombinator", "Character", "prnt", "NumeralExtractor", "pred", "plus", "succ", "mult",
    "true", "false", "iszero", "BooleanEvaluator", "LambdaWrapper"
]


class Combinator(object):
    def is_lazy(self):
        return False

    def eval(self):
        return self


class LazyCombinator(Combinator):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def is_lazy(self):
        return True

    def eval(self):
        first = self.first.eval()
        result = first(self.second)
        result = result.eval()
        if not result.is_lazy():
            return result
        second = self.second.eval()
        return first(second).eval()

    def __call__(self, term):
        return LazyCombinator(self, term)

    def __repr__(self):
        return "(lazy:{!r}.{!r})".format(self.first, self.second)


class LambdaWrapper(Combinator):
    def __init__(self, function):
        self.function = function

    def __call__(self, term):
        result = self.function(term)
        if not isinstance(result, Combinator):
            return LambdaWrapper(result)
        return result

    def __repr__(self):
        return "(lambda)"


class ICombinator(Combinator):
    def __call__(self, term):
        return term

    def __repr__(self):
        return "I"


class ConstantCombinator(Combinator):
    def __init__(self, term):
        self.term = term

    def is_lazy(self):
        return self.term.is_lazy()

    def __call__(self, _):
        return self.term

    def __repr__(self):
        return "(K.{!r})".format(self.term)


class KCombinator(Combinator):
    def __call__(self, term):
        return ConstantCombinator(term)

    def __repr__(self):
        return "K"


class S2Combinator(Combinator):
    def __init__(self, first, second):
        self.first = first
        self.second = second

    def is_lazy(self):
        return self.first.is_lazy() or self.second.is_lazy()

    def __call__(self, third):
        function = LazyCombinator(self.first, third)
        argument = LazyCombinator(self.second, third)
        return function(argument)

    def __repr__(self):
        return "(S.{!r}.{!r})".format(self.first, self.second)


class S1Combinator(Combinator):
    def __init__(self, term):
        self.term = term

    def is_lazy(self):
        return self.term.is_lazy()

    def __call__(self, term):
        return S2Combinator(self.term, term)

    def __repr__(self):
        return "(S.{!r})".format(self.term)


class SCombinator(Combinator):
    def __call__(self, term):
        return S1Combinator(term)

    def __repr__(self):
        return "S"

S = SCombinator()
K = KCombinator()
I = ICombinator()


class IotaCombinator(Combinator):
    def __call__(self, term):
        return term(S)(K)

    def __repr__(self):
        return "iota"


class InnerYCombinator(Combinator):
    def __init__(self, term):
        self.term = term

    def is_lazy(self):
        return self.term.is_lazy()

    def __call__(self, term):
        return self.term(LazyCombinator(term, term))

    def __repr__(self):
        return "(λx{!r}.xx)".format(self.term)

class YCombinator(Combinator):
    def __call__(self, term):
        return InnerYCombinator(term)(InnerYCombinator(term))

    def __repr__(self):
        return "Y"

    @classmethod
    def as_elementary(cls):
        a = K(S(I)(I))
        b = S(K(S))(K)
        c = S(b)(a)
        return S(a)(c)


iota = IotaCombinator()
Y = YCombinator()


class StepCombinator(Combinator):
    def __init__(self, callback=None):
        self.steps = 0
        self.callback = callback

    def __call__(self, term):
        if self.callback is not None:
            self.callback(self.steps)
        self.steps += 1
        return term

    def __repr__(self):
        return "step:{}".format(self.steps)


class DeferredCombinator(Combinator):
    def __init__(self):
        self.deferred = []

    def is_lazy(self):
        return True

    def eval(self):
        for term, step in self.deferred:
            term.eval()
            self.accumulate(step.steps)
        return I

    def __call__(self, term):
        step = StepCombinator()
        self.deferred.append((term(step)(I), step))
        return self


class PrintCombinator(DeferredCombinator):
    def __init__(self, stream):
        super(PrintCombinator, self).__init__()
        self.stream = stream

    def accumulate(self, steps):
        self.stream.write(chr(steps))

    def __repr__(self):
        return "prnt"


class NumeralExtractor(DeferredCombinator, list):
    def accumulate(self, steps):
        self.append(steps)


prnt = PrintCombinator(sys.stdout)


class RepeatCombinator(Combinator):
    def __init__(self, term, n):
        self.term = term
        self.n = n

    def is_lazy(self):
        return self.term.is_lazy()

    def __call__(self, term):
        for i in range(self.n):
            term = self.term(term)
        return term

    def __repr__(self):
        return "(Numeral({!r}).{!r})".format(self.n, self.term)


class Numeral(Combinator):
    def __init__(self, n):
        self.n = n

    def __call__(self, term):
        return RepeatCombinator(term, self.n)

    def __repr__(self):
        return "Numeral({!r})".format(self.n)


class Character(Numeral):
    def __init__(self, character):
        super(Character, self).__init__(ord(character))

    def __repr__(self):
        return "Character({!r})".format(chr(self.n))


class PlusCombinator(Combinator):
    def __call__(self, term):
        return LambdaWrapper(lambda n: lambda f: lambda x: term(f)(n(f)(x)))

    def __repr__(self):
        return "plus"


class SuccessorCombinator(Combinator):
    def __call__(self, term):
        return LambdaWrapper(lambda f: lambda x: f(term(f)(x)))

    def __repr__(self):
        return "succ"


class MultiplyCombinator(Combinator):
    def __call__(self, term):
        return LambdaWrapper(lambda n: lambda f: term(n(f)))

    def __repr__(self):
        return "mult"


class PredecessorCombinator(Combinator):
    def __call__(self, term):
        return LambdaWrapper(lambda f: lambda x: term(lambda g: lambda h: h(g(f)))(lambda u: x)(lambda u: u))

    def __repr__(self):
        return "pred"


plus = PlusCombinator()
succ = SuccessorCombinator()
mult = MultiplyCombinator()
pred = PredecessorCombinator()


true = LambdaWrapper(lambda a: lambda b: a)
false = LambdaWrapper(lambda a: lambda b: b)


class IsZeroCombinator(Combinator):
    def __call__(self, term):
        return term(K(false))(true)

    def __repr__(self):
        return "?zero"


iszero = IsZeroCombinator()


class BooleanEvaluator(Combinator):
    def is_lazy(self):
        return True

    def eval(self):
        self.term.eval()
        return self.term

    def __call__(self, term):
        self.true_counter = StepCombinator()
        self.false_counter = StepCombinator()
        self.term = term(self.true_counter)(self.false_counter)(I)
        return term

    def __bool__(self):
        return self.true_counter.steps > self.false_counter.steps
