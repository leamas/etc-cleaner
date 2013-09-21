''' Abstract option definitions.  '''
# pylint: disable=W0105,R0201,W0613

from subprocess import check_output, call


class AbstractOption(object):
    ''' Miminium generic Options interface. '''

    option_id = 'Unique ID'
    ''' Visual representation of this option. '''

    unavailable_msg = 'Install package to enable.'

    available_msg = 'Use tool to make make some work.'

    def is_available(self):
        ''' Return true if command tool is installed. '''
        return True

    def is_visible(self):
        ''' Return True if option is available on this platorm.'''
        return True

    @staticmethod
    def _which(cmd):
        ''' Test if cmd is available in PATH using which(1).'''
        with open('/dev/null', 'w') as null:
            rc = call(['which', cmd], stdout=null, stderr=null)
        return rc == 0


class ProfileOption(AbstractOption):
    ''' A possible alternative when selectinf profile. '''

    app = 'etc-cleaner'

    backup_suffix = None
    ''' For backup copy of updated file. '''

    pending_suffix = None
    ''' For new version installed without touching the original file. '''

    datadir = '/usr/share/etc-cleaner'
    ''' Where we look for e. g., ui.glade.'''

    mandir = '/usr/share/man/man1'
    ''' Where we look for our manpage.'''

    max_viewsize = 15000
    ''' Max # of bytes presented in "View" button. '''

    def cs(self, path):
        ''' Return a checksum for file at path. '''
        return check_output(['md5sum', path]).split()[0].strip()

    def get_owner(self, path):
        ''' Return package owning the given path.
        Parameters:
           - path: Absolute path to file.
        Returns:
           - Name of package owning path, or None.
        '''
        assert False, 'Abstract get_owner called'


class MergeOption(AbstractOption):
    ''' A possible alternative when choosing merge command. '''
    cmd = None


class DiffOption(AbstractOption):
    ''' A possible alternative when choosing merge command. '''
    cmd = None


# vim: set expandtab ts=4 sw=4:
