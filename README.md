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

## Status
This is in the dogfood status: I'm using this for my own needs.  Let's call
it sort of alpha.

## Download
Either use git:
```
    $ git clone  https://github.com/leamas/etc-cleaner
    $ cd etc_cleaner
```
or download a tarball and use that:
```
    $ wget https://github.com/leamas/etc-cleaner/tarball/master/etc-cleaner.tar.gz
    $ tar xzf etc-cleaner.tar.gz
    $ cd leamas-etc-cleaner-*
```

## Setup
To test, no setup is needed - the app can be run straight from
the git source tree.  However, there is then no desktop integration.

Otherwise, three installation modes are supported using the Makefile:
```
$ make help
Plain 'make' doesn't do anything. Targets:
 - install-home:   Personal user install in ~/.local/share and ~/bin.
 - install-usr:    Install in /usr (as root).
 - install-local:  Install in /usr/local (as root).
 - dist:           Create tarball in dist/.
 - install-src:    Patch installation after unpacking dist tarball.
 - uninstall-home, uninstall-local, uninstall-usr: Remove installations.

 Variables:
 DESTDIR: For install-usr, relocate installation to DESTDIR/usr.
```

## Running
For the source version
```
    $ ./etc-cleaner
```
In the other installation modes just invoke etc-cleaner or use the desktop to
start it.


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

## Using git
etc-cleaner uses git attributes and filters to markup version info. Here
is also provisions to run pep8 and pylint on all code before committing.
All this is enabled with
```
    $ git-hooks/fix-setup
```

## rpmconf notes.
This package is inspired by rpmconf. However, here are also some
changes:
  - This is obviously a GUI app.
  - External merge tools are not run as root. Merging is done on
    local copies which are copied to-from /etc using sudo.
  - The workflow is more user-driven with user picking changes from
    a list instead of being pushed to answer questions for each change.
  - I have tried to isolate the rpm dependencies, which are not really
    that big. An as yet untested dpkg profile serves as proof of concept.
