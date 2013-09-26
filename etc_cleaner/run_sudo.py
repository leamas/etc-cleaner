#!/usr/bin/env python
''' Run sudo command, possibly prompting for password.  '''

import os
import sys

from gi.repository import Gtk                    # pylint: disable=E0611
from subprocess import Popen, PIPE, CalledProcessError, check_output

from . import prefix

_MAX_RETRIES = 3


def _show_login_window(command, on_ok, builder, retries):
    ''' Display login dialog, run on_ok() if password works. '''

    def again_dialog():
        ''' Show a wrong password, try again dialog. '''
        dialog = Gtk.MessageDialog(builder.get_object('main_window'),
                                   Gtk.DialogFlags.DESTROY_WITH_PARENT
                                       | Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.WARNING,
                                   Gtk.ButtonsType.OK,
                                   'Sudo authentication failed')
        dialog.run()
        dialog.destroy()

    def enough_dialog():
        ''' Too many failed logins. '''
        dialog = Gtk.MessageDialog(builder.get_object('main_window'),
                                   Gtk.DialogFlags.DESTROY_WITH_PARENT
                                       | Gtk.DialogFlags.MODAL,
                                   Gtk.MessageType.ERROR,
                                   Gtk.ButtonsType.OK,
                                   'Too many login failures, giving up.')
        dialog.run()
        dialog.destroy()

    def cb_login_cancel(button):
        ''' Login cancel button: exit, nothing more to do.'''
        print("Login cancelled, exiting")
        sys.exit(2)

    def cb_login_delete_event(window, event):
        ''' Login window deleted: exit, nothing more to do.'''
        print("Login window killed, exiting")
        sys.exit(2)

    def cb_login_ok(widget, retries):
        ''' Login OK button or CR in entry: run command using password. '''
        entry = builder.get_object('login_entry')
        my_cmd = ['sudo', '-S']
        my_cmd.extend(command)
        popen = Popen(my_cmd, stdin=PIPE, stdout=PIPE)
        stdout = popen.communicate(entry.get_text().strip() + '\n')[0]
        if popen.returncode == 0:
            on_ok(stdout)
            widget.get_toplevel().hide()
        else:
            retries[0] -= 1
            if retries[0] <= 0:
                enough_dialog()
                sys.exit(2)
            else:
                entry.set_text('')
                again_dialog()

    builder.get_object('login_cancel_btn').connect('clicked',
                                                   cb_login_cancel)
    builder.get_object('login_ok_btn').connect('clicked', cb_login_ok)
    builder.get_object('login_entry').connect('activate',
                                               cb_login_ok,
                                               retries)
    w = builder.get_object("login_window")
    w.connect('delete-event', cb_login_delete_event)
    header = builder.get_object('login_header')
    if not header.get_text():
        script = os.path.join(prefix.prefix_option.datadir,
                              'show-sudo-prompt')
        prompt = check_output('%s || true' % script, shell=True).strip()
        header.set_text(prompt)
    w.show_all()


def run_command(command, on_ok, builder):
    ''' Run command using sudo, invoke on_ok() with the stdout from
    command as argument if it succeeds.
    '''
    sudo = ['sudo', '-n'] + command
    try:
        paths = check_output(sudo)
        on_ok(paths)
    except CalledProcessError:
        retries = [_MAX_RETRIES]
        _show_login_window(command, on_ok, builder, retries)

# vim: set expandtab ts=4 sw=4:
