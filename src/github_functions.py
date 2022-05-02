from github import Github
import os
from decouple import config  


def authenticate(print_rate_limit=False):

    if not os.path.exists('.env'):
        raise Exception('Please create .env file with the following content:\n\nGITHUB_TOKEN=')

    github_oaut_token = config('GITHUB_TOKEN')
    g = Github(login_or_token=github_oaut_token)

    if print_rate_limit:
        remaining, request_limit = g.rate_limiting
        print("Remaining: %s, Limit: %s" % (remaining, request_limit))

    return g

