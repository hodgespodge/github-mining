#!/usr/bin/env python

from github import Github       #pip3 install pyGithub
from decouple import config     #pip3 install python-decouple
from time import sleep
import datetime

from os import path

search_term_list = ['behaviortree_ros']

if not path.exists('.env'):
    raise Exception('Please create .env file with the following content:\n\nGITHUB_TOKEN=')

github_oaut_token = config('GITHUB_TOKEN')

g = Github(login_or_token=github_oaut_token)


remaining, request_limit = g.rate_limiting

print("Remaining: %s, Limit: %s" % (remaining, request_limit))

while(True):

    while(remaining > 1):
        sleep(10)
        remaining, request_limit = g.rate_limiting
        # print("Remaining: %s, Limit: %s" % (remaining, request_limit))

    

    reset_time = g.rate_limiting_resettime

    # sleep until the reset time
    sleep(reset_time - datetime.datetime.now().timestamp())

    print("Sleeping for %s seconds" % (reset_time - datetime.datetime.now().timestamp()))