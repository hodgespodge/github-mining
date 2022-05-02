from github import Github
import os
from decouple import config  

def authenticate(github_token=None) -> Github:

    if type(github_token) != str:
        if not os.path.exists('.env'):
            raise Exception('Please create .env file with the following content:\n\nGITHUB_TOKEN=')

        github_token = config('GITHUB_TOKEN')

    return Github(login_or_token=github_token)
