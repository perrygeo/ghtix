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
import dateutil.parser
from datetime import datetime
from utils import parse_hours_from_title
import requests_cache

requests_cache.install_cache('ghtix_cache', backend='sqlite', expire_after=900) # 15 min

repos_url = "https://api.github.com/orgs/%s/repos?per_page=100"  # max 100 repos
issues_url = "https://api.github.com/repos/%s/issues?state=open"


def get_projects_overview(org, name_filter=None):
    r = requests.get(repos_url % org)
    repos = r.json()
    if r.status_code > 299:
        raise Exception("Request failed with status code: %d. \n\n %r" % (
            r.status_code, r.headers))

    projects = []
    for repo in repos:
        if not name_filter or repo['name'] in name_filter:
            project = {'name': repo['name']}
            sys.stderr.write("------ %s" % repo['name'])
            sys.stderr.write("\n")

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

            from dateutil.relativedelta import relativedelta
            the_distance_future = get_nice_date(str(datetime.today() + relativedelta(years=10)))
            future_title = "Future Release"

            for issue in issues:
                m = issue['milestone']
                if m:
                    if m['title'] not in [x['name'] for x in milestones]:
                        milestone = {'name': m['title'],
                                     'due': get_nice_date(m['due_on']), 'hours': {}, 'tasks': {}}
                        milestones.append(milestone)
                    else:
                        milestone = [
                            x for x in milestones if x['name'] == m['title']][0]
                else:
                    # Assign a fictional "Future Release" milestone 
                    if future_title not in [x['name'] for x in milestones]:
                        milestone = {'name': future_title,
                                     'due': the_distance_future, 'hours': {}, 'tasks': {}}
                        milestones.append(milestone)
                    else:
                        milestone = [
                            x for x in milestones if x['name'] == future_title][0]

                assignee = issue['assignee']
                try:
                    assignee_login = assignee['login']
                except (KeyError, TypeError):
                    assignee_login = "unassigned"

                hours = parse_hours_from_title(issue['title'])

                issue_desc = {'title': issue['title'], "url":
                              issue['html_url'], "number": issue['number']}

                if assignee_login in milestone['hours']:
                    milestone['tasks'][assignee_login].append(issue_desc)
                    milestone['hours'][assignee_login] += hours
                else:
                    milestone['tasks'][assignee_login] = [issue_desc]
                    milestone['hours'][assignee_login] = hours

            project['milestones'] = milestones
            projects.append(project)
    return projects


def get_weeks_diff(ts):
    dt = dateutil.parser.parse(ts)
    future = dt.replace(tzinfo=None)
    now = datetime.now()
    diff = future - now
    return diff.days / 7.0


def get_nice_date(ts):
    dt = dateutil.parser.parse(ts)
    date = dt.replace(tzinfo=None)
    return date.strftime("%B %d %Y")


def flatten_projects(projects):
    """
    Creates a flat table structure out of the data
    """
    # get a list of all developers
    devs = []
    devs_mod = []
    for project in projects:
        for milestone in project['milestones']:
            for dev in milestone['hours'].keys():
                if dev not in devs:
                    devs.append(dev)
                    devs_mod.append(dev.replace("atecotrustdotorg", ""))

    devs_mod = [x + " (wks)" for x in devs_mod]
    header = ["project", "milestone", "due", "devweeks",
              "cumul. devweeks", "weeks away", "project load", "cumul. load"]
    header.extend(devs_mod)
    print "\t".join([str(x) for x in header])

    datarray = []
    # datarray.append(header)

    for project in projects:
        p = project['name']
        for milestone in project['milestones']:
            m = milestone['name']
            due = milestone['due']
            if due:
                d = get_nice_date(due)  # due.split("T")[0]
            else:
                d = "Dec 31 2999"  # the distant future
            ts = [0] * len(devs)
            for dev, hours in milestone['hours'].items():
                # convert from hours to weeks
                ts[devs.index(dev)] = hours / 40.0
            row = [p, m, d]

            devweeks = sum(ts)
            row.append("%.1f" % devweeks)

            try:
                weeks = get_weeks_diff(due)
            except AttributeError:
                weeks = -999

            if weeks <= 0:
                row.append("")
                row.append("")
            else:
                devload = devweeks / weeks
                row.append("%.1f" % weeks)
                row.append("%.2f" % devload)

            row.extend([round(t, 1) for t in ts])
            datarray.append(row)

    data1 = sorted(datarray, key=lambda x: dateutil.parser.parse(x[2]))
    data = []
    cdevweeks = 0
    for d in data1:
        try:
            cdevweeks += float(d[3])
            cdevload = cdevweeks / float(d[4])
            cdevload = "%.2f" % cdevload
        except ValueError:
            cdevload = ''

        d.insert(4, cdevweeks)  # cumulative devweeks
        d.insert(7, cdevload)  # cumulative devload
        data.append(d)

    for row in data:
        print "\t".join([str(x) for x in row])

    return header, data


if __name__ == '__main__':
    org = "Ecotrust"
    name_filter = ['land_owner_tools', 'growth-yield-batch', 'harvest-scheduler', 
        'madrona-priorities', 'madrona', 'locus', 'ak-logbook']

    #try:
    projects = get_projects_overview(org, name_filter)
    with open('ksdev/ksdev.json', 'w') as kfh:
        kfh.write(json.dumps(projects, indent=2))
    #except:
    #    print "WARNING: using cached json since our request didn't go through"
    #    with open('ksdev/ksdev.json', 'r') as fh:
    #        projects = json.loads(fh.read())

    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('.'))

    with open('ksdev/tickets.html', 'w') as htmlfh:
        template = env.get_template('assigned.html')
        htmlfh.write(template.render(projects=projects, now=datetime.now()))

    header, data = flatten_projects(projects)
    with open('ksdev/index.html', 'w') as htmlfh:
        template = env.get_template('template_table.html')
        htmlfh.write(template.render(header=header, rows=data, now=datetime.now()))
