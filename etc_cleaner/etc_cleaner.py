#!/usr/bin/env python
'''
Support poor admin when trying to keep config files up-to-date.

This is not a library. Nothing here is intended to be used by anything
besides the etc-cleaner script. Importing this module starts an
interactive process!

'''

import Queue
import multiprocessing
import os
import os.path
import subprocess
import sys

from glob import glob
from subprocess import check_output

from gi.repository import Gtk                    # pylint: disable=E0611
from gi.repository import GLib                   # pylint: disable=E0611
from gi.repository.Pango import FontDescription  # pylint: disable=F0401,E0611

from . import filechange
from . import prefix
from . import options
from . import run_sudo

profile = options.profile
XdgDirs = xdg_dirs.XdgDirs


class FileChange(object):
    ''' A changed configuration file. '''
    # pylint: disable=W0108

    def __init__(self, pkg_name, paths):
        self.package = pkg_name
        self.files = sorted(paths, key = lambda c: len(c))
        self.files = [f for f in self.files if os.path.isfile(f)]
        self.basepath = paths[0].replace(profile.backup_suffix, '')
        self.basepath = self.basepath.replace(profile.pending_suffix, '')
        self.basename = os.path.basename(self.basepath)
        self.dirname = os.path.dirname(self.basepath)
        self._cachedir = os.path.join(XdgDirs.app_cachedir, str(self))

    def setup(self):
        ''' Create cache dir and copy all files to it. '''
        if os.path.exists(self._cachedir):
            shutil.rmtree(self._cachedir)
        os.makedirs(self._cachedir)
        cmd = ['sudo', '-A', 'cp', '--preserve']
        cmd.extend(self.files)
        cmd.append(self._cachedir)
        check_output(cmd)
        check_output(['sudo', '-A', 'chown', '-R', str(os.getuid()),
                     self._cachedir])

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
            print "Cannot shuffle (not found): " + path

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


def sudo_setup():
    ''' Verify path to sudo_askpass and set environment. '''
    try:
        sudo_askpass = check_output(['which', 'rpmconf-sudo-askpass']).strip()
    except subprocess.CalledProcessError:
        print "Configuration error: can't find rpmconf-sudo-askpass"
        sys.exit(2)
    os.environ['SUDO_ASKPASS'] = sudo_askpass


def find_gladefile():
    ''' Locate the ui file in current dir or datadir. '''
    here = os.path.dirname(__file__)
    if os.path.exists(os.path.join(here, 'ui.glade')):
        return os.path.join(here, 'ui.glade')
    print "Installation error: Cannot find the ui.glade file"
    sys.exit(2)


def paths_equals(path1, path2):
    ''' Return if path1 has same content as path2. '''
    if not os.path.exists(path1) and not os.path.exists(path2):
        return True
    try:
        stat1 = os.stat(path1)
    except OSError:
        return False
    try:
        stat2 = os.stat(path2)
    except OSError:
        return False
    if stat1.st_mtime != stat2.st_mtime:
        return False
    if stat1.st_size != stat2.st_size:
        return False
    cmd = 'diff -q %s %s &>/dev/null' % (path1, path2)
    return subprocess.call(cmd, shell=True) == 0


def reconnect(widget, signal, handler, data):
    ''' Disconnect previous connection before doing connect.
    Beware: Stores the signal id as a widget attribute.
    '''
    signal_id_attr = signal + '_signal_id'
    if hasattr(widget, signal_id_attr):
        widget.disconnect(getattr(widget, signal_id_attr))
    id_ = widget.connect(signal, handler, data)
    setattr(widget, signal_id_attr, id_)


def get_change_by_name(do_when_done):
    ''' Run do_when_done  with a FileChange by str(change) needing
    a merge as argument.
    '''

    def process_paths(paths):
        ''' Given a list of paths, compute changes_by_name and
        invoke do_when_done(changes_by_name)
        '''
        if not isinstance(paths, list):
            paths = paths.split('\n')
        change_by_name = {}       # pylint: disable=W0621
        for path in [p for p in paths if p]:
            configpath = path
            for suffix in suffixes:
                configpath = configpath.replace(suffix, '')
            files = glob(configpath + '*')
            try:
                pkg_nvr = check_output(['rpm', '-qf', configpath],
                                         stderr=open('/dev/null', 'w')).strip()
                pkg = pkg_nvr.rsplit('-', 2)[0]
            except subprocess.CalledProcessError:
                pkg = options.ORPHANED_OWNER
            change = filechange.FileChange(pkg, files, builder)
            if str(change) in change_by_name and pkg == options.ORPHANED_OWNER:
                change_by_name[str(change)].files.extend(files)
            else:
                change_by_name[str(change)] = change
        do_when_done(change_by_name)

    suffixes = (options.profile.pending_suffix, options.profile.backup_suffix)
    cmd = 'find /etc ( -name *%s -o -name *%s )' % suffixes
    run_sudo.run_command(cmd.split(), process_paths, builder)


def get_labels(_change_by_name):
    ''' Given a list of FileChange, return list of labels. '''

    def get_label(markup, padding=10):
        ''' Left-justified, horizontal padded label. '''
        label = Gtk.Label('')
        label.set_markup(markup)
        label.set_justify(Gtk.Justification.LEFT)
        label.set_alignment(0.0, 0.5)
        label.set_padding(padding, 0)
        return label

    labels = []
    pkgs = list(set([c.package for c in _change_by_name.itervalues()]))
    for pkg in pkgs:
        label = get_label(pkg)
        labels.append(label)
        changes = \
            [c for c in _change_by_name.itervalues() if c.package == pkg]
        for c in changes:
            markup = options.LABEL_LINK % (str(c), c.basename)
            label = get_label(markup, 40)
            label.connect('activate-link', on_activate_link, _change_by_name)
            labels.append(label)
    return labels


def connect_signals():
    ''' Connect signals defined in glade. '''
    handlers = {
        "onDeleteWindow": Gtk.main_quit,
        "on_main_quit_clicked": Gtk.main_quit,
        "on_main_refresh_clicked": on_main_refresh_clicked,
        "on_all_done_ok_clicked": Gtk.main_quit,
        "on_merge_cancel_btn_clicked": on_merge_cancel_btn_clicked,
        "on_merge_window_delete_event": on_window_delete_event,
        "on_refresh_item_activate": on_refresh_item_activate,
        "on_quit_item_activate": Gtk.main_quit,
        "on_about_item_activate": on_about_item_activate,
        "on_manpage_item_activate": on_manpage_item_activate,
        "on_prefs_item_activate": on_prefs_item_activate,
        "on_profile_combo_changed": on_profile_combo_changed,
        "on_prefix_combo_changed": on_prefix_combo_changed,
    }
    builder.connect_signals(handlers)


#
# Windows
#
def rebuild_merge_window(change):
    ''' Handle user clicking change link. '''
    # pylint: disable=R0914,R0912
    # TBD!!!

    def set_info_label(change):
        ''' Compute the label explaing change status. '''
        if change.package == options.ORPHANED_OWNER:
            msg = options.MSG_ORPHANED % {'dir': change.dirname}
        elif change.backup:
            msg = options.MSG_UPDATED % {'basename': change.basename,
                                         'dir': change.dirname,
                                         'pkg': change.package,
                                         'saved': change.backup}
        elif change.update:
            msg = options.MSG_PENDING % {'basename': change.basename,
                                         'dir': change.dirname,
                                         'pkg': change.package,
                                         'update': change.update}
        else:
            msg = 'What?!'
        label = builder.get_object("merge_label")
        label.set_text(msg)

    def cell_alignment():
        ''' Right-attached expanded-fill alignment. '''
        a = Gtk.Alignment()
        a.set(1.0, 0.5, 1.0, 1.0)
        a.set_padding(0, 0, 40, 10)
        return a

    def add_header(grid, row, change):
        ''' Add the 'Use: ' or '0: ' line headerto grid. '''
        if change.name == options.ORPHANED_OWNER or row != 0:
            hdr = Gtk.Label('%d: ' % row)
        else:
            hdr = Gtk.Label('Use: ')
        hdr.set_alignment(0.0, 0.5)
        hdr.set_justify(Gtk.Justification.LEFT)
        grid.attach(hdr, 0, row, 1, 1)

    def add_filename(grid, filename, row):
        ''' Add filename to grid line. '''
        label = Gtk.Label(os.path.basename(filename))
        label.set_alignment(0.0, 0.5)
        label.set_justify(Gtk.Justification.LEFT)
        grid.attach(label, 1, row, 1, 1)

    def add_filedate(grid, path, row, refpath):
        ''' Add date or 'duplicate' to  grid line. '''

        def on_sudo_done(date_output):
            ''' sudo done, update date column. '''
            date = date_output.split()[5]
            label = Gtk.Label(date)
            align = cell_alignment()
            align.add(label)
            grid.attach(align, 2, row, 1, 1)
            builder.get_object('merge_window').show_all()

        if row != 0 and paths_equals(path, refpath):
            label = Gtk.Label('duplicate')
            align = cell_alignment()
            align.add(label)
            grid.attach(align, 2, row, 1, 1)
        else:
            cmd = "ls -l --time-style +%Y-%m-%d".split()
            cmd.append(path)
            run_sudo.run_command(cmd, on_sudo_done, builder)

    def add_delete_box(grid, row):
        ''' Add the delete checkbox to grid line. '''
        box = Gtk.CheckButton("Delete")
        box.set_active(True)
        align = cell_alignment()
        align.add(box)
        grid.attach(align, 3, row, 1, 1)

    def add_up_button(grid, row, change):
        ''' Add the ^-button to grid line. '''
        b = Gtk.Button()
        image = Gtk.Image()
        image.set_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.MENU)
        b.set_image(image)
        align = cell_alignment()
        align.add(b)
        grid.attach(align, 4, row, 1, 1)
        b.connect("clicked", on_merge_up_button_click, change)

    def create_grid_align():
        grid = Gtk.Grid()
        grid_align = builder.get_object("table_align")
        grid_align.get_child().destroy()
        grid_align.add(grid)
        return grid_align

    def update_grid(grid, change):
        ''' Complete grid with oneline for each file variant. '''
        for i in range(0, 6):
            grid.insert_column(i)
        grid.set_column_spacing(10)
        grid.set_hexpand(True)
        grid.set_halign(Gtk.Align.FILL)
        for row in range(0, len(change.files)):
            grid.insert_row(row)
            add_header(grid, row, change)
            add_filename(grid, change.get_cached(row), row)
            if row or change.package == options.ORPHANED_OWNER:
                add_delete_box(grid, row)
            if row and change.package != options.ORPHANED_OWNER:
                add_up_button(grid, row, change)
            add_filedate(grid, change.get_cached(row), row,
                         change.get_cached())
        grid.row_count = len(change.files)
        grid.column_count = 6

    set_info_label(change)
    buttons_align = builder.get_object("merge_buttons_align")
    info_hbox = builder.get_object("merge_info_hbox")
    grid_align = create_grid_align()
    top_vbox = builder.get_object("merge_top_vbox")

    for child in top_vbox.get_children():
        top_vbox.remove(child)

    top_vbox.pack_start(info_hbox, True, True, 10)
    top_vbox.pack_start(Gtk.HSeparator(), True, True, 10)
    top_vbox.pack_start(grid_align, True, True, 10)
    top_vbox.pack_start(buttons_align, True, True, 10)
    update_grid(grid_align.get_child(), change)

    btn = builder.get_object("merge_merge_btn")
    reconnect(btn, "clicked", on_merge_merge_btn_clicked, change)
    btn = builder.get_object("merge_diff_btn")
    reconnect(btn, "clicked", on_merge_diff_btn_clicked, change)
    btn = builder.get_object("merge_view_btn")
    reconnect(btn, "clicked", on_merge_view_btn_clicked, change)
    btn = builder.get_object("merge_ok_btn")
    reconnect(btn, "clicked", on_merge_ok_btn_clicked, change)
    w = builder.get_object('merge_window')
    w.set_title(options.profile.app + ': ' + change.basename)
    #w.show_all()
    return w


def get_main_window(builder, _change_by_name):      # pylint: disable=W0621
    ''' Build the main window with links to each change. '''

    labels = get_labels(_change_by_name)
    if not labels:
        return all_done_window()

    orphaned = [c for c in _change_by_name.itervalues()
                    if c.package == options.ORPHANED_OWNER]
    heading_label = builder.get_object("main_heading_lbl")
    txt = '%d files to merge, %d orphaned config files' % \
               (len(_change_by_name) - len(orphaned), len(orphaned))
    heading_label.set_text(txt)

    vbox = builder.get_object("pkg_vbox")
    for child in vbox.get_children():
        child.destroy()
    for l in labels:
        vbox.pack_start(l, True, True, 0)
    w = builder.get_object("Main")
    w.connect("delete-event", Gtk.main_quit)
    return w


def all_done_window():
    ''' Simple "No changes detected" dialog. '''
    w = builder.get_object("all_done_dialog")
    handlers = {
        "onDeleteWindow": Gtk.main_quit,
        "on_all_done_ok_clicked": Gtk.main_quit,
    }
    builder.connect_signals(handlers)
    return w


def size_warning_dialog(main_window, what):      # pylint: disable=W0621
    ''' Simple too large text warning dialog. '''
    msg = 'Warning: %s is too large, only showing first' \
          ' %d bytes.' % (what, options.profile.max_viewsize)
    dialog = Gtk.MessageDialog(main_window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT
                                   | Gtk.DialogFlags.MODAL,
                               Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.OK,
                               msg)
    dialog.run()
    dialog.destroy()


def show_some_text(text, change):
    ''' Read-only text display in a textview. '''
    textview = builder.get_object("view_textview")
    textview.modify_font(FontDescription("Monospace"))
    buf = textview.get_buffer()
    buf.set_text(text)
    w = builder.get_object('view_window')
    w.set_title(options.profile.app + ': ' + change.basename)
    w.connect('delete-event', on_window_delete_event)
    b = builder.get_object('view_ok_btn')
    b.connect('clicked', on_view_ok_btn_clicked, change)
    w.set_size_request(600, 600)
    return w


def rebuild_prefs_window():
    ''' Setup preferences window. '''

    def init_combo(combo_id, option, option_by_id, handler):
        ''' Setup combo with values from dict. Cannot fix renderer
        in glade-3 :(
        '''
        combo = builder.get_object(combo_id)
        store = combo.get_model()
        if store.get_iter_first():
            return
        store.append([option])
        for opt in option_by_id:
            if opt != option:
                store.append([opt])
        renderer = Gtk.CellRendererText()
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 0)
        combo.connect("changed", handler)
        combo.set_active(0)

    w = builder.get_object('prefs_window')
    w.connect('delete-event', on_prefs_window_delete_event)
    b = builder.get_object('prefs_ok_btn')
    b.connect('clicked', on_prefs_ok_btn_clicked)
    init_combo("profile_combo",
               options.profile.option_id,
               options.profiles_by_id,
               on_profile_combo_changed)
    init_combo("merge_combo",
               options.merge_option.option_id,
               options.merge_options_by_id,
               on_merge_combo_changed)
    init_combo("diff_combo",
               options.diff_option.option_id,
               options.diff_options_by_id,
               on_diff_combo_changed)
    init_combo("prefix_combo",
               prefix.prefix_option.option_id,
               prefix.prefix_options_by_id,
               on_prefix_combo_changed)
    w.set_size_request(600, 400)
    return w


#
# Callbacks
# pylint: disable=W0613
#
def on_activate_link(label, href, _change_by_name):
    ''' Handle user clicking change link. '''
    _change_by_name[href].setup()
    w = rebuild_merge_window(_change_by_name[href])
    if _change_by_name[href].package == options.ORPHANED_OWNER:
        builder.get_object("merge_merge_btn").hide()
        builder.get_object("merge_diff_btn").hide()
    return True


def on_window_delete_event(window, event):
    ''' generic window close event. '''
    window.hide()
    return True


def on_view_ok_btn_clicked(button, change):
    ''' OK button on view_some_text window. '''
    button.get_toplevel().hide()
    return True


def on_merge_merge_btn_clicked(button, change):
    ''' Merge button on merge window. Invoke external
    merge tool, rescan status when done.
    Parallell stuff: merge runs in a separate process. When
    done sends a message to the queue. In othe rend the queue
    is polled and acted upon when the message arrives.
    '''

    def cs(path):
        ''' Return a checksum for file at path. '''
        return check_output(['md5sum', path]).split()[0].strip()

    def timer_check():
        ''' Check if merge has completed, refresh if so. '''
        try:
            queue.get(False)
        except Queue.Empty:
            return True
        else:
            on_main_refresh_clicked()
            p.join()
            if old_cs != cs(path0):
                change.update_from_cache()
            change.rescan()
            w = rebuild_merge_window(change)
            w. show_all()
            return False

    def run_merge(cmd, queue):
        ''' Thread wrapper. '''
        rc = subprocess.call(cmd.split())
        queue.put(str(rc))

    path0 = change.get_cached(0)
    path1 = change.get_cached(1)
    old_cs = cs(path0)
    cmd = options.merge_option.cmd % {'path0': path0, 'path1': path1}
    queue = multiprocessing.Queue()
    GLib.timeout_add(500, timer_check)
    p = multiprocessing.Process(target = run_merge, args = (cmd, queue))
    p.start()
    builder.get_object('merge_window').hide()
    return True


def on_merge_diff_btn_clicked(button, change):
    ''' Diff button on merge window. '''
    path0 = change.get_cached()
    path1 = change.get_cached(1)
    cmd = options.diff_option.cmd % {'path0': path0, 'path1': path1}
    try:
        diff = check_output(cmd.split())
    except subprocess.CalledProcessError as e:
        diff = e.output
    if len(diff) > options.profile.max_viewsize:
        size_warning_dialog(button.get_toplevel(), 'Diff')
        diff = diff[:options.profile.max_viewsize]
    w = show_some_text(diff, change)
    w.show_all()
    return True


def on_merge_view_btn_clicked(button, change):
    ''' View button on merge window. '''
    path = change.get_cached()
    if os.stat(path).st_size > options.profile.max_viewsize:
        size_warning_dialog(button.get_toplevel(), path)
    with open(path) as f:
        text = f.read(options.profile.max_viewsize)
    w = show_some_text(text, change)
    w.show_all()
    return True


def on_merge_cancel_btn_clicked(button, change=None):
    ''' Cancel button on merge window. '''
    button.get_toplevel().hide()
    return True


def on_merge_ok_btn_clicked(button, change):
    ''' OK button on merge window. Remove files marked for deletion
    and update config file if user has changed cached copy.
    '''
    def do_when_cache_updated(dummy=None):
        ''' Cache ok, update ui and remove files.'''
        to_remove = []
        grid = builder.get_object('table_align').get_child()
        for row in range(0, grid.row_count):
            child = grid.get_child_at(3, row)
            if child:
                child = child.get_child()
            if child and child.get_active():
                basename = grid.get_child_at(1, row).get_text()
                path = os.path.join(change.dirname, basename)
                to_remove.append(path)
        if to_remove:
            cmd = ['rm']
            cmd.extend(to_remove)
            run_sudo.run_command(cmd, on_main_refresh_clicked, builder)
        button.get_toplevel().show_all()


    cached = change.get_cached()
    if not paths_equals(cached, change.basepath):
        cmd = ['cp', cached, change.basepath]
        run_sudo.run_command(cmd, do_when_cache_updated, builder)
    else:
        do_when_cache_updated()

def on_merge_up_button_click(button, change):
    ''' The ^-button on row. Swap this row and row above. '''
    grid = button.get_parent().get_parent()
    for row in range(1, grid.row_count):
        if grid.get_child_at(4, row).get_child() == button:
            basename = grid.get_child_at(1, row).get_text()
            break
    else:
        print "Cannot find button file"
    found = [f for f in change.files if f.endswith(basename)]
    if found:
        change.shuffle_up(found[0])
        rebuild_merge_window(change)
    else:
        print "No match for button basename: " + basename
    w = builder.get_object('merge_window')
    w.show_all()


def on_main_refresh_clicked(button=None):
    ''' Main refresh button: recompute pending changes. '''

    def do_with_change_by_name(change_by_name):
        ''' dummy docstring. This should be obvious. '''
        w = get_main_window(builder, change_by_name)
        w.show_all()

    get_change_by_name(do_with_change_by_name)


def on_refresh_item_activate(item):
    ''' File|Refresh menu item: same as button. '''
    on_main_refresh_clicked()


def on_about_item_activate(item):
    ''' Help|About menu item: run precanned about dialog. '''
    d = builder.get_object('about_window')
    d.run()
    d.hide()


def on_manpage_item_activate(item):
    ''' Help| manpage menu item. Open manpage on desktop. '''
    subprocess.call(['xdg-open', os.path.join(prefix.prefix_option.mandir,
                                             'etc-cleaner.1')])


def on_prefs_item_activate(item):
    ''' Edit|Peferences menu item: TBD. '''
    w = rebuild_prefs_window()
    w.connect('delete-event', lambda w, e: w.hide())
    b = builder.get_object('prefs_ok_btn')
    b.connect('clicked', lambda item: item.get_toplevel().hide())
    w.show_all()


def update_prefs_option(option, label_id, checkbox_id):
    ''' Update a prefs line from the selected option. '''
    label = builder.get_object(label_id)
    builder.get_object(checkbox_id).set_sensitive(False)
    if option.is_available():
        label.set_text(option.available_msg)
        builder.get_object(checkbox_id).set_active(True)
        return True
    else:
        label.set_text(option.unavailable_msg)
        builder.get_object(checkbox_id).set_active(False)
        return False


def on_profile_combo_changed(combo):
    ''' User selected a profile. '''
    tree_iter = combo.get_active_iter()
    if tree_iter is None:
        return True
    option_id = combo.get_model()[tree_iter][0]
    option = options.profiles_by_id[option_id]
    if update_prefs_option(option, "profile_info_label", 'profile_checkbox'):
        options.profile = option
    return True


def on_merge_combo_changed(combo):
    ''' User selected a merge tool preference. '''
    tree_iter = combo.get_active_iter()
    if tree_iter is None:
        return True
    option_id = combo.get_model()[tree_iter][0]
    option = options.merge_options_by_id[option_id]
    if update_prefs_option(option, "merge_info_label", 'merge_checkbox'):
        options.merge_option = option
    return True


def on_diff_combo_changed(combo):
    ''' user selected a diff setup preference. '''
    tree_iter = combo.get_active_iter()
    if tree_iter is None:
        return True
    option_id = combo.get_model()[tree_iter][0]
    option = options.diff_options_by_id[option_id]
    if update_prefs_option(option, "diff_info_label", 'diff_checkbox'):
        options.diff_option = option
    return True


def on_prefix_combo_changed(combo):
    ''' user selected a installation prefix preference. '''
    tree_iter = combo.get_active_iter()
    if tree_iter is None:
        return True
    option_id = combo.get_model()[tree_iter][0]
    option = prefix.prefix_options_by_id[option_id]
    if update_prefs_option(option, "prefix_info_label", 'prefix_checkbox'):
        prefix.prefix_option = option
    return True


def on_prefs_ok_btn_clicked(button):
    ''' 'OK' button on preferences window. '''
    options.save()
    prefix.save()
    return True


def on_prefs_window_delete_event(window, event):
    ''' Prefs window close event. '''
    options.save()
    prefix.save()
    window.hide()
    return True

def show_main(change_by_name):
    ''' Display main window and start main loop. '''
    main_window = get_main_window(builder, change_by_name)
    main_window.show_all()

builder = Gtk.Builder()
builder.add_from_file(find_gladefile())
connect_signals()
get_change_by_name(show_main)
Gtk.main()

# vim: set expandtab ts=4 sw=4:
