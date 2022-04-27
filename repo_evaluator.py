from github import Repository

import json
import sympy as sy

class repo_evaluator:

    def get_expr_arg_set(self, expr : sy.Expr):

        def _add_expr_args_to_set(expr : sy.Expr , unique_args : set):
                if len(expr.args) == 0:
                    unique_args.add(expr)
                else:
                    for arg in expr.args:
                        _add_expr_args_to_set(arg, unique_args)

        unique_args = set()
        _add_expr_args_to_set(expr, unique_args)
        return unique_args

    def check_args_exist_in_dict(self, args : set, target : dict):

        for arg in args:
            if not target.get(str(arg), False) or target[str(arg)] == None:
                raise Exception("Equation \"" + str(target['equation']) +  "\" contains an argument that is not in the search description: " + str(arg))
                
    def clean_equation(self, equation : str):
        equation = equation.replace('and', '&').replace('or', '|').replace('not', '~').replace('!', '~')
        equation = sy.parsing.sympy_parser.parse_expr(equation, evaluate=False)
        equation = sy.to_dnf(equation, simplify=True)
        return equation

    def __init_code_targets(self, code_targets : dict):

        code_targets['equation'] = self.clean_equation(code_targets['equation'])
        code_targets['code_args'] = self.get_expr_arg_set(code_targets['equation'])

        print("Code equation: " + str(code_targets['equation']))

        self.check_args_exist_in_dict(code_targets['code_args'], code_targets)

        for target in code_targets['code_args']:
            if type(target) == dict:
                raise Exception("Cannot have another target type inside a code target")

        return code_targets

    def __init_file_targets(self, file_targets : dict):
            
        file_targets['equation'] = self.clean_equation(file_targets['equation'])
        file_targets['file_args'] = self.get_expr_arg_set(file_targets['equation'])

        print("File equation: " + str(file_targets['equation']))

        self.check_args_exist_in_dict(file_targets['file_args'], file_targets)

        for arg in file_targets['file_args']:
            target = file_targets[str(arg)]
            if type(target) == dict:
                target_type = target.get('target_type', None)
                
                if target_type == None:
                    raise Exception("Target must have a 'target_type' key")
                if target_type == "repo":
                    raise Exception("Cannot have a repo target inside a file")
                elif target_type == "dir":
                    raise Exception("Cannot have a dir target inside a file")
                elif target_type == "file":
                    raise Exception("Cannot have a file target inside a file")
                elif target_type == "code":
                    target = self.__init_code_targets(target)
                else:
                    raise Exception("Target type not recognized: " + target["target_type"])

        return file_targets

    def __init_dir_targets(self, dir_targets: dict):

        dir_targets['equation'] = self.clean_equation(dir_targets['equation'])
        dir_targets['dir_args'] = self.get_expr_arg_set(dir_targets['equation'])

        print("Dir equation: " + str(dir_targets['equation']))

        self.check_args_exist_in_dict(dir_targets['dir_args'], dir_targets)

        for arg in dir_targets['dir_args']:
            target = dir_targets[str(arg)]
            if type(target) == dict:
                target_type = target.get('target_type', None)

                if target_type == None:
                    raise Exception("Target must have a 'target_type' key")
                if target_type == "repo":
                    raise Exception("Cannot have a repo target inside a dir")
                elif target_type == "dir":
                    raise Exception("Cannot have a dir target inside a dir")
                elif target_type == "file":
                    target = self.__init_file_targets(target)
                elif target_type == "code":
                    target = self.__init_code_targets(target)
                else:
                    raise Exception("Target type not recognized: " + target["target_type"])

        return dir_targets

    def __init_repo_targets(self, repo_targets : dict):

        repo_targets['equation'] = self.clean_equation(repo_targets['equation'])
        repo_targets['repo_args'] = self.get_expr_arg_set(repo_targets['equation'])

        print("Repo equation: " + str(repo_targets['equation']))

        self.check_args_exist_in_dict(repo_targets['repo_args'], repo_targets)

        for arg in repo_targets['repo_args']:
            target = repo_targets[str(arg)]
            if type(target) == dict:

                target_type = target.get('target_type', None)
                
                if target_type == None:
                    raise Exception("Target must have a 'target_type' key")
                if target_type == "repo":
                    raise Exception("Cannot have a repo target inside a repo")
                elif target_type == "dir":
                    target = self.__init_dir_targets(target)
                elif target_type == "file":
                    target = self.__init_file_targets(target)
                elif target_type == "code":
                    target = self.__init_code_targets(target)
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
            elif target_type == "dir":
                targets = self.__init_dir_targets(targets)
            elif target_type == "file":
                targets = self.__init_file_targets(targets)
            elif target_type == "code":
                targets = self.__init_code_targets(targets)
            else:
                raise Exception("Target type not recognized: " + targets["target_type"])
        else:
            raise Exception("Target must be a dict with a 'target_type' key\n Target: " + str(targets))

        return targets

    def __init__(self, search_description : dict):
        self.search_description = search_description

        self.targets = self.search_description.get('targets')
        self.max_file_size = self.search_description.get('max_file_size', 1000000)

        if self.targets is None:
            return

        self.targets = self.__init_targets(self.targets)

        
    def eval_repo(self,repo : Repository.Repository):

        if self.repo_target == None: # no target specified
            return True

        

    
def main():

    with open('searches.json') as json_file:
        searches = json.load(json_file)

    searcher = repo_evaluator(searches[0])



if __name__ == "__main__":
    main()