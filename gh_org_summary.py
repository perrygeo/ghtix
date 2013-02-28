#!/usr/bin/env python
"""
Github Organization Summary 
Simple script to summarize github issues across projects

Currently, the estimated time for each issue is either assumed to be 8 hours
or you can put the time in brackets in the title:

    `Update this app to do something cool [6 hours]`

Requirements: pip install requests  

See the __main__ block for usage.

Example output:
[
  {
    "milestones": {
      "Juniper Beta": {
        "hours": {
          "perrygeo": 24,
          "unassigned": 8
        },
        "due": "2013-03-31T07:00:00Z"
      },
      "USFW 2.0 alpha": {
        "hours": {
          "perrygeo": 56
        },
        "due": "2013-04-30T07:00:00Z"
      }
    },
    "name": "madrona-priorities"
  },
  ....
]
"""
import requests
import json
import re
import sys

repos_url = "https://api.github.com/orgs/%s/repos"
issues_url = "https://api.github.com/repos/%s/issues?state=open"

convert_to_hours = {
    'hours': 1,
    'hour': 1,
    'hrs': 1,
    'hr': 1,
    'days': 8,
    'day': 8,
    'week': 40,
    'weeks': 40,
    'wk': 40,
    'wks': 40,
}


def get_projects_overview(org, name_filter=None):
    r = requests.get(repos_url % org)
    repos = r.json()
    projects = []
    for repo in repos:
        if not name_filter or repo['name'] in name_filter:
            project = {'name': repo['name']}
            sys.stderr.write("------ %s" % repo['name'])
            sys.stderr.write("\n")

            url = issues_url % repo['full_name']
            res = requests.get(url)
            issues = res.json()

            page = 1
            while "next" in res.headers['link']:
                page += 1
                paged_url = url + "&page=%d" % page
                res = requests.get(paged_url)
                issues.extend(res.json())

            print len(issues)
            milestones = {}
            for issue in issues:
                m = issue['milestone']
                if "Server" in issue['title']:
                    print "#####################################################################"
                if m:
                    if m['title'] not in milestones.keys():
                        milestones[m['title']] = {'due': m['due_on'], 'hours': {}, 'tasks': {}}

                    assignee = issue['assignee']
                    try:
                        assignee_login = assignee['login']
                    except (KeyError, TypeError):
                        assignee_login = "unassigned"

                    regex = re.compile(".*\[\s*(\d+)\s*(\w+)\s*\]")  # [1hr] or [ 8 weeks ] but not [8.2 days] and not [8 weeks approx]
                    r = regex.search(issue['title'])
                    if r:
                        val, units = r.groups()
                        val = int(val)
                    else:
                        sys.stderr.write("Warning:: assuming `%s` takes 8 hours. If not, add time to the title (like '[3 days]')" % issue['title'])
                        sys.stderr.write("\n")
                        val = 8
                        units = "hours"

                    hours = val * convert_to_hours[units]

                    if assignee_login in milestones[m['title']]['hours']:
                        milestones[m['title']]['tasks'][assignee_login] += 1
                        milestones[m['title']]['hours'][assignee_login] += hours
                    else:
                        milestones[m['title']]['tasks'][assignee_login] = 1
                        milestones[m['title']]['hours'][assignee_login] = hours
                else:
                    print "NO MILESTONE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
            project['milestones'] = milestones
            projects.append(project)
    return projects

if __name__ == '__main__':
    org = "Ecotrust"
    name_filter = ['land_owner_tools', ] #'madrona-priorities', 'growth-yield-batch']
    projects = get_projects_overview(org, name_filter)
    print json.dumps(projects, indent=2)
