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

            r = requests.get(issues_url % repo['full_name'])
            issues = r.json()
            milestones = {}
            for issue in issues:
                m = issue['milestone']
                if m:
                    if m['title'] not in milestones.keys():
                        milestones[m['title']] = {'due': m['due_on'], 'hours': {}}

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
                        milestones[m['title']]['hours'][assignee_login] += hours
                    else:
                        milestones[m['title']]['hours'][assignee_login] = hours
            project['milestones'] = milestones
            projects.append(project)
    return projects

if __name__ == '__main__':
    org = "Ecotrust"
    name_filter = ['land_owner_tools', 'madrona-priorities', 'nroc_boater_survey']
    projects = get_projects_overview(org, name_filter)
    print json.dumps(projects, indent=2)
