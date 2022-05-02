import pytest

from src.repo_evaluator import repo_evaluator
import json
import copy

from sympy import Symbol


@pytest.fixture(scope="module")
def searches():
    json_path = "test/test_jsons/test_repo_evaluator_initialization.json"
    with open(json_path) as json_file:
        return json.load(json_file)

@pytest.fixture(scope="module")
def default_repo_target():
    return {
        "target_type":"repo",
        "x1":".*",
        "equation":Symbol("x1"),
        "args":{
            Symbol("x1"):None
        }
    }

@pytest.fixture(scope="module")
def dir_target(default_repo_target):
    default_repo_target["x1"] = {
        "target_type":"dir",
        "x1":".*",
        "equation":Symbol("x1"),
        "args":{
            Symbol("x1"):None
            }
        }
    return default_repo_target

@pytest.fixture(scope="module")
def file_target(dir_target):
    dir_target["x1"]["x1"] = {
        "target_type":"file",
        "x1":".*",
        "equation":Symbol("x1"),
        "args":{
            Symbol("x1"):None
            }
        }
    return dir_target

@pytest.fixture(scope="module")
def code_target(file_target):
    file_target["x1"]["x1"]["x1"] = {
        "target_type":"code",
        "x1":".*",
        "equation":Symbol("x1"),
        "args":{
            Symbol("x1"):None
            }
        }
    return file_target

def test_empty_targets(searches, default_repo_target):

    no_targets_evaluator = repo_evaluator(searches[0])
    assert no_targets_evaluator.search_name == "no targets"

    empty_targets_evaluator = repo_evaluator(searches[1])
    assert empty_targets_evaluator.search_name == "empty targets"

    assert empty_targets_evaluator.targets == default_repo_target
    assert no_targets_evaluator.targets == default_repo_target

def test_repo_target_initialization(searches, default_repo_target):

    repo_target_evaluator = repo_evaluator(searches[2])
    assert repo_target_evaluator.search_name == "repo target init"

    repo_target = default_repo_target
    assert repo_target_evaluator.targets == repo_target

def test_dir_target_initialization(searches, dir_target):

    dir_target_evaluator = repo_evaluator(searches[3])

    assert dir_target_evaluator.search_name == "dir target init"
    assert dir_target_evaluator.targets == dir_target

def test_file_target_initialization(searches, file_target):

    file_target_evaluator = repo_evaluator(searches[4])

    assert file_target_evaluator.search_name == "file target init"
    assert file_target_evaluator.targets == file_target

def test_code_target_initialization(searches, code_target):

    code_target_evaluator = repo_evaluator(searches[5])

    assert code_target_evaluator.search_name == "code target init"
    assert code_target_evaluator.targets == code_target