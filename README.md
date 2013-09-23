## etc-cleaner README

etc-cleaner is a simple GUI application intended to make it easier to
maintain the configuration files in /etc. The problem is basically about
merging the local changes with the changes made by the package installers
when updating.

The app first lists all changes done so far (i. e., files having any
.rpmnew or .rpmsave variants when using rpm).  When clicking on such a
change there is a window where you can select which variant to use, view it,
merge it or just show the diff. There are some screenshots making it more
clear in the screenshots directory.

## Installation
To test, no installation is needed - the app can be run straight from
the source tree checked out from git. However, there is then no desktop
inegration.

Otherwise, three installation modes are supported using the Makefile:
- make install-home installs everything under ~/.local with a binary
  in ~/bin. No root required.
- make install-local installs everything under /usr/local
- make install-usr installs everything under /usr

To uninstall use the corresponding  uninstall-home, uninstall-local and
uninstall-usr targets

## Running
For the source version
```
    $ export PATH=$PWD:$PATH
    $ ./etc-cleaner
```
## Extending

The preferences window is basically dead simple, presenting a few precanned
alternatives. To create other alternatives such as another tool for merging
or a complete profile, create a new plugin similar to those in the plugins
directory. Using one existing alternative as a template this is not hard. A
few cave-eats:
- Install your own plugins in ~/.local/share/etc-cleaner/plugins or
  /etc/etc-cleaner/plugins
- The class name must be unique. A plugin with the same class name as a
  system plugin will not be loaded.
- The option_id could be unique or not. If not unique, your plugin will
  shadow the system one.

## rpm-config notes.
This package is inspired by rpm-config. However, here are also some
changes:
  - This is obviously a GUI app.
  - External merge tools are not run as root. Merging is done on
    local copies which are copied to-from /etc using sudo.
  - The workflow is more user-driven with user picking changes from
    a list instead of being pushed to answer questions for each change.
  - I have tried to isolate the rpm dependencies, which are not really
    that big. An as yet untested dpkg profile serves as proof of concept.
