#!/usr/bin/env python

from github import Github       #pip3 install pyGithub
from decouple import config     #pip3 install python-decouple
from time import sleep
import datetime
import re

from os import path

def main():

    keywords = ['ros','ros2']
    qualifiers = ['stars:>2', 'language:python']
    # languages = ['Python','C++']
    # sort = ''       #('stars', 'forks', 'updated')
    # order = ''      #('asc', 'desc')

    # checked_repos = set()

    searchable_files = ['.*.py', 'CMakeLists.txt', 'package.xml'] 

    targets = ['test']

    if not path.exists('.env'):
        raise Exception('Please create .env file with the following content:\n\nGITHUB_TOKEN=')

    github_oaut_token = config('GITHUB_TOKEN')

    g = Github(login_or_token=github_oaut_token)


    remaining, request_limit = g.rate_limiting

    print("Remaining: %s, Limit: %s" % (remaining, request_limit))

    while(True):

        try:

            while(remaining > 1):

                query = ' '.join(keywords) + ' ' + ' '.join(qualifiers)

                print(query)

                repos = g.search_repositories(query=query)

                # print(repos)

                for repo in repos:

                    print("")

                    contents = repo.get_contents("")

                    # repo.get

                    while contents:
                        file_content = contents.pop(0)
                        if file_content.type == "dir":
                            contents.extend(repo.get_contents(file_content.path))
                        else:

                            file_name = file_content.path.split('/')[-1]
                            print(file_name)

                            # check if file is in searchable_files (with regex)
                            if any(re.search(pattern, file_name) for pattern in searchable_files):
                                print("Found file: %s" % file_name)

                                code = file_content.decoded_content.decode('utf-8', 'ignore')
                                # print(code)

                                #TODO check if code contains any of the targets
                                #if yes, save the repo
                    
                remaining, request_limit = g.rate_limiting
                print("Remaining: %s, Limit: %s" % (remaining, request_limit))
                sleep(100)
                
        except KeyboardInterrupt:
            print("\nExiting early...")
            print(remaining , " github requests remaining")
            return False

        reset_time = g.rate_limiting_resettime

        try:

            # sleep until the reset time
            print("Sleeping for %s seconds" % (reset_time - datetime.datetime.now().timestamp()))
            sleep(reset_time - datetime.datetime.now().timestamp())
            
        except KeyboardInterrupt:
            print("\nExiting timeout")
            return False


if __name__ == '__main__':
    main()