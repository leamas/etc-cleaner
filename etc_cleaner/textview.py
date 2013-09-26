''' Main windows and setup. '''

from gi.repository import Gtk                    # pylint: disable=E0611
from gi.repository.Pango import FontDescription  # pylint: disable=F0401,E0611

from . import options


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


def show_some_text(text, builder, change):
    ''' Read-only text display in a textview. '''

    def cb_on_view_ok_btn_clicked(button, change):
        ''' OK button on view_some_text window. '''
        button.get_toplevel().hide()
        return True

    textview = builder.get_object("view_textview")
    textview.modify_font(FontDescription("Monospace"))
    buf = textview.get_buffer()
    buf.set_text(text)
    w = builder.get_object('view_window')
    w.set_title(options.profile.app + ': ' + change.basename)
    w.connect('delete-event', cb_on_window_delete_event)
    b = builder.get_object('view_ok_btn')
    b.connect('clicked', cb_on_view_ok_btn_clicked, change)
    w.set_size_request(600, 600)
    return w


def cb_on_window_delete_event(window, event):
    ''' generic window close event. '''
    window.hide()
    return True


# vim: set expandtab ts=4 sw=4:
