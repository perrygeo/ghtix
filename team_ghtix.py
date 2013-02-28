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
    if r.status_code > 299:
        raise Exception("Request failed with status code: %d. \n\n %r" % (r.status_code, r.headers))

    projects = []
    for repo in repos:
        sys.exit()
        if not name_filter or repo['name'] in name_filter:
            project = {'name': repo['name']}
            sys.stderr.write("------ %s" % repo['name'])
            sys.stderr.write("\n")

            url = issues_url % repo['full_name']
            res = requests.get(url)
            issues = res.json()

            if res.headers['link']:
                page = 1
                while "next" in res.headers['link']:
                    page += 1
                    paged_url = url + "&page=%d" % page
                    res = requests.get(paged_url)
                    issues.extend(res.json())

            milestones = []
            for issue in issues:
                m = issue['milestone']
                if m:
                    if m['title'] not in [x['name'] for x in milestones]:
                        milestone = {'name': m['title'], 'due': m['due_on'], 'hours': {}, 'tasks': {}}
                        milestones.append(milestone)
                    else: 
                        milestone = [x for x in milestones if x['name'] == m['title']][0]

                    assignee = issue['assignee']
                    try:
                        assignee_login = assignee['login']
                    except (KeyError, TypeError):
                        assignee_login = "unassigned"

                    # [1hr] or [ 8 weeks ] but not [8.2 days] and not [8 weeks approx]
                    regex = re.compile(".*\[\s*(\d+)\s*(\w+)\s*\]") 
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
                    issue_desc = {'title': issue['title'], "url": issue['html_url'], "number": issue['number']}

                    if assignee_login in milestone['hours']:
                        milestone['tasks'][assignee_login].append(issue_desc)
                        milestone['hours'][assignee_login] += hours
                    else:
                        milestone['tasks'][assignee_login] = [issue_desc]
                        milestone['hours'][assignee_login] = hours
                else:
                    sys.stderr.write("No milestone for issue `%s`" % issue['title'])
                    sys.stderr.write("\n")
            project['milestones'] = milestones
            projects.append(project)
    return projects

if __name__ == '__main__':
    org = "Ecotrust"
    name_filter = ['land_owner_tools', 'madrona-priorities', 'growth-yield-batch', 'madrona']

    try:
        projects = get_projects_overview(org, name_filter)
        with open('ksdev.json','w') as kfh:
            kfh.write(json.dumps(projects, indent=2))
    except:
        with open('ksdev.json','r') as fh:
            projects = json.loads(fh.read())

    with open('ksdev.html','w') as htmlfh:
        from jinja2 import Environment, FileSystemLoader
        env = Environment(loader=FileSystemLoader('.'))
        template = env.get_template('template.html')
        htmlfh.write(template.render(projects=projects))


