''' Currently active options. '''

# pylint: disable=W0105

import inspect
import os
import os.path
import sys

from .option import MergeOption, DiffOption, ProfileOption
from .xdg_dirs import XdgDirs


ORPHANED_OWNER = 'orphaned'
LABEL_LINK = '<a href="%s"> %s </a>'
SITEDIR = '/etc/etc-cleaner'

MSG_UPDATED = '''File %(basename)s in %(dir)s has been updated by package
%(pkg)s, leaving a backup in %(saved)s.'''

MSG_PENDING = '''Package %(pkg)s has installed a new version of %(basename)s
called %(update)s in %(dir)s. %(basename)s has not been changed.'''

MSG_ORPHANED = '''Packages have been removed leaving stale configuration
files in %(dir)s.'''

DEFAULT_PROFILE = 'Fedora RPM (default)'

DEFAULT_MERGE_OPTION = 'meld'

DEFAULT_DIFF_OPTION = 'sdiff'

profiles_by_id = {}
''' Dict of all ProfileOptions keyed by their option_id. '''

merge_options_by_id = {}
''' Dict of all MergeOptions keyed by their option_id. '''

diff_options_by_id = {}
''' Dict of all DiffOptions keyed by their option_id. '''

profile = None
''' Currently selected profile. '''

merge_option = None
''' Currently selected merge option. '''

diff_option = None
''' Currently selected diff option. '''


def save():
    ''' Save values in config file. '''
    path = os.path.join(XdgDirs.app_configdir, 'options.rc')
    with open(path, 'w') as f:
        f.write('# Autogenerated...\n')
        f.write('%s: %s\n' % ('merge_option', merge_option.option_id))
        f.write('%s: %s\n' % ('diff_option', diff_option.option_id))
        f.write('%s: %s\n' % ('profile', profile.option_id))


def _fix_unavailable():
    ''' For unavailable options try to find an alternative. '''
    for option, options_by_id in [(profile, profiles_by_id),
                                  (merge_option, merge_options_by_id),
                                  (diff_option, diff_options_by_id)]:
        if not option.is_available:
            for try_opt in options_by_id.itervalues():
                if try_opt.is_available():
                    option = try_opt
                    break
            else:
                print "No available option!"


def _restore():
    ''' Restore values from config file. '''
    # pylint: disable=W0603
    global diff_option
    global merge_option
    global profile

    profile = profiles_by_id[DEFAULT_PROFILE]
    merge_option = merge_options_by_id[DEFAULT_MERGE_OPTION]
    diff_option = diff_options_by_id[DEFAULT_DIFF_OPTION]

    path = os.path.join(XdgDirs.app_configdir, 'options.rc')
    if not os.path.exists(path):
        return False
    with open(path) as f:
        lines = f.readlines()
    for l in lines:
        l = l.strip()
        if l.startswith('#'):
            continue
        elif not ':'  in l:
            continue
        else:
            try:
                key, value = l.split(':', 1)
                value = value.strip()
                if key == 'merge_option':
                    merge_option = merge_options_by_id[value]
                elif key == 'diff_option':
                    diff_option = diff_options_by_id[value]
                elif key == 'profile':
                    profile = profiles_by_id[value]
                else:
                    print "Bad config  key: " + key
            except IndexError:
                print "Bad config value: " + value


def _load_dir(dir_):
    ''' Load all plugins in dir_. '''
    # pylint: disable=W0612

    try:
        files = [p[:-3] for p in os.listdir(dir_) if p.endswith(".py")]
    except OSError:
        return
    sys.path.insert(0, dir_)
    for file_ in files:
        mod = __import__(file_)
        for name, class_ in inspect.getmembers(mod, inspect.isclass):
            bases = class_.__bases__
            if DiffOption in bases:
                diff_options_by_id[class_.option_id] = class_()
            elif MergeOption in bases:
                merge_options_by_id[class_.option_id] = class_()
            elif ProfileOption in bases:
                profiles_by_id[class_.option_id] = class_()
    sys.path.pop(0)


def _load_plugins():
    ''' Load all option plugins. '''
    here = os.path.dirname(__file__)
    _load_dir(os.path.join(here, 'plugins'))
    _load_dir(os.path.join(SITEDIR, 'plugins'))
    _load_dir(os.path.join(XdgDirs.app_datadir, 'plugins'))
    if not profiles_by_id:
        print "Configuration error: no plugins found"
        sys.exit(2)

_load_plugins()
_restore()
_fix_unavailable()


# vim: set expandtab ts=4 sw=4:
