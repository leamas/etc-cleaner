''' kdiff3 merge option. '''

from etc_cleaner.option import MergeOption


class Kdiff3MergeOption(MergeOption):
    ''' Merge using kdiff3. '''

    option_id = 'kdiff3'
    unavailable_msg = 'Install package kdiff3 to enable.'
    available_msg = 'Use kdiff3(1) GUI tool to merge config files.'

    cmd = 'kdiff3 %(path0)s %(path1)s'

    def is_available(self):
        return self._which('kdiff3')

# vim: set expandtab ts=4 sw=4:
