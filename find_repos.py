#!/usr/bin/env python

from github import Github       #pip3 install pyGithub
from decouple import config     #pip3 install python-decouple
from time import sleep
import datetime
import re
import csv
import hashlib
import json

import os

results_dir = 'results'

csv_repo_header = ['full_name','URL','target_found','target_file_name','target']
csv_row_len = len(csv_repo_header)

def in_regex_list(file_name, patterns):
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


def check_if_already_searched(keywords, qualifiers, files_targets, dir_targets, max_file_size):

    # Default hash() function is randomly seeded, so we need to use a consistent one
    args_hash = hashlib.sha1((str(keywords) + str(qualifiers) + str(files_targets) + str(dir_targets) + str(max_file_size)).encode('utf-8')).hexdigest()[:12]

    new_file_name = datetime.datetime.now().strftime("%Y-%m-%d") + "_" + str(args_hash) + ".csv"

    if os.path.exists(results_dir):
        for old_file_name in os.listdir(results_dir):
            if old_file_name.endswith(".csv"):
                file_hash = old_file_name.split("_")[1].split(".")[0]

                if file_hash == str(args_hash):

                    return True, old_file_name, new_file_name

    else:
        os.mkdir(results_dir)
    
    return False, new_file_name, new_file_name

def csvify(row: list):

    row_len = len(row)
    
    if row_len > csv_row_len:
            raise Exception("Row is too long.")

    if row_len < csv_row_len:
        row.extend([''] * (csv_row_len - len(row)))

    return row

def search_repo_contents(repo, files_targets, dir_targets, max_file_size):

    contents = repo.get_contents("")

    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":

            folder_name_found, folder_name_pattern = in_regex_list(file_content.name, dir_targets)

            if folder_name_found:
                return True, file_content.name, folder_name_pattern


            contents.extend(repo.get_contents(file_content.path))
        else:

            file_name = file_content.path.split('/')[-1]
            # print(file_name)

            if file_content.size > max_file_size:
                continue

            # check if file is in files_targets (with regex)
            file_type_found , file_type_target = in_regex_list(file_name, files_targets.keys()) 

            if file_type_found:
                try:
                    code = str(file_content.decoded_content.decode('utf-8', 'ignore'))
                    
                    #check if code string contains any of the targets in target using regex
                    for target in files_targets[file_type_target]:
                        # print("Checking if target: ", target, " is in file: ", file_name)

                        if re.search(target, code):
                            print("Found Target: \"", target,"\"")
                            # print(code)
                            return True, file_name, target
                except AssertionError:
                    print("Error decoding file: ", file_content.path)
                
    return False, "", ""    #code_target_found, target_file_name, target 

def main():

    checked_repos = set()

    # get personal access token
    if not os.path.exists('.env'):
        raise Exception('Please create .env file with the following content:\n\nGITHUB_TOKEN=')

    github_oaut_token = config('GITHUB_TOKEN')

    g = Github(login_or_token=github_oaut_token)

    
    searches = None
    with open('searches.json') as json_file:
        searches = json.load(json_file)

    # START for each loop here. Iterate through each search
    # print(searches)

    for search in searches:
        print("Searching for: ", search['name'])

        keywords = search['keywords']
        qualifiers = search['qualifiers']
        dir_targets = search['dir_targets']
        files_targets = search['files_targets']
        max_file_size = search['max_file_size']


        # sort the args so that hashing is consistent
        keywords.sort() 
        qualifiers.sort()
        dir_targets.sort()
        for target in files_targets.values():
            target.sort()

        # check if we already searched for this combination of keywords and qualifiers
        already_searched, old_file_name, new_file_name = check_if_already_searched(keywords, qualifiers, files_targets, dir_targets, max_file_size)

        f = None
        reader = None
        writer = None

        if already_searched and boolean_input("Would you like to resume the search? (y/n) \n", 3):

            os.rename(results_dir + "/" + old_file_name, results_dir + "/" + new_file_name)

            with open(results_dir + "/" + new_file_name, 'r') as f:
                    
                reader = csv.reader(f)

                # skip the header
                next(reader)

                # skip the search arguments
                next(reader)

                # skip the empty line
                next(reader)

                # skip the header
                next(reader)

                for row in reader:
                    if row:
                        checked_repos.add(row[0]) # full_name

            f = open(results_dir + "/" + new_file_name, 'a')
            writer = csv.writer(f)

        else:
            f = open(results_dir + "/" + new_file_name, 'w', newline='')

            # write the search arguments to the file
            writer = csv.writer(f)

            writer.writerow(csvify(['keywords','qualifiers','files_targets','max_file_size']))
            writer.writerow(csvify([keywords, qualifiers, files_targets, max_file_size]))
            writer.writerow(csvify([]))

            writer.writerow(csvify(csv_repo_header))
            f = open(results_dir + "/" + new_file_name,'a' ,newline='')
            writer = csv.writer(f)

        query = ' '.join(keywords) + ' ' + ' '.join(qualifiers)
        print("querying:",query)

        repos = g.search_repositories(query=query)
        
        repos = list(repos)
        print("Found %s repos" % len(repos))

        try:

            for repo in repos:  

                remaining, request_limit = g.rate_limiting

                print("Remaining: %s, Limit: %s" % (remaining, request_limit))

                if remaining < 500:

                    reset_time = g.rate_limiting_resettime
                    # sleep until the reset time
                    print("Sleeping for %s seconds" % (reset_time - datetime.datetime.now().timestamp()))
                    sleep(reset_time - datetime.datetime.now().timestamp())

                if repo.full_name not in checked_repos:
                    checked_repos.add(repo.full_name)
                    print("")
                    print(repo.full_name)
                else:
                    continue

                code_target_found, target_file_name, target = search_repo_contents(repo,files_targets,dir_targets, max_file_size)
                writer.writerow(csvify([repo.full_name, repo.clone_url, code_target_found, target_file_name, target]))
            
        except KeyboardInterrupt:
            print("\nExiting early...")
            f.close()
            print(remaining , " github requests remaining")
            return False

if __name__ == '__main__':
    main()