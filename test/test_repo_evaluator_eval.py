import pytest

from src.repo_evaluator import repo_evaluator
from src.github_functions import authenticate
import json
import copy

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
def test_authenticate(g):
    assert g is not None

def test_eval_repo_name(g,searches):
    # print(searches)
    # print(g)
    pass

    