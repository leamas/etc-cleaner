#!/usr/bin/env python
''' Run sudo command, possibly prompting for password.  '''

import subprocess
import sys

from subprocess import Popen, PIPE, CalledProcessError, check_output


def _show_login_window(command, on_ok, builder):
    ''' Display login dialog, run on_ok() if password works. '''

    def cb_login_cancel(button):
        ''' Login cancel button: exit, nothing more to do.'''
        print "Login cancelled, exiting"
        sys.exit(2)

    def cb_login_delete_event(window, event):
        ''' Login window deleted: exit, nothing more to do.'''
        print "Login window killed, exiting"
        sys.exit(2)

    def cb_login_ok(widget):
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
            print "sudo failed, exiting"
            sys.exit(2)

    retries = 0
    w = builder.get_object("login_window")
    builder.get_object('login_cancel_btn').connect('clicked',
                                                   cb_login_cancel)
    builder.get_object('login_ok_btn').connect('clicked', cb_login_ok)
    builder.get_object('login_entry').connect('activate', cb_login_ok)

    w.connect('delete-event', cb_login_delete_event)
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
        _show_login_window(command, on_ok, builder)

# vim: set expandtab ts=4 sw=4:
