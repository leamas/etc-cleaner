#!/usr/bin/env python
'''
Support poor admin when trying to keep config files up-to-date.

This is not a library. Nothing here is intended to be used by anything
besides the etc-cleaner script. Importing this module starts an
interactive process!

'''

from gi.repository import Gtk                    # pylint: disable=E0611

from . import options
from . import prefix


def rebuild_window(builder):
    ''' Setup preferences window. '''
    # pylint: disable=too-many-branches

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
        if update_prefs_option(option,
                               "prefix_info_label",
                               'prefix_checkbox'):
            prefix.prefix_option = option
        return True

    def on_profile_combo_changed(combo):
        ''' User selected a profile. '''
        tree_iter = combo.get_active_iter()
        if tree_iter is None:
            return True
        option_id = combo.get_model()[tree_iter][0]
        option = options.profiles_by_id[option_id]
        if update_prefs_option(option,
                               "profile_info_label",
                               'profile_checkbox'):
            options.profile = option
        return True

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


# vim: set expandtab ts=4 sw=4:
