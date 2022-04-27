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

        return code_targets

    def __init_file_targets(self, file_targets : dict):
            
        return file_targets

    def __init_directory_targets(self, directory_targets: dict):

        return directory_targets

    def __init_repo_targets(self, repo_targets : dict):

        self.repo_targets['equation'] = self.clean_equation(repo_targets['equation'])
        print(self.repo_targets['equation'])

        self.repo_targets['repo_args'] = self.get_expr_arg_set(self.repo_targets['equation'])

        self.check_args_exist_in_dict(self.repo_targets['repo_args'], self.repo_targets)

        for arg in self.repo_targets['repo_args']:
            
            target = self.repo_targets[str(arg)]
            if type(target) != dict:
                continue

            # TODO: do I allow repo_targets to hold a file_targets? Or must it be within a directory_targets
        
        return repo_targets

    def __init__(self, search_description : dict):
        self.search_description = search_description

        self.repo_targets = self.search_description.get('repo_targets')
        self.max_file_size = self.search_description.get('max_file_size', 1000000)

        if self.repo_targets is None:
            return

        self.repo_targets = self.__init_repo_targets(self.repo_targets)

        
    def eval_repo(self,repo : Repository.Repository):

        if self.repo_target == None: # no target specified
            return True

        

    
def main():

    with open('searches.json') as json_file:
        searches = json.load(json_file)


    searcher = repo_evaluator(searches[0])



if __name__ == "__main__":
    main()