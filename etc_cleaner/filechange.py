''' Change class, basically the model.  '''

import os
import os.path
import shutil

from glob import glob

from . import xdg_dirs
from . import options
from . import run_sudo

profile = options.profile
XdgDirs = xdg_dirs.XdgDirs


class FileChange(object):
    ''' A changed configuration file. Maintains a list of files with
    a common basename and different extension as created by package
    managers.
    rpm specifics:
      - rpmorig: file existed but was not owned by any package, saved
        in .rpmorig
      - .rpmnew: Existing file had local modifications, new file was
        installed as .rpmnew without touching original file.
      - .rpmsave: reflects a %config. The original filewas replaced by
        the new and saved in .rpmsave
    '''
    # pylint: disable=W0108

    def __init__(self, pkg_name, paths, builder):
        self.package = pkg_name
        self.files = sorted(paths, key = lambda c: len(c))
        self.files = [f for f in self.files if os.path.isfile(f)]
        self.basepath = paths[0].replace(profile.backup_suffix, '')
        self.basepath = self.basepath.replace(profile.pending_suffix, '')
        self.basepath = self.basepath.replace(profile.replaced_suffix, '')
        self.basename = os.path.basename(self.basepath)
        self.dirname = os.path.dirname(self.basepath)
        self.builder = builder
        self._cachedir = os.path.join(XdgDirs.app_cachedir, str(self))

    def setup(self):
        ''' Create cache dir and copy all files to it. '''

        def cb_copy_done(stdout):
            ''' Copy done, fix permissions. '''
            cmd = ['chown', '-R', str(os.getuid()), self._cachedir]
            run_sudo.run_command(cmd, lambda x: True, self.builder)

        if os.path.exists(self._cachedir):
            shutil.rmtree(self._cachedir)
        os.makedirs(self._cachedir)
        cmd = ['cp', '--preserve']
        cmd.extend(self.files)
        cmd.append(self._cachedir)
        run_sudo.run_command(cmd, cb_copy_done, self.builder)

    def update_from_cache(self):
        ''' Copy the modified value in cache to /etc target. '''
        cmd = ['sudo', '-A', 'cp']
        cmd.extend([self.get_cached(), self.basepath])
        run_sudo.run_command(cmd, lambda x: True, self.builder)

    def __str__(self):
        return self.package + ':' + self.basename

    def shuffle_up(self, path):
        ''' Exchange path and path-1 in files. '''
        for ix, file_  in enumerate(self.files):
            if file_ == path:
                assert ix > 0, "Attempt to shuffle up index 0: " + path
                tmp = self.files[ix - 1]
                self.files[ix - 1] = self.files[ix]
                self.files[ix] = tmp
                break
        else:
            print("Cannot shuffle (not found): " + path)

    def get_cached(self, index=0):
        ''' Return full path to cached copy of a files item. '''
        return os.path.join(self._cachedir,
                            os.path.basename(self.files[index]))

    def rescan(self):
        ''' Re-compute files to match what's on filesystem. '''
        matches = glob(self.basepath + '*')
        self.files = sorted(matches, key = lambda c: len(c))

    def find_suffix(self, suffix):
        ''' Find path in files ending with suffix, or 'None'. '''
        found = [f for f in self.files if f.endswith(suffix)]
        if found:
            return os.path.basename(found[0])
        else:
            return None

    def name(self):
        ''' Return package name or ORPHANED_OWNER if unowned. '''
        return self.package if self.package else options.ORPHANED_OWNER

    backup = property(lambda self: self.find_suffix(profile.backup_suffix))
    update = property(lambda self: self.find_suffix(profile.pending_suffix))
    replaced = \
        property(lambda self: self.find_suffix(profile.replaced_suffix))


# vim: set expandtab ts=4 sw=4:
