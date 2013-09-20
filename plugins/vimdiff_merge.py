''' vim  merge option.  '''

from etc_cleaner.option import MergeOption


class VimMergeOption(MergeOption):
    ''' Merge using vimdiff (i. e., vi). '''

    option_id = 'vimdiff'
    unavailable_msg = 'Install package vim-enhanced to enable.'
    available_msg = 'Use vimdiff (i. e., vim) to merge config files.'

    cmd = 'vimdiff %(path0)s %(path1)s'

    def is_available(self):
        return self._which('vimdiff')

# vim: set expandtab ts=4 sw=4:
