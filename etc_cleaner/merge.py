''' Main windows and setup. '''
# pylint: disable=redefined-outer-name

import sys
if sys.version_info[0] >= 3:
    import queue as Queue               # pylint: disable=import-error
else:
    import Queue                        # pylint: disable=unused-import
import multiprocessing
import os
import os.path
import subprocess

from subprocess import check_output

from gi.repository import Gtk                    # pylint: disable=E0611
from gi.repository import GLib                   # pylint: disable=E0611

from . import options
from . import run_sudo
from . import textview


def _paths_equals(path1, path2):
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


def _reconnect(widget, signal, handler, data):
    ''' Disconnect previous connection before doing connect.
    Beware: Stores the signal id as a widget attribute.
    '''
    signal_id_attr = signal + '_signal_id'
    if hasattr(widget, signal_id_attr):
        widget.disconnect(getattr(widget, signal_id_attr))
    id_ = widget.connect(signal, handler, data)
    setattr(widget, signal_id_attr, id_)


def _set_info_label(change, builder):
    ''' Compute the label explaining change status. '''
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


def _add_header(grid, row, change):
    ''' Add the 'Use: ' or '0: ' line headerto grid. '''
    if change.name == options.ORPHANED_OWNER or row != 0:
        hdr = Gtk.Label('%d: ' % row)
    else:
        hdr = Gtk.Label('Use: ')
    hdr.set_alignment(0.0, 0.5)
    hdr.set_justify(Gtk.Justification.LEFT)
    grid.attach(hdr, 0, row, 1, 1)


def _add_filename(grid, filename, row):
    ''' Add filename to grid line. '''
    label = Gtk.Label(os.path.basename(filename))
    label.set_alignment(0.0, 0.5)
    label.set_justify(Gtk.Justification.LEFT)
    grid.attach(label, 1, row, 1, 1)


def _cell_alignment():
    ''' Right-attached expanded-fill alignment. '''
    a = Gtk.Alignment()
    a.set(1.0, 0.5, 1.0, 1.0)
    a.set_padding(0, 0, 40, 10)
    return a


def _add_filedate(grid, path, row, refpath, builder):
    ''' Add date or 'duplicate' to  grid line. '''

    def on_sudo_done(date_output):
        ''' sudo done, update date column. '''
        date = date_output.split()[5]
        label = Gtk.Label(date)
        align = _cell_alignment()
        align.add(label)
        grid.attach(align, 2, row, 1, 1)
        builder.get_object('merge_window').show_all()

    if row != 0 and _paths_equals(path, refpath):
        label = Gtk.Label('duplicate')
        align = _cell_alignment()
        align.add(label)
        grid.attach(align, 2, row, 1, 1)
    else:
        cmd = "ls -l --time-style +%Y-%m-%d".split()
        cmd.append(path)
        run_sudo.run_command(cmd, on_sudo_done, builder)


def _add_delete_box(grid, row):
    ''' Add the delete checkbox to grid line. '''
    box = Gtk.CheckButton("Delete")
    box.set_active(True)
    align = _cell_alignment()
    align.add(box)
    grid.attach(align, 3, row, 1, 1)


def _add_up_button(grid, row, change, callback):
    ''' Add the ^-button to grid line. '''
    b = Gtk.Button()
    image = Gtk.Image()
    image.set_from_stock(Gtk.STOCK_GO_UP, Gtk.IconSize.MENU)
    b.set_image(image)
    align = _cell_alignment()
    align.add(b)
    grid.attach(align, 4, row, 1, 1)
    b.connect("clicked", callback, change)


def _create_grid_align(builder):
    ''' Create the align holding the grid. '''
    grid = Gtk.Grid()
    grid_align = builder.get_object("table_align")
    grid_align.get_child().destroy()
    grid_align.add(grid)
    return grid_align


def _update_grid(grid, change, builder, up_button_callback):
    ''' Complete grid with oneline for each file variant. '''
    for i in range(0, 6):
        grid.insert_column(i)
    grid.set_column_spacing(10)
    grid.set_hexpand(True)
    grid.set_halign(Gtk.Align.FILL)
    for row in range(0, len(change.files)):
        grid.insert_row(row)
        _add_header(grid, row, change)
        _add_filename(grid, change.get_cached(row), row)
        if row or change.package == options.ORPHANED_OWNER:
            _add_delete_box(grid, row)
        if row and change.package != options.ORPHANED_OWNER:
            _add_up_button(grid, row, change, up_button_callback)
        _add_filedate(grid, change.get_cached(row), row,
                     change.get_cached(), builder)
    grid.row_count = len(change.files)
    grid.column_count = 6


def rebuild_window(change, builder, refresh_func):
    ''' Handle user clicking change link. '''
    # pylint: disable=R0914,R0912
    # TBD!!!

    def cb_on_merge_diff_btn_clicked(button, change):
        ''' Diff button on merge window. '''
        path0 = change.get_cached()
        path1 = change.get_cached(1)
        cmd = options.diff_option.cmd % {'path0': path0, 'path1': path1}
        try:
            diff = check_output(cmd.split())
        except subprocess.CalledProcessError as e:
            diff = e.output
        if len(diff) > options.profile.max_viewsize:
            textview.size_warning_dialog(button.get_toplevel(), 'Diff')
            diff = diff[:options.profile.max_viewsize]
        w = textview.show_some_text(diff, builder, change)
        w.show_all()
        return True

    def cb_on_merge_view_btn_clicked(button, change):
        ''' View button on merge window. '''
        path = change.get_cached()
        if os.stat(path).st_size > options.profile.max_viewsize:
            textview.size_warning_dialog(button.get_toplevel(), path)
        with open(path) as f:
            text = f.read(options.profile.max_viewsize)
        w = textview.show_some_text(text, builder, change)
        w.show_all()
        return True

    def cb_on_merge_merge_btn_clicked(button, change):
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
                refresh_func()
                p.join()
                if old_cs != cs(path0):
                    change.update_from_cache()
                change.rescan()
                w = rebuild_window(change, builder, refresh_func)
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
-       # builder.get_object('merge_window').hide()
        button.get_toplevel().hide()
        return True

    def cb_on_merge_ok_btn_clicked(button, change):
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
                run_sudo.run_command(cmd, refresh_func, builder)
            button.get_toplevel().show_all()

        cached = change.get_cached()
        if not _paths_equals(cached, change.basepath):
            cmd = ['cp', cached, change.basepath]
            run_sudo.run_command(cmd, do_when_cache_updated, builder)
        else:
            do_when_cache_updated()

    def cb_on_merge_up_button_click(button, change):
        ''' The ^-button on row. Swap this row and row above. '''
        grid = button.get_parent().get_parent()
        for row in range(1, grid.row_count):
            if grid.get_child_at(4, row).get_child() == button:
                basename = grid.get_child_at(1, row).get_text()
                break
        else:
            print("Cannot find button file")
        found = [f for f in change.files if f.endswith(basename)]
        if found:
            change.shuffle_up(found[0])
            rebuild_window(change, builder, refresh_func)
        else:
            print("No match for button basename: " + basename)
        w = builder.get_object('merge_window')
        w.show_all()

    _set_info_label(change, builder)
    buttons_align = builder.get_object("merge_buttons_align")
    info_hbox = builder.get_object("merge_info_hbox")
    grid_align = _create_grid_align(builder)
    top_vbox = builder.get_object("merge_top_vbox")

    for child in top_vbox.get_children():
        top_vbox.remove(child)

    top_vbox.pack_start(info_hbox, True, True, 10)
    top_vbox.pack_start(Gtk.HSeparator(), True, True, 10)
    top_vbox.pack_start(grid_align, True, True, 10)
    top_vbox.pack_start(buttons_align, True, True, 10)
    _update_grid(grid_align.get_child(),
                change,
                builder,
                cb_on_merge_up_button_click)
    btn = builder.get_object("merge_merge_btn")
    _reconnect(btn, "clicked", cb_on_merge_merge_btn_clicked, change)
    btn = builder.get_object("merge_diff_btn")
    _reconnect(btn, "clicked", cb_on_merge_diff_btn_clicked, change)
    btn = builder.get_object("merge_view_btn")
    _reconnect(btn, "clicked", cb_on_merge_view_btn_clicked, change)
    btn = builder.get_object("merge_ok_btn")
    _reconnect(btn, "clicked", cb_on_merge_ok_btn_clicked, change)
    btn = builder.get_object("merge_cancel_btn")
    _reconnect(btn, "clicked", cb_on_merge_cancel_btn_clicked, change)
    w = builder.get_object('merge_window')
    _reconnect(w, 'delete-event', cb_on_window_delete_event, change)
    w.set_title(options.profile.app + ': ' + change.basename)
    #w.show_all()
    return w


def cb_on_window_delete_event(window, event, data=None):
    ''' Generic window close event. '''
    window.hide()
    return True


def cb_on_merge_cancel_btn_clicked(button, change=None):
    ''' Cancel button on merge window. '''
    button.get_toplevel().hide()
    return True



# vim: set expandtab ts=4 sw=4:
