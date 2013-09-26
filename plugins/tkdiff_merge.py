''' vim  merge option.  '''

from etc_cleaner.option import MergeOption


class TkdiffMergeOption(MergeOption):
    ''' Merge using tkdiff GUI tool. '''

    option_id = 'tkdiff'
    unavailable_msg = 'Install package tkcvs (on Fedora) to enable.'
    available_msg = 'Use tkdiff GUI tool to merge config files.'

    cmd = 'tkdiff %(path0)s %(path1)s'

    def is_available(self):
        return self._which('tkdiff')

# vim: set expandtab ts=4 sw=4:
