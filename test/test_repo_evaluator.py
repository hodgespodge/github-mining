import unittest

from src.repo_evaluator import repo_evaluator
import json

class TestRepoEvaluator(unittest.TestCase):
    def test_repo_evaluator(self):
        searches = None
        with open('test/test_searches.json') as json_file:
            searches = json.load(json_file)
            
        evaluator = repo_evaluator(searches[0])

        print(evaluator.search_description)

        # self.assertEqual(evaluator.search_description, True)
        