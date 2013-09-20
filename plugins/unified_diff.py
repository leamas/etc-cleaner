''' Unified diff diff option. '''

from etc_cleaner.option import DiffOption


class UnifiedDiffOption(DiffOption):
    ''' diff using diff -U. '''

    option_id = 'Unified diff'
    unavailable_msg = 'Install package diffutils to enable.'
    available_msg = 'Use diff -U  to compare config files.'

    cmd = 'diff -U -C2 %(path0)s %(path1)s'

    def is_available(self):
        return self._which('diff')


# vim: set expandtab ts=4 sw=4:
