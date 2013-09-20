''' sdiff diff option. '''

from etc_cleaner.option import DiffOption


class SdiffDiffOption(DiffOption):
    ''' Default diff using sdiff. '''

    option_id = 'sdiff'
    unavailable_msg = 'Install package diffutils to enable.'
    available_msg = 'Use sdiff(1) to compare config files side ny side.'

    cmd = 'sdiff %(path0)s %(path1)s'

    def is_available(self):
        return self._which('sdiff')

# vim: set expandtab ts=4 sw=4:
