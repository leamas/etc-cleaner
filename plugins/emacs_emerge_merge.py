''' emacs-emerge merge option.  '''

from etc_cleaner.option import MergeOption


class EmacsEmergeMergeOption(MergeOption):
    ''' Merge using emacs emerge mode. '''

    option_id = 'emacs-emerge'
    unavailable_msg = 'Install package emacs to enable.'
    available_msg = 'Use emacs emerge mode to merge config files.'
    cmd = ' emacs -Q -f emerge-files-command %(path0)s %(path1)s'

    def is_available(self):
        return self._which('emacs')

# vim: set expandtab ts=4 sw=4:
