''' Use meld as merge tool  '''

from etc_cleaner.option import MergeOption


class MeldMergeOption(MergeOption):
    ''' Default merge using meld. '''

    option_id = 'meld'
    unavailable_msg = 'Install package meld to enable.'
    available_msg = 'Use meld(1) GUI tool to merge config files.'

    cmd = 'meld %(path0)s %(path1)s'

    def is_available(self):
        return self._which('meld')

# vim: set expandtab ts=4 sw=4:
