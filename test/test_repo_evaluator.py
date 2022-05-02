import unittest

from src.repo_evaluator import repo_evaluator
import json
import copy

from sympy import Symbol

class TestRepoEvaluator(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestRepoEvaluator, self).__init__(*args, **kwargs)

        self.DEFAULT_REPO_TARGET = {
            "target_type":"repo",
             "x1":".*",
             "equation":Symbol("x1"),
             "args":{
                 Symbol("x1"):None
                }
             }

        self.DIR_TARGET = copy.deepcopy(self.DEFAULT_REPO_TARGET)
        self.DIR_TARGET["x1"] = {
            "target_type":"dir",
            "x1":".*",
            "equation":Symbol("x1"),
            "args":{
                Symbol("x1"):None
            }
        }

        self.FILE_TARGET = copy.deepcopy(self.DIR_TARGET)
        self.FILE_TARGET["x1"]["x1"] = {
            "target_type":"file",
            "x1":".*",
            "equation":Symbol("x1"),
            "args":{
                Symbol("x1"):None
            }
        }

        self.CODE_TARGET = copy.deepcopy(self.FILE_TARGET)
        self.CODE_TARGET["x1"]["x1"]["x1"] = {
            "target_type":"code",
            "x1":".*",
            "equation":Symbol("x1"),
            "args":{
                Symbol("x1"):None
            }
        }

    def get_searches(self, repo_name):
        json_folder = "test/test_jsons"
        with open(json_folder + "/"+ repo_name + ".json" ) as json_file:
            return json.load(json_file)

    def test_empty_targets(self):

        searches = self.get_searches("test_repo_evaluator")
    
        no_targets_evaluator = repo_evaluator(searches[0])
        self.assertEqual(no_targets_evaluator.search_name, "no targets")

        empty_targets_evaluator = repo_evaluator(searches[1])
        self.assertEqual(empty_targets_evaluator.search_name, "empty targets")

        self.assertEqual(empty_targets_evaluator.targets, self.DEFAULT_REPO_TARGET)
        self.assertEqual(no_targets_evaluator.targets, self.DEFAULT_REPO_TARGET)

    def test_repo_target_initialization(self):

        searches = self.get_searches("test_repo_evaluator")

        repo_target_evaluator = repo_evaluator(searches[2])
        self.assertEqual(repo_target_evaluator.search_name, "repo target init")

        repo_target = self.DEFAULT_REPO_TARGET

        self.assertEqual(repo_target_evaluator.targets, repo_target)

    def test_dir_target_initialization(self):

        searches = self.get_searches("test_repo_evaluator")

        dir_target_evaluator = repo_evaluator(searches[3])
        self.assertEqual(dir_target_evaluator.search_name, "dir target init")

        dir_target = self.DIR_TARGET

        self.assertEqual(dir_target_evaluator.targets, dir_target)

    def test_file_target_initialization(self):

        searches = self.get_searches("test_repo_evaluator")

        file_target_evaluator = repo_evaluator(searches[4])
        self.assertEqual(file_target_evaluator.search_name, "file target init")

        file_target = self.FILE_TARGET

        self.assertEqual(file_target_evaluator.targets, file_target)

    def test_code_target_initialization(self):

        searches = self.get_searches("test_repo_evaluator")

        code_target_evaluator = repo_evaluator(searches[5])
        self.assertEqual(code_target_evaluator.search_name, "code target init")

        code_target = self.CODE_TARGET

        self.assertEqual(code_target_evaluator.targets, code_target)
