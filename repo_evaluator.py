from github import Repository, ContentFile

import json
import sympy as sy
import copy
from regex_functions import in_regex, in_regex_list

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
        print(type(type(equation)))

        return equation

    def __init_code_targets(self, code_targets : dict):

        code_targets['equation'] = self.clean_equation(code_targets['equation'])
        code_targets['args'] = self.get_expr_arg_dict(code_targets['equation'])

        # print("Code equation: " + str(code_targets['equation']))

        print("Code targets:" + str(code_targets)+"\n")

        self.check_args_exist_in_dict(code_targets['args'], code_targets)

        for target in code_targets['args']:
            if type(target) == dict:
                raise Exception("Cannot have another target type inside a code target")

        return code_targets

    def __init_file_targets(self, file_targets : dict):
            
        file_targets['equation'] = self.clean_equation(file_targets['equation'])
        file_targets['args'] = self.get_expr_arg_dict(file_targets['equation'])

        # print("File equation: " + str(file_targets['equation']))

        print("File targets:" + str(file_targets)+"\n")

        self.check_args_exist_in_dict(file_targets['args'], file_targets)

        for arg in file_targets['args']:
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
        dir_targets['args'] = self.get_expr_arg_dict(dir_targets['equation'])

        # print("Dir equation: " + str(dir_targets['equation']))

        print("Dir targets:" + str(dir_targets)+"\n")

        self.check_args_exist_in_dict(dir_targets['args'], dir_targets)

        for arg in dir_targets['args']:
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

                    wrapper_file_target = {
                        "target_type": "file",
                        "x1": copy.deepcopy(target),
                        "equation": "x1",
                    }

                    print("initing file target with dummy wrapper")

                    # TODO: need to add (always true file to wrap code requirement)
                    # target = self.__init_code_targets(target)
                    target = self.__init_file_targets(wrapper_file_target)

                else:
                    raise Exception("Target type not recognized: " + target["target_type"])

        return dir_targets

    def __init_repo_targets(self, repo_targets : dict):

        repo_targets['equation'] = self.clean_equation(repo_targets['equation'])
        repo_targets['args'] = self.get_expr_arg_dict(repo_targets['equation'])

        # print("Repo equation: " + str(repo_targets['equation']))

        print("Repo targets:" + str(repo_targets)+"\n")

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
                    target = self.__init_dir_targets(target)
                elif target_type == "file" or target_type == "code":

                    wrapper_dir_target = {
                        "target_type": "dir",
                        "x1": copy.deepcopy(target),
                        "equation": "x1",
                    }

                    print("initing dir target with dummy wrapper")
                    # TODO: need to add (always true dir to wrap file requirement)
                    target = self.__init_dir_targets(wrapper_dir_target)

                # elif target_type == "code":
                #     # TODO: need to add (always true file to wrap code requirement)
                #     target = self.__init_code_targets(target)
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

                # targets = self.__init_dir_targets(targets)
            # elif target_type == "file":
            #     targets = self.__init_file_targets(targets)
            # elif target_type == "code":
            #     targets = self.__init_code_targets(targets)
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

        print()
        print("Targets: " + str(self.targets))
        print()
    def evaluate_equation(self, equation: sy.Expr, args: dict):
        print("evaluating equation: " + str(equation))
        print("args: " + str(args))
        equation_result = equation.subs(args)
        print("equation result: " + str(equation_result))

        if type(equation_result) == bool:
            return equation_result
        else:
            print("")

    def eval_repo_targets(self, repo : Repository.Repository, contents : ContentFile.ContentFile, targets : dict):

        repo_args = targets['args']

        for arg in repo_args.keys():

            arg_regex = targets[str(arg)]

            if type(arg_regex) == str: # else it's a dict
                repo_args[arg] = in_regex( arg_regex, repo.name)

        equation_result = self.evaluate_equation(targets['equation'], repo_args)

        # print(equation_result)

        # loop and eval dir targets. 
        # If the equation_result returns a bool value at any point, return it

        return equation_result


    def eval_repository(self,repo : Repository.Repository):

        if self.targets == None: # no target specified
            return True

        targets = copy.deepcopy(self.targets)

        contents = repo.get_contents("")

        if targets['target_type'] == "repo":
            return self.eval_repo_targets(repo, contents, targets)
        # elif targets['target_type'] == "dir":
        #     return self.eval_dir_targets(repo, contents, targets)
        # elif targets['target_type'] == "file":
        #     return self.eval_file_targets(repo, contents, targets)
        # elif targets['target_type'] == "code":
        #     return self.eval_code_targets(repo, contents, targets)
        else:
            raise Exception("Target type not recognized: " + targets["target_type"])

        # while contents:
        #     file_content = contents.pop(0)
        #     if file_content.type == "dir":

        #         folder_name_found, folder_name_pattern = in_regex_list(file_content.name, dir_targets)

        #         if folder_name_found:
        #             return True, file_content.name, folder_name_pattern


        #         contents.extend(repo.get_contents(file_content.path))
        #     else:

        #         file_name = file_content.path.split('/')[-1]
        #         # print(file_name)

        #         if file_content.size > max_file_size:
        #             continue

        #         # check if file is in files_targets (with regex)
        #         file_type_found , file_type_target = in_regex_list(file_name, files_targets.keys()) 

        #         if file_type_found:
        #             try:
        #                 code = str(file_content.decoded_content.decode('utf-8', 'ignore'))
                        
        #                 #check if code string contains any of the targets in target using regex
        #                 for target in files_targets[file_type_target]:
        #                     # print("Checking if target: ", target, " is in file: ", file_name)

        #                     if re.search(target, code):
        #                         print("Found Target: \"", target,"\"")
        #                         # print(code)
        #                         return True, file_name, target
        #             except AssertionError:
        #                 print("Error decoding file: ", file_content.path)
                    
        # return False, "", ""    #code_target_found, target_file_name, target 



    
def main():

    import os
    from github import Github
    from decouple import config   

    with open('searches2.json') as json_file:
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

    print(searcher.eval_repository(repo))

if __name__ == "__main__":
    main()