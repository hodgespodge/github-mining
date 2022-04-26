#!/usr/bin/env python

from github import Github       #pip3 install pyGithub
from decouple import config     #pip3 install python-decouple
from time import sleep
import datetime
import re
import csv
import hashlib

import os

previous_searches_dir = 'previous_searches'

csv_repo_header = ['full_name','URL','target_found','target_file_name','target']

csv_row_len = len(csv_repo_header)

def regex_file_name(file_name, patterns):
    for pattern in patterns:

        match = re.search(pattern, file_name)

        if match:
            return True , pattern

    return False , None

def boolean_input(prompt, max_trys):
    for i in range(max_trys):

        try:
            answer = input(prompt).capitalize()

        except:

            print("Please enter \"y\" or \"n\".")
            continue

        if answer == 'N':

            return False
        elif answer == 'Y':

            return True
        else:

            print("Please enter \"y\" or \"n\".")

    raise Exception("Too many tries.")


def check_if_already_searched(keywords, qualifiers, files_targets):

    # Default hash() function is randomly seeded, so we need to use a consistent one
    args_hash = hashlib.sha1((str(sorted(keywords)) + str(sorted(qualifiers)) + str(files_targets)).encode('utf-8')).hexdigest()[:12]

    new_file_name = datetime.datetime.now().strftime("%Y-%m-%d") + "_" + str(args_hash) + ".csv"

    if os.path.exists(previous_searches_dir):
        for old_file_name in os.listdir(previous_searches_dir):
            if old_file_name.endswith(".csv"):
                file_hash = old_file_name.split("_")[1].split(".")[0]

                if file_hash == str(args_hash):

                    return True, old_file_name, new_file_name

    else:
        os.mkdir(previous_searches_dir)
    
    return False, new_file_name, new_file_name

def csvify(row: list):

    if len(row) < csv_row_len:
        row.extend([''] * (csv_row_len - len(row)))

    return row

def search_repo_contents(repo):

    contents = repo.get_contents("")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path))
        else:

            file_name = file_content.path.split('/')[-1]
            print(file_name)

            # check if file is in files_targets (with regex)
            file_type_found , target = regex_file_name(file_name, files_targets.keys()) 

            if file_type_found:

                print("Found file: ", file_name, " in target: ", target)

                code = file_content.decoded_content.decode('utf-8', 'ignore')
                # print(code)

                #TODO check if code contains any of the targets

    return False, "", ""    #code_target_found, target_file_name, target 

def main():

    keywords = ['ros','ros2']
    qualifiers = ['stars:>2', 'language:python']
    # languages = ['Python','C++']
    # sort = ''       #('stars', 'forks', 'updated')
    # order = ''      #('asc', 'desc')
    files_targets = {'.*.py':('test'), 'CMakeLists.txt':('test'), 'package.xml':('test')}

    keywords.sort()
    qualifiers.sort()

    checked_repos = set()

    # get personal access token
    if not os.path.exists('.env'):
        raise Exception('Please create .env file with the following content:\n\nGITHUB_TOKEN=')

    github_oaut_token = config('GITHUB_TOKEN')

    g = Github(login_or_token=github_oaut_token)


    # check if we already searched for this combination of keywords and qualifiers
    already_searched, old_file_name, new_file_name = check_if_already_searched(keywords, qualifiers, files_targets)

    new_file = True

    # may want to move this to the check_if_already_searched function
    if already_searched:

        # Ask user if they want to append to the previous search
        if boolean_input("Previous search found. Do you want to append to the previous search? (y/n)", 3):
            # print("Appending to previous search: ", old_file_name)

            # rename the old file to the new file name
            os.rename(previous_searches_dir + "/" + old_file_name, previous_searches_dir + "/" + new_file_name)

            new_file = False

        else:
            # print("Writing new search to: ", new_file_name)
            new_file = True
    else:
        new_file


    f = None
    reader = None
    writer = None

    if new_file:
        f = open(previous_searches_dir + "/" + new_file_name, 'w')

        # write the search arguments to the file
        
        writer = csv.writer(f)
        reader = csv.reader(f)

        writer.writerow(csvify(['keywords','qualifiers','files_targets']))
        writer.writerow(csvify([keywords, qualifiers, files_targets]))
        writer.writerow(csvify([]))
        

        writer.writerow(csvify(csv_repo_header))

        # writer.writerow(csvify(['samuel','bingus','True', 'test.py', 'test']))

        
    else:
        f = open(previous_searches_dir + "/" + new_file_name)

        # read through the old file and add the repos to the checked_repos set

        reader = csv.reader(f)
        writer = csv.writer(f)

        # skip the first 4 rows
        for i in range(4):
            next(reader)

        for row in reader:
            if row:
                checked_repos.add(row[0]) # full_name

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

                    if repo.full_name not in checked_repos:
                        checked_repos.add(repo.full_name)
                        print(repo.full_name)

                    print("")

                    code_target_found, target_file_name, target = search_repo_contents(repo)

                    
                    writer.writerow(csvify([repo.full_name, repo.git_url, code_target_found, target_file_name, target]))


                remaining, request_limit = g.rate_limiting
                print("Remaining: %s, Limit: %s" % (remaining, request_limit))
                sleep(100)
                
        except KeyboardInterrupt:
            print("\nExiting early...")
            f.close()
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