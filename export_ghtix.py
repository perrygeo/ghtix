#!/usr/bin/env python
import requests
import json
import re
import sys
import dateutil.parser
from datetime import datetime
import requests_cache
from utils import parse_hours_from_title

requests_cache.install_cache('ghtix_cache', backend='sqlite', expire_after=900) # 15 min


repos_url = "https://api.github.com/orgs/%s/repos?per_page=100"  # max 100 repos
issues_url = "https://api.github.com/repos/%s/issues?state=open"


def print_issue_list(org, name_filter=None):
    r = requests.get(repos_url % org)
    repos = r.json()
    if r.status_code > 299:
        raise Exception("Request failed with status code: %d. \n\n %r" % (
            r.status_code, r.headers))

    print ",".join(["repo_name", "issue", "labels", "hours", "milestone",]) 
    for repo in repos:
        if not name_filter or repo['name'] in name_filter:
            repo_name = repo['name']

            url = issues_url % repo['full_name']
            res = requests.get(url)
            issues = res.json()

            if 'link' in res.headers.keys():
                page = 1
                while "next" in res.headers['link']:
                    page += 1
                    paged_url = url + "&page=%d" % page
                    res = requests.get(paged_url)
                    issues.extend(res.json())

            milestones = []
            fields = ['title', 'description', ]
            for issue in issues:
                labels = ','.join([x['name'] for x in issue['labels']])
                m = issue['milestone']
                if m:
                    milestone = m['title']
                else:
                    milestone = ""
                hours = parse_hours_from_title(issue['title'])
                print ",".join([repo_name, issue['title'].replace(","," "), labels.replace(",","/"), str(hours), milestone,]) 



if __name__ == '__main__':
    org = "Ecotrust"
    name_filter = ['land_owner_tools', 'growth-yield-batch', 'harvest-scheduler']
    print_issue_list(org, name_filter)
