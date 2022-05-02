from github import Repository, ContentFile

import json
import sympy as sy
import copy
from src.regex_functions import in_regex, in_regex_list, any_string_in_pattern

class repo_evaluator:

    def get_expr_arg_dict(self, expr : sy.Expr):

        def _add_expr_args_to_dict(expr : sy.Expr , unique_args : dict):
            if len(expr.args) == 0:
                unique_args[expr] = None
            else:
                for arg in expr.args:
                    _add_expr_args_to_dict(arg, unique_args)

        unique_args = {}
        _add_expr_args_to_dict(expr, unique_args)
        return unique_args

    def check_args_exist_in_dict(self, args : dict, target : dict):

        for arg in args.keys():
            if not target.get(str(arg), False) or target[str(arg)] == None:
                raise Exception("Equation \"" + str(target['equation']) +  "\" contains an argument that is not defined in the search description: " + str(arg))
                
    def clean_equation(self, equation : str):
        equation = equation.replace('and', '&').replace('or', '|').replace('not', '~').replace('!', '~')
        equation = sy.parsing.sympy_parser.parse_expr(equation, evaluate=False)
        equation = sy.to_dnf(equation, simplify=True)

        return equation

    def __init_code_targets(self, code_targets : dict):

        code_targets['equation'] = self.clean_equation(code_targets['equation'])
        code_targets['args'] = self.get_expr_arg_dict(code_targets['equation'])

        self.check_args_exist_in_dict(code_targets['args'], code_targets)

        for target in code_targets['args']:
            if type(target) == dict:
                raise Exception("Cannot have another target type inside a code target")

        return code_targets

    def __init_file_targets(self, file_targets : dict):
            
        file_targets['equation'] = self.clean_equation(file_targets['equation'])
        file_targets['args'] = self.get_expr_arg_dict(file_targets['equation'])

        self.check_args_exist_in_dict(file_targets['args'], file_targets)

        for arg in file_targets['args']:
            target = file_targets[str(arg)]
            if type(target) == dict:
                target_type = target.get('target_type', None)
                
                if target_type == None:
                    raise Exception("Target must have a 'target_type' key")
                elif target_type == "repo" or target_type == "dir" or target_type == "file":
                    raise Exception("Cannot have a "+ target_type +" target inside a file")
                elif target_type == "code":
                    file_targets[str(arg)] = self.__init_code_targets(target)
                else:
                    raise Exception("Target type not recognized: " + target["target_type"])

        return file_targets

    def __init_dir_targets(self, dir_targets: dict):

        dir_targets['equation'] = self.clean_equation(dir_targets['equation'])
        dir_targets['args'] = self.get_expr_arg_dict(dir_targets['equation'])

        self.check_args_exist_in_dict(dir_targets['args'], dir_targets)

        for arg in dir_targets['args']:
            target = dir_targets[str(arg)]
            if type(target) == dict:
                target_type = target.get('target_type', None)

                if target_type == None:
                    raise Exception("Target must have a 'target_type' key")
                elif target_type == "repo":
                    raise Exception("Cannot have a " + target_type + "target inside a dir")
                elif target_type == "dir":
                    raise Exception("Cannot have a dir target inside a dir... Multiple levels of dir targets are partially supported via the \' \"recursive\" : true\' arg")
                elif target_type == "file":
                    dir_targets[str(arg)] = self.__init_file_targets(target)
                elif target_type == "code":

                    wrapper_file_target = {
                        "target_type": "file",
                        "x1": copy.deepcopy(target),
                        "equation": "x1",
                    }

                    dir_targets[str(arg)] = self.__init_file_targets(wrapper_file_target)

                else:
                    raise Exception("Target type not recognized: " + target["target_type"])

        return dir_targets

    def __init_repo_targets(self, repo_targets : dict):

        repo_targets['equation'] = self.clean_equation(repo_targets['equation'])
        repo_targets['args'] = self.get_expr_arg_dict(repo_targets['equation'])

        self.check_args_exist_in_dict(repo_targets['args'], repo_targets)

        for arg in repo_targets['args']:
            target = repo_targets[str(arg)]
            if type(target) == dict:

                target_type = target.get('target_type', None)
                
                if target_type == None:
                    raise Exception("Target must have a 'target_type' key")
                if target_type == "repo":
                    raise Exception("Cannot have a repo target inside a repo")
                elif target_type == "dir":
                    repo_targets[str(arg)] = self.__init_dir_targets(target)
                elif target_type == "file" or target_type == "code":

                    wrapper_dir_target = {
                        "target_type": "dir",
                        "x1": copy.deepcopy(target),
                        "equation": "x1",
                    }

                    repo_targets[str(arg)] = self.__init_dir_targets(wrapper_dir_target)

                else:
                    raise Exception("Target type not recognized: " + target["target_type"])
        

        return repo_targets

    def __init_targets(self, targets:dict):

        if type(targets) == dict:

            target_type = targets.get('target_type', None)

            if target_type == None:
                raise Exception("Target must have a 'target_type' key")

            if target_type == "repo":
                targets = self.__init_repo_targets(targets)
            elif target_type == "dir" or target_type == "file" or target_type == "code":

                wrapper_repo_target = {
                    "target_type": "repo",
                    "x1": copy.deepcopy(targets),
                    "equation": "x1",
                }
                targets = self.__init_repo_targets(wrapper_repo_target)

            else:
                raise Exception("Target type not recognized: " + targets["target_type"])
        else:
            raise Exception("Target must be a dict with a 'target_type' key\n Target: " + str(targets))

        return targets

    def __init__(self, search_dict : dict):
        self.search_dict = search_dict

        self.targets = self.search_dict.get('targets')
        self.max_file_size = self.search_dict.get('max_file_size', 1000000)

        # Dummy "accept all" target if none provided
        if self.targets is None or len(self.targets) == 0:
            self.targets = {
            "target_type":"repo",
             "x1":".*",
             "equation":"x1"
             }
            
        self.search_name = self.search_dict.get('name', "")

        self.targets = self.__init_targets(self.targets)

    def evaluate_equation(self, equation: sy.Expr, args: dict):
        
        equation_result = equation.subs(args)
        if type(equation_result) == sy.logic.boolalg.BooleanTrue:
            return True
        elif type(equation_result) == sy.logic.boolalg.BooleanFalse:
            return False
        else:
            return None

    def eval_code_targets(self, repo: Repository.Repository, contents : ContentFile.ContentFile, targets : dict):

        code = str(contents.decoded_content.decode('utf-8', 'ignore'))        

        code_args = targets['args']

        equation_result = self.evaluate_equation(targets['equation'], code_args)

        if equation_result is not None:
            return equation_result

        for arg in code_args:

            arg_regex = targets[str(arg)]

            if in_regex(arg_regex, code):
                code_args[arg] = True

                equation_result = self.evaluate_equation(targets['equation'], code_args)

                if equation_result is not None:
                    return equation_result

        return False

    def eval_file_targets(self, repo: Repository.Repository, contents : ContentFile.ContentFile, targets : dict):
        
        file_args = targets['args']
        matching_files = set()    

        accept_any_file = True

        for arg in file_args:
            
            arg_regex = targets[str(arg)]
            if type(arg_regex) == str:

                accept_any_file = False

                for file in contents:
                    file_name = file.path.split('/')[-1]

                    if in_regex(arg_regex, file_name):
                        matching_files.add(file)
                        file_args[arg] = True
  
        for arg in file_args:

            # if file name wasn't found, then set to false
            if type(targets[str(arg)]) == str and file_args[arg] == None: 
                file_args[arg] = False

        equation_result = self.evaluate_equation(targets['equation'], file_args)

        if equation_result is not None:
            return equation_result

        if accept_any_file:
            for file in contents:
                matching_files.add(file)

        for arg in file_args:

            arg_regex = targets[str(arg)]

            if type(arg_regex) == str:
                continue
            else:

                for file in matching_files:

                    if self.eval_code_targets(repo, file, targets[str(arg)]):
                        file_args[arg] = True
                        break

                if file_args[arg] != True:
                    file_args[arg] = False

                equation_result = self.evaluate_equation(targets['equation'], file_args)

                if equation_result is not None:
                    return equation_result

        return self.evaluate_equation(targets['equation'], file_args)


    def eval_dir_targets(self, repo: Repository.Repository, contents : ContentFile.ContentFile, targets : dict):

        matching_dirs = set() # need to both recurse and call dir targets as well as file targets.
        unmatching_dirs = set() # need to recurse and call dir targets here
        
        targets_copy = copy.deepcopy(targets)

        recursive = targets.get('recursive', False)

        dir_args = targets['args']

        accept_any_dir = True

        for arg in dir_args:

            arg_regex = targets[str(arg)]

            if type(arg_regex) == str: # else it's a file target

                accept_any_dir = False

                for item in contents:
                    if item.type == "dir":

                        dir_name_match = in_regex(arg_regex, item.name)
                        
                        if dir_name_match:
                            dir_args[arg] = True
                            matching_dirs.add(item.name)
                            # if recursive, then dir name discovery is passed to recursive call
                            if recursive: 
                                targets_copy['args'][arg] = True
                                
                        else:
                            if dir_args[arg] != True:
                                dir_args[arg] = False
                            unmatching_dirs.add(item.name)

        if accept_any_dir:
            for item in contents:
                if item.type == "dir":
                    matching_dirs.add(item.name)

        equation_result = self.evaluate_equation(targets['equation'], dir_args)

        if equation_result is not None:
            return equation_result

        all_dirs = matching_dirs.union(unmatching_dirs)

        for dir_name in all_dirs: # Recurse through all directories
            dir_contents = repo.get_contents(dir_name)
            if dir_contents is not None:
                dir_eval = self.eval_dir_targets(repo, dir_contents, copy.deepcopy(targets_copy)) # recurse in subdir
                if dir_eval == True:
                    return True

        for arg in dir_args.keys():

            if dir_args[arg] != None:
                continue
            else:
                for dir_name in matching_dirs:
                    dir_contents = repo.get_contents(dir_name)

                    if dir_contents is not None:

                        file_eval = self.eval_file_targets(repo, dir_contents, targets[str(arg)])

                        if file_eval == True:
                            dir_args[arg] = True

                            equation_result = self.evaluate_equation(targets['equation'], dir_args)

                            if equation_result is not None: # equation can be decided before all files are evaluated
                                return equation_result 

                if dir_args[arg] == None: # pattern not found in this dir
                    dir_args[arg] = False

        return self.evaluate_equation(targets['equation'], dir_args)
        # return False

    def eval_repo_targets(self, repo : Repository.Repository, contents : ContentFile.ContentFile, targets : dict):

        repo_args = targets['args']

        for arg in repo_args.keys(): # loop through repo name regexes 

            arg_regex = targets[str(arg)]

            if type(arg_regex) == str: # else it's a dir target
                repo_args[arg] = in_regex( arg_regex, repo.name)

        equation_result = self.evaluate_equation(targets['equation'], repo_args)

        if equation_result is not None:
            return equation_result

        for arg in repo_args.keys(): # after checking repo names, check dirs
            
            if repo_args[arg] != None:
                continue
            else:
                repo_args[arg] = self.eval_dir_targets(repo, contents, targets[str(arg)])

            equation_result = self.evaluate_equation(targets['equation'], repo_args)

            if equation_result is not None:
                return equation_result

        return False

    def eval_repository(self,repo : Repository.Repository):

        if self.targets == None: # no target specified
            return True

        targets = copy.deepcopy(self.targets)

        contents = repo.get_contents("")

        if targets['target_type'] == "repo":
            return self.eval_repo_targets(repo, contents, targets)

        else:
            raise Exception("Some error occured while initializing the targets")

def main():

    import os
    from github import Github
    from decouple import config   

    with open('searches.json') as json_file:
        searches = json.load(json_file)

    searcher = repo_evaluator(searches[0])

    # get personal access token
    if not os.path.exists('.env'):
        raise Exception('Please create .env file with the following content:\n\nGITHUB_TOKEN=')

    github_oaut_token = config('GITHUB_TOKEN')

    g = Github(login_or_token=github_oaut_token)

    remaining, request_limit = g.rate_limiting
    print("Remaining: %s, Limit: %s" % (remaining, request_limit))

    repo = g.get_repo("hodgespodge/github-mining")

    print(repo.clone_url)

    print("\nevaling repo: " + str(repo)+"\n")

    print(searcher.eval_repository(repo))

if __name__ == "__main__":
    main()