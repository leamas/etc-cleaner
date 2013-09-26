''' xxdiff  merge option.  '''

from etc_cleaner.option import MergeOption


class XxdiffMergeOption(MergeOption):
    ''' Merge using xxdiff GUI tool. '''

    option_id = 'xxdiff'
    unavailable_msg = 'Install package xxdiff (on Fedora) to enable.'
    available_msg = 'Use xxdiff GUI tool to merge config files.'

    cmd = 'xxdiff %(path0)s %(path1)s'

    def is_available(self):
        return self._which('xxdiff')

# vim: set expandtab ts=4 sw=4:
