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
    version = "0-@commit@",
    description = "Support sysadm while maintaning config files",
    author = "Alec Leamas",
    author_email = "leamas@nowhere.net",
    url = "whatever",
    packages = ['etc_cleaner'],
    data_files = [('applications', ['etc-cleaner.desktop']),
                  ('etc-cleaner', ['data/ui.glade']),
                  ('etc-cleaner/plugins',
                      list_files_in_dir('plugins', '.py')),
                  ('icons/hicolor/32x32/apps',
                     ['data/icons/32x32/etc-cleaner.png']),
                  ('icons/hicolor/22x22/apps',
                     ['data/icons/22x22/etc-cleaner.png']),
                  ('icons/hicolor/16x16/apps',
                     ['data/icons/16x16/etc-cleaner.png']),
    ],
    scripts = ["etc-cleaner", 'rpmconf-sudo-askpass'],
    long_description = open('README.md').read()
)
