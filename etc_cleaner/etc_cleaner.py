''' Main windows and setup. '''

import os
import os.path
import subprocess
import sys

from glob import glob
from subprocess import check_output

from gi.repository import Gtk                    # pylint: disable=E0611

from . import filechange
from . import merge
from . import options
from . import prefix
from . import prefs
from . import run_sudo
from . import xdg_dirs


def _find_gladefile():
    ''' Locate the ui file in current dir. '''
    here = os.path.dirname(__file__)
    if os.path.exists(os.path.join(here, 'ui.glade')):
        return os.path.join(here, 'ui.glade')
    print("Installation error: Cannot find the ui.glade file")
    sys.exit(2)


def _find_linked_file(file_):
    ''' Locate the file in current dir. '''
    here = os.path.dirname(__file__)
    if os.path.exists(os.path.join(here, file_)):
        return os.path.join(here, file_)
    print("Installation error: Cannot find: " + file_)
    sys.exit(2)


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
                bytes_ = check_output(['rpm', '-qf', configpath],
                                         stderr=open('/dev/null', 'w')).strip()
                pkg_nvr = bytes_.decode(encoding='utf-8')
                pkg = pkg_nvr.rsplit('-', 2)[0]
            except subprocess.CalledProcessError:
                pkg = options.ORPHANED_OWNER
            change = filechange.FileChange(pkg, files, builder)
            if str(change) in change_by_name and pkg == options.ORPHANED_OWNER:
                change_by_name[str(change)].files.extend(files)
            else:
                change_by_name[str(change)] = change
        do_when_done(change_by_name)

    suffixes = (options.profile.pending_suffix,
                options.profile.backup_suffix,
                options.profile.replaced_suffix)
    cmd = 'find /etc ( -name *%s -o -name *%s -o -name *%s )' % suffixes
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
    pkgs = list(set([c.package for c in _change_by_name.values()]))
    for pkg in pkgs:
        label = get_label(pkg)
        labels.append(label)
        changes = \
            [c for c in _change_by_name.values() if c.package == pkg]
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
        "on_refresh_item_activate": on_refresh_item_activate,
        "on_quit_item_activate": Gtk.main_quit,
        "on_about_item_activate": on_about_item_activate,
        "on_manpage_item_activate": on_manpage_item_activate,
        "on_prefs_item_activate": on_prefs_item_activate,
    }
    builder.connect_signals(handlers)


#
# Windows
#
def get_main_window(builder, _change_by_name):      # pylint: disable=W0621
    ''' Build the main window with links to each change. '''

    w = builder.get_object("Main")
    labels = get_labels(_change_by_name)
    if not labels:
        all_done_dialog(w)

    orphaned = [c for c in _change_by_name.values()
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
    w.connect("delete-event", Gtk.main_quit)
    return w


def all_done_dialog(main_window):      # pylint: disable=W0621
    ''' Simple "All done" info dialog. '''
    msg = 'No unmerged changes found'
    dialog = Gtk.MessageDialog(main_window,
                               Gtk.DialogFlags.DESTROY_WITH_PARENT
                                   | Gtk.DialogFlags.MODAL,
                               Gtk.MessageType.INFO,
                               Gtk.ButtonsType.OK,
                               msg)
    dialog.run()
    dialog.destroy()


#
# Callbacks
# pylint: disable=W0613
#
def on_activate_link(label, href, _change_by_name):
    ''' Handle user clicking change link. '''
    _change_by_name[href].setup()
    merge.rebuild_window(_change_by_name[href],
                         builder,
                         on_main_refresh_clicked)
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
    path = os.path.join(prefix.prefix_option.mandir,
                        find_linked_file('etc-cleaner.8'))
    subprocess.call(['xdg-open', path])


def on_prefs_item_activate(item):
    ''' Edit|Peferences menu item: TBD. '''
    w = prefs.rebuild_window(builder)
    w.connect('delete-event', lambda w, e: w.hide())
    b = builder.get_object('prefs_ok_btn')
    b.connect('clicked', lambda item: item.get_toplevel().hide())
    w.show_all()


def show_main(change_by_name):
    ''' Display main window and start main loop. '''
    main_window = get_main_window(builder, change_by_name)
    main_window.show_all()

builder = Gtk.Builder()
builder.add_from_file(find_linked_file('ui.glade'))
connect_signals()
get_change_by_name(show_main)
Gtk.main()

# vim: set expandtab ts=4 sw=4:
