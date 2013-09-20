''' Weeeell, we need a docstring. '''
from distutils.core import setup

import os
import os.path
import sys

HERE = os.path.dirname(os.path.realpath(sys.argv[0]))


def list_files_in_dir(dir_, extension):
    ''' Return recursive listing of all regular files under dir. '''
    file_list = []
    for filename in os.listdir(os.path.join(HERE, dir_)):
        if filename.endswith(extension):
            file_list.append(os.path.join(dir_, filename))
    return file_list


setup(name = "etc-cleaner",
    version = "0",
    description = "Support sysadm while maintaning config files",
    author = "Alec Leamas",
    author_email = "leamas@nowhere.net",
    url = "whatever",
    packages = ['etc_cleaner'],
    data_files = [('/usr/share/applications/', ['etc-cleaner.desktop']),
                  ('/usr/share/etc-cleaner/plugins',
                      list_files_in_dir('plugins', '.py')),
                  ('/usr/share/icons/hicolor/32x32',
                     ['data/icons/32x32/etc-cleaner.png']),
                  ('/usr/share/icons/hicolor/22x22',
                     ['data/icons/22x22/etc-cleaner.png']),
                  ('/usr/share/icons/hicolor/16x16',
                     ['data/icons/16x16/etc-cleaner.png']),
    ],

    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    #package_data = {'etc-cleaner' : ['data', '/data/icons/32x32/*.png',
    #                                 'etc-cleaner.desktop'] },
    #package_data = {'': ['data', 'etc-cleaner.desktop']},
    #'runner' is in the root.
    scripts = ["etc-cleaner"],
    long_description = open('README.md').read()
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []
)
