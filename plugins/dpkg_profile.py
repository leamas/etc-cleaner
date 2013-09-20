''' default, RPM-based profile  '''

from subprocess  import check_output, CalledProcessError

from etc_cleaner.option import ProfileOption


class DpkgProfileOption(ProfileOption):
    ''' Dpkg setup, untested. '''

    option_id = 'Dpkg profile (untested)'
    unavailable_msg = 'This profile only works on dpkg-based platforms.'
    available_msg = 'Use dpkg-based configuration.'
    backup_suffix = '.dpkg-old'
    pending_suffix = '.dpkg-dist'
    max_viewsize = 15000
    datadir = '/usr/share/etc-cleaner'

    def get_owner(self, path):
        try:
            with open('/dev/null', 'w') as null:
                name = check_output(['dpkg', '-S', path], stderr=null)
        except CalledProcessError:
            return None
        else:
            return name.split(':', 1)[0] if ':' in name else name

    def is_available(self):
        return self._which('dpkg')


# vim: set expandtab ts=4 sw=4:
