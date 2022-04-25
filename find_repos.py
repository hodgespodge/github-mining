#!/usr/bin/env python

from github import Github
from decouple import config
from time import sleep

github_oaut_token = config('GITHUB_TOKEN')

g = Github(login_or_token=github_oaut_token)


remaining, request_limit = g.rate_limiting

print("Remaining: %s, Limit: %s" % (remaining, request_limit))