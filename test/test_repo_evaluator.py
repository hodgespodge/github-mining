import unittest

from src.repo_evaluator import repo_evaluator
import json

from sympy import Symbol

class TestRepoEvaluator(unittest.TestCase):

    def test_empty_targets(self):

        searches = None

        json_folder = "test/test_jsons/"
        with open(json_folder + "test_repo_evaluator.json" ) as json_file:
            searches = json.load(json_file)
            
        no_targets_evaluator = repo_evaluator(searches[0])
        self.assertEqual(no_targets_evaluator.search_name, "no targets")

        empty_targets_evaluator = repo_evaluator(searches[1])
        self.assertEqual(empty_targets_evaluator.search_name, "empty targets")

        default_target = {
            "target_type":"repo",
             "x1":".*",
             "equation":Symbol("x1"),
             "args":{
                 Symbol("x1"):None
                }
             }

        self.assertEqual(empty_targets_evaluator.targets, default_target)
        self.assertEqual(no_targets_evaluator.targets, default_target)
        