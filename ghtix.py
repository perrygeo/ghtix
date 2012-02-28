#!/usr/bin/env python
import os
import sys
import optparse
import json
import dateutil.parser
import datetime
import pytz
from github_apiv3 import client
from operator import itemgetter

def msg(txt, opts):
    if not opts.quiet:
        sys.stderr.write(txt + "\n")

def main():
    utc = pytz.UTC
    farfaraway = datetime.datetime(3000,1,15,8,15,12,0, utc)

    parser = optparse.OptionParser(
            usage="ghtix.py [options]")
    parser.add_option("-p", help="Sort by project name (default)", 
            action="store_true", dest="byproject", default=True)
    parser.add_option("-t", help="Sort by time / due date",
            action="store_false", dest="byproject", default=True)
    parser.add_option("-d", help="Output remaining days instead of due date",
            action="store_true", dest="usedays", default=False)
    parser.add_option("-a", help="Include ALL issues even without milestone or due date",
            action="store_true", dest="allissues", default=False)
    parser.add_option("-e", help="Show empty projects without any issues assigned",
            action="store_true", dest="showempty", default=False)
    parser.add_option("-q", help="Quiet - no stderr messages, only issues list",
            action="store_true", dest="quiet", default=False)
    (opts, args) = parser.parse_args()

    try:
        jsoncfg = os.path.join(os.path.expanduser("~"), '.ghtix.json')
        jsontxt = open(jsoncfg,'r').read()
        cfg = json.loads(jsontxt)
        username = cfg['username']
        password = cfg['password']
        projects = [ (x['owner'], x['name']) for x in cfg['projects'] ]
    except (IOError,):
        print 
        print open(os.path.join(os.path.dirname(__file__), 'template.ghtix.json')).read()  
        sys.exit()

    c = client.Client(username=username, password=password)

    issues = []
    proj_width = 0

    for owner, project in projects:
        msg("fetching %s tickets..." % project, opts)
        if len(project) > proj_width:
            proj_width = len(project)
        repo = client.Repo(c, owner, project)
        project_issues = repo.issues()
        empty = True
        for i in project_issues:
            if i['assignee'] and \
            i['assignee']['login'] == username and \
            i['state'] != 'closed':
                empty = False
                i['project'] = project
                i['empty'] = False
                try:
                    dt = dateutil.parser.parse(i['milestone']['due_on'])
                    # d.tzinfo is not None but d.tzinfo.utcoffset(d) returns None
                    if dt.tzinfo is None:
                        dt = utc.localize(dt)
                    i['due_sortable'] = dt
                except TypeError:
                    i['due_sortable'] = farfaraway
                    
                issues.append(i)
        if empty:
            issues.append( { 'project': project, 
                'empty': True, 
                'due_sortable': farfaraway
                }
            )

    if opts.byproject:
        # sort by project name
        issues = sorted(issues, key=itemgetter('project')) 
    else:
        # sort by due date 
        issues = sorted(issues, key=itemgetter('due_sortable')) 
    
    for i in issues:
        if i['empty']:
            if opts.showempty:
                print i['project'].ljust(proj_width), "---------- None"
            continue

        title = i['title']
        number = i['number']
        project = i['project']
        if len(project) > 17:
            project = project[:15] + ".."
        project = "%s " % project 
        if i['milestone'] or opts.allissues:
            try:
                mtitle = i['milestone']['title']
                if len(mtitle) > 17:
                    mtitle = mtitle[:15] + ".."
                mtitle = "(%s) " % mtitle

            except:
                mtitle = ""

            try:
                mdue = dateutil.parser.parse(i['milestone']['due_on'])
                if opts.usedays:
                    togo = mdue - datetime.datetime.now(utc)
                    duedate = "%d days" % togo.days
                else:
                    duedate = "%d-%d-%d" % (mdue.month, mdue.day, mdue.year)
            except: 
                duedate = ""
                
            print "%s %s %s#%d %s" % (project.ljust(18), 
                    duedate.rjust(10), mtitle.ljust(20), number, title)

if __name__ == '__main__':
    main()
