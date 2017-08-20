# coding: utf-8

class Stack(list):
    def push(self, *args, **kwargs):
        return super(Stack, self).append(*args, **kwargs)

    def apply(self):
        function = self.pop()
        argument = self.pop()
        self.append(function(argument))

    def reduce(self):
        term = self.pop()
        while self:
            term = term(self.pop())
        result = term.eval()
        assert (not result.is_lazy())
        return result
