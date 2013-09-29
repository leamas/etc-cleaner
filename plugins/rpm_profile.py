''' Default, RPM-based profile  '''

from subprocess  import check_output, CalledProcessError

from etc_cleaner.option import ProfileOption


class RpmProfileOption(ProfileOption):
    ''' Fedora setup, should work on any rpm-based distro. '''

    option_id = 'Fedora RPM (default)'
    unavailable_msg = 'This profile only works on rpm-based platforms.'
    available_msg = 'Use rpm-based default configuration.'
    backup_suffix = '.rpmsave'
    pending_suffix = '.rpmnew'
    replaced_suffix = '.rpmorig'
    man_viewer = 'yelp'
    #The xdg-open default should work, but doesn't on Fedora. This should
    #really be fixed upstream, 'man_viewer' shouldn't be in the profile. '''

    def get_owner(self, path):
        try:
            with open('/dev/null', 'w') as null:
                bytes_ = check_output(['rpm', '-qf', path], stderr=null)
                nvr = bytes_.decode(encoding='utf-8')
        except CalledProcessError:
            return None
        else:
            name = nvr.strip().rsplit('-', 2)[0]
            return name.split(':', 1)[1] if ':' in name else name

    def is_available(self):
        return self._which('rpm')


# vim: set expandtab ts=4 sw=4:
