''' meld merge tool option.  '''

from etc_cleaner.option import MergeOption


class DiffuseMergeOption(MergeOption):
    '''  merge using diffuse. '''

    option_id = 'diffuse'
    unavailable_msg = 'Install package diffuse to enable.'
    available_msg = 'Use diffuse(1) GUI tool to merge config files.'

    cmd = 'diffuse %(path0)s %(path1)s'

    def is_available(self):
        return self._which('diffuse')

# vim: set expandtab ts=4 sw=4:
