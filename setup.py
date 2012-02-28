from setuptools import setup
readme_text = file('README.md', 'rb').read()

setup_args = dict(
    name                = 'ghtix',
    version             = '0.1.3',
    description         = 'A simple tool to summarize github issues across projects',
    author              = 'Matthew Perry',
    author_email        = 'perrygeo@gmail.com',
    url                 = 'http://gitub.com/perrygeo/ghtix',
    license             = 'New BSD License',
    keywords            = 'tickets issues tracker github project management',
    long_description    = readme_text,
    packages            = ['github_apiv3'],
    scripts             = ['ghtix.py'],
    install_requires    = ['pytz>=2010'],
    classifiers         = [
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Console'
        ],
    )

setup(**setup_args)
