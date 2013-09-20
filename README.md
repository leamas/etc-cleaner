## etc-cleaner README

etc-cleaner is a simple GUI application intended to make it easier to
maintain the configuraition files in /etc. The problem is basically about
merging the local changes with the changes made by the package installers
when updating.

The app first lists all changes done so far (i. e., files having any
.rpmnew or .rpmsave variants when using rpm).  When clicking on such a
change there is a window where you can select which variant to use, view it,
merge it or just show the diff. There are some screenshots making it more
clear in the screenshots directory.

## Installation
etc\_cleaner  must be in the load path. It works when running off the
src directory and iff setup.py gets it into a proper location. Use
PYTHONPATH= if in troubles.

the ui.glade file is looked for in the same directory as the etc-cleaner
script. Create a symlink if in trouble.

The sudo-askpass helper script must be in $PATH, see below. Sudo is used
to get root permissions and must be properly configured.

## Running
For the source version
```
    $ export PATH=$PWD:$PATH
    $ ln -s data/ui.glade .
    $ ./etc-cleaner
```

## rpm-config notes.
This package is inspired by rpm-config. However, here are also some
changes:
  - This is obviously a GUI app.
  - External merge tools are not run as root. Merging is done on
    local copies which are copied to-from /etc using sudo.
  - The workflow is more user-driven with user picking changes from
    a list instead of being pushed to answer questions for each change.
  - I have tried to isolate the rpm dependencies, which are not really
    that big. It should be doable to run this on e. g., debian as well.

