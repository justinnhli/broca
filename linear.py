#!/usr/bin/env python3

from math import ceil
from random import choice, sample, shuffle, randrange, randint

VARIABLE_DIFFICULTY = 4

class Line:
    LINE_ID = 0
    def __init__(self, **kwargs):
        self.line_id = Line.LINE_ID
        Line.LINE_ID += 1
        self.parents = set()
        self.children = set()
        self.vars_in = set()
        self.min_vars_in = kwargs.get('min_vars_in', 0)
        self.max_vars_in = kwargs.get('max_vars_in', 3)
    def __hash__(self):
        return self.line_id
    def emit_code(self):
        raise NotImplementedError()
    def emit_dot(self):
        raise NotImplementedError()

class VarAss(Line):
    def __init__(self, variable, **kwargs):
        super().__init__(**kwargs)
        self.variable = variable
        self.expression = None
    def create_expression(self):
        if len(self.vars_in) == 0:
            self.expression = str(randrange(1, 10))
        else:
            terms = [var.variable for var in self.vars_in]
            num_terms = randrange(2, 6)
            if num_terms > len(terms):
                terms.extend(sample([str(n) for n in range(1, 10)], num_terms - len(terms)))
            shuffle(terms)
            self.expression = terms[0]
            for term in terms[1:]:
                operator = choice(['+', '-', '*', '/'])
                self.expression += ' {} {}'.format(operator, term)
    def emit_code(self):
        return '{} = {}'.format(self.variable, self.expression)
    def emit_dot(self):
        return '{} [label="VarAss({} = {})"]'.format(self.line_id, self.variable, self.expression)

def main():
    lines = []
    line_id = ord('a')
    for i in range(VARIABLE_DIFFICULTY):
        lines.append(VarAss(chr(line_id), max_vars_in=0))
        lines.append(VarAss(chr(line_id), min_vars_in=randint(1, ceil(VARIABLE_DIFFICULTY / 2))))
        line_id += 1
    # connect variable producers and consumers
    producers = [line for line in lines if isinstance(line, VarAss)]
    consumers = [line for line in lines if isinstance(line, VarAss) and line.min_vars_in > 0]
    while consumers:
        producer = choice(producers)
        consumer = choice(consumers)
        if producer is not consumer and producer not in consumer.children:
            producer.children.add(consumer)
            consumer.parents.add(producer)
            consumer.vars_in.add(producer)
            if len(consumer.vars_in) >= consumer.min_vars_in:
                consumers.remove(consumer)
    # create assignment expressions
    for line in producers:
        line.create_expression()
    # print dot
    print('digraph {')
    for line in lines:
        print('    ' + line.emit_dot())
        for child in line.children:
            print('    {} -> {}'.format(line.line_id, child.line_id))
    print('}')
    # dead code elimination
    # remove lines that do not consume and are not consumed
    lines = [line for line in lines if line.parents or line.children]
    # topological sort
    order = []
    while len(order) != len(lines):
        for line in lines:
            if line not in order and line.parents <= set(order):
                order.append(line)
    # emit code
    for line in order:
        print(line.emit_code())




if __name__ == '__main__':
    main()
