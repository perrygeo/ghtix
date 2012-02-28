# GHTix - The Github Issue Tool

Right now, this is just a python script to grab your github issues from 
multiple projects and spit out your open tickets and due dates associated with milestones.

    $ ghtix.py -h
    Usage: ghtix.py [options]

    Options:
    -h, --help  show this help message and exit
    -p          Sort by project name (default)
    -t          Sort by time / due date
    -d          Output remaining days instead of due date
    -a          Include ALL issues even without milestone or due date
    -e          Show empty projects without any issues assigned
    -q          Quiet - no stderr messages, only issues list

Configure with a `~/.ghtix.json` file

    {
        "username": "myusername",
        "password": "mysupersecretpassword",
        "projects": [
        {"owner": "ecotrust", "name": "bioregion-discovery"},
        {"owner": "perrygeo", "name": "ghtix"}
        ]
    }

The default behavior showing due date and sorting by project

    $ ghtix.py
    fetching a_test_project tickets...
    fetching ghtix tickets...
    a_test_project       4-7-2012 (Define Analysis..) #7 Modeling Framework
    a_test_project      3-15-2012 (Software Scoping)  #40 Data model 
    ghtix               3-12-2012 (0.1 Release)       #6 Better way to configure
    ghtix               3-12-2012 (0.1 Release)       #5 PyPi page

Showing date delta (-d) and sorting by time (-t)

    $ ghtix.py -dt
    fetching a_test_project tickets...
    fetching ghtix tickets...
    ghtix                 14 days (0.1 Release)       #6 Better way to configure
    ghtix                 14 days (0.1 Release)       #5 PyPi page
    a_test_project        17 days (Software Scoping)  #40 Data model 
    a_test_project        40 days (Define Analysis..) #7 Modeling Framework

Setup is easy as py

    python setup.py install 

PyPi packaging on it's way
