#!/usr/bin/env python
import pprint 
import dateutil.parser
import getpass
from github_apiv3 import client

try:
    from _secret import username, password
    from _secret import projects
except ImportError:
    username = getpass.getpass(prompt="Github username: ")
    password = getpass.getpass(prompt="Password for %s: " % username)
    projectname = getpass.getpass(prompt="Name of project:")
    projects = [
            (username, projectname),
    ]

c = client.Client(username=username, password=password)

for owner, project in projects:
    issues = []
    repo = client.Repo(c, owner, project)
    allissues = repo.issues()
    for x in allissues:
        if x['assignee'] and \
           x['assignee']['login'] == username and \
           x['state'] != 'closed':
            issues.append(x)

    print "--------------------------------"
    print project
    print

    for i in issues:
        if i['milestone']:
            title = i['title'] #, i['html_url']
            mtitle = i['milestone']['title']
            mdesc = i['milestone']['description']
            duedate = "??"
            if i['milestone']['due_on']:
                mdue = dateutil.parser.parse(i['milestone']['due_on'])
                duedate = "%d-%d-%d" % (mdue.month, mdue.day, mdue.year)
            print "\t%s (%s due on %s)" % (title, mtitle, duedate)

print "--------------------------------"
