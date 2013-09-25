''' /usr installation  '''
import os
import os.path

from . import xdg_dirs
from .option import AbstractOption


_CONFIG_FILE = os.path.join(xdg_dirs.XdgDirs.app_configdir, 'prefix.rc')

prefix_option = None
prefix_options_by_id = {}


def _get_default():
    ''' Return default prefix class. '''
    if os.path.exists(os.path.join(os.getcwd(), 'etc_cleaner')):
        return SourcePrefixOption
    elif os.path.exists(os.expanduser('~/.local/share/etc-cleaner')):
        return HomePrefixOption
    elif os.path.exists(os.expanduser('/usr/local/share/etc-cleaner')):
        return UsrLocalPrefixOption
    elif os.path.exists(os.expanduser('/usr/share/etc-cleaner')):
        return UsrPrefixOption
    else:
        return NoPrefixOption


def _restore():
    ''' Read active prefix from config file. '''
    # pylint: disable=W0603

    global prefix_option

    try:
        with open(_CONFIG_FILE) as f:
            prefix_id = f.read().split(':')[1].strip()
        prefix_option = prefix_options_by_id[prefix_id]
    except (OSError, IOError, IndexError, KeyError) as e:
        print "Cannot read prefix: (ignored) " + str(e)
        prefix_option = _get_default()


class PrefixOption(AbstractOption):
    ''' Installation prefix option. '''
    prefix = None
    mandir = None

    def is_available(self):
        raise NotImplementedError


class UsrPrefixOption(PrefixOption):
    ''' /usr installation prefix. '''

    option_id = '/usr'
    available_msg = 'Use installation in /usr, normally a package install.'
    unavailable_msg = 'Nothing is installed in /usr.'
    prefix = '/usr/share'
    mandir = '/usr/share/man/man1'
    datadir = '/usr/share/etc-cleaner'

    def is_available(self):
        return os.path.exists('/usr/share/etc-cleaner')


class UsrLocalPrefixOption(PrefixOption):
    ''' /usr/local installation prefix. '''

    option_id = '/usr/local'
    available_msg = 'Use installation in /usr/local.'
    unavailable_msg = 'Nothing is installed in /usr/local.'
    prefix = '/usr/local/share'
    mandir = '/usr/local/share/man/man1'
    datadir = '/usr/local/share/etc-cleaner'

    def is_available(self):
        return os.path.exists('/usr/local/share/etc-cleaner')


class HomePrefixOption(PrefixOption):
    ''' $HOME installation prefix. '''

    option_id = 'home'
    _prefix = os.path.expanduser('~/.local')
    available_msg = 'Use installation in ' + _prefix
    unavailable_msg = 'Nothing is installed in ' + _prefix
    prefix = _prefix
    mandir = os.path.expanduser('~/man/man1')
    datadir = os.path.expanduser('~/.local/share/etc-cleaner')

    def is_available(self):
        return os.path.exists(os.path.join(HomePrefixOption.prefix,
                                           'share/etc-cleaner'))


class SourcePrefixOption(PrefixOption):
    ''' Source installation prefix. '''

    option_id = 'source'
    available_msg = 'Use installation in current directory'
    unavailable_msg = 'Nothing is installed in: ' + os.getcwd()
    prefix = os.getcwd()
    mandir = os.getcwd()
    datadir = os.getcwd()

    def is_available(self):
        return os.path.exists(os.path.join(os.getcwd(), 'etc_cleaner'))


class NoPrefixOption(PrefixOption):
    '''No prefix selected option. '''

    option_id = 'no_prefix'
    available_msg = 'No installation found'

    def is_available(self):
        return True


def save():
    ''' Store active prefix in config file. '''
    with open(_CONFIG_FILE, 'w') as f:
        f.write('prefix: ' + prefix_option.option_id)


for class_ in [SourcePrefixOption,
               HomePrefixOption,
               UsrLocalPrefixOption,
               UsrPrefixOption]:
    prefix_options_by_id[class_.option_id] = class_()
_restore()


# vim: set expandtab ts=4 sw=4:
