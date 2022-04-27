from github import Repository

class repo_evaluator:

    def __init__(self, search_description : dict):
        self.search_description = search_description

        self.repo_target = self.search_description.get('repo_target')
        self.max_file_size = self.search_description.get('max_file_size', 1000000)

        if self.repo_target is not None:
            

        
    def eval_repo(self,repo : Repository.Repository):

        if self.repo_target == None: # no target specified
            return True

        

    
