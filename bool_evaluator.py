import sympy as sy

import json
import repo_evaluator

# need to parse json equation as sympy expression

logic_expression = '(((x1 and x2) or (x3 and x4)) and (x5 or x6))'

# logic_expression = '(((x1 & x2) | (x3 & x4)) & (x5 | x6))'

logic_expression = logic_expression.replace('and', '&').replace('or', '|').replace('not', '~')

a = sy.parsing.sympy_parser.parse_expr(logic_expression, evaluate=False)

# print(a)
# print(a.subs({'x1': True, 'x2': True, 'x3': True, 'x4': True, 'x5': False, 'x6': False}))

# conver the expression to disjunctive normal form ()
a = sy.to_dnf(a, simplify=True)

print(a)
print(a.subs({'x1': True, 'x2': True, 'x3': True, 'x4': True, 'x5': False, 'x6': False}))

# split the disjunctions into a list
disjunctions = a.args


print(disjunctions)

searches = None

with open('searches.json') as json_file:
    searches = json.load(json_file)

print(searches)

evaluator = repo_evaluator(searches)

