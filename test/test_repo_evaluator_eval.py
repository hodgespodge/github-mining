import pytest

from src.repo_evaluator import repo_evaluator
from src.github_functions import authenticate
from github import Github
import json

from sympy import Symbol

@pytest.fixture(scope="module")
def searches():
    json_path = "test/test_jsons/test_repo_evaluator_eval.json"
    with open(json_path) as json_file:
        return json.load(json_file)

@pytest.fixture(scope="module")
def g():
    return authenticate()

@pytest.mark.order(1)
def test_authenticate(g: Github):
    assert g is not None

def test_eval_repo_name(g: Github,searches):
    repo = g.get_repo("hodgespodge/github-mining")

    searcher = repo_evaluator(searches[0])

    assert searcher.search_name == "eval this repo name"
    assert searcher.eval_repository(repo) == True

def test_eval_dir_name(g: Github,searches):

    searcher = repo_evaluator(searches[1])

    assert searcher.search_name == "eval this dir name"
    assert searcher.eval_repository(g.get_repo("hodgespodge/github-mining")) == True