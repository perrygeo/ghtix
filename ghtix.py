#!/usr/bin/env python
import os
import sys
import optparse
import dateutil.parser
from github_apiv3 import client

try:
    from _secret import username, password
    from _secret import projects
except ImportError:
    print 
    print open(os.path.join(os.path.dirname(__file__), 'secret.template')).read()  
    sys.exit()

def main():
    parser = optparse.OptionParser(
            usage="ghtix.py [options]")
    parser.add_option("-p", help="Sort by project name (default)", 
            action="store_true", dest="byproject", default=True)
    parser.add_option("-t", help="Sort by time / due date",
            action="store_false", dest="byproject", default=True)
    parser.add_option("-d", help="Output remaining days instead of due date",
            action="store_true", dest="usedays", default=False)
    (opts, args) = parser.parse_args()

    c = client.Client(username=username, password=password)

    for owner, project in projects:
        print "--------------------------------"
        print project
        print

        issues = []
        repo = client.Repo(c, owner, project)
        allissues = repo.issues()
        for x in allissues:
            if x['assignee'] and \
            x['assignee']['login'] == username and \
            x['state'] != 'closed':
                issues.append(x)

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

if __name__ == '__main__':
    main()
