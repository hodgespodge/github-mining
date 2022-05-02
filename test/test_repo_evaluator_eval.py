import unittest

from src.repo_evaluator import repo_evaluator
import json
import copy

from sympy import Symbol

class TestRepoEvaluatorEval(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRepoEvaluatorEval, self).__init__(*args, **kwargs)

    def get_searches(self):
        json_path = "test/test_jsons/test_repo_evaluator_eval.json"
        with open(json_path) as json_file:
            return json.load(json_file)

    