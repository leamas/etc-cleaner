help_msg = \
Plain 'make' doesn't do anything. Targets: \n\
  - install-home:   Personal user install in ~/.local/share and ~/bin. \n\
  - install-usr:    Install in /usr (as root). \n\
  - install-local:  Install in /usr/local (as root). \n\
  - install-src:    Patch installation after unpacking dist tarball. \n\
  - dist:           Create tarball in dist/. \n\
  - uninstall-home, uninstall-local, uninstall-usr: Remove installations\n\
\n\
Variables: \n\
DESTDIR: For install-usr, relocate installation to DESTDIR/usr \n\
NO_TTYTICKETS: Disable tty_tickets in sudoers and get rid of ugly terminal.

pythonvers = $(shell python -c "import distutils; \
    print distutils.__version__.rsplit('.',1)[0]")

sitelib = python$(pythonvers)/site-packages

all:
	@echo -e "$(help_msg)"

help:  all

install:
	python ./setup.py --quiet install    \
	    --prefix=$(prefix)               \
	    --install-lib=$(python_sitelib)  \
	    --install-scripts=$(bindir)      \
	    --install-data=$(datadir)
	sed -i  -e '/^PATH/s|=.*|= "$(bindir)"|'                 \
	        -e   '/^PYTHONPATH/s|=.*|= "$(python_sitelib)"|' \
	    $(bindir)/etc-cleaner
	install -pDm 644 etc-cleaner.8 $(datadir)/man/man8/etc-cleaner.8
	ln -sf $(datadir)/etc-cleaner/ui.glade $(python_sitelib)/etc_cleaner
	ln -sf $(datadir)/etc-cleaner/plugins  $(python_sitelib)/etc_cleaner
	ln -sf $(datadir)/man/man8/etc-cleaner.8  $(python_sitelib)/etc_cleaner
	gtk-update-icon-cache -t $(datadir)/icons/hicolor
	[ -n "$(NO_TTYTICKETS)" ] && {                           \
	    sed -i '/exec=/s/=.*/=etc-cleaner/'                  \
	        $(datadir)/applications/etc-cleaner.desktop;     \
	    sudo cp etc-cleaner.sudo /etc/sudoers.d/etc-cleaner; \
	} || :

uninstall:
	rm -rf $(python_sitelib)/etc_cleaner*               \
	    $(datadir)/etc-cleaner                          \
	    $(datadir)/man/man8/etc-cleaner.8               \
	    $(datadir)/applications/etc-cleaner.desktop     \
	    $(datadir)/icons/hicolor/*/apps/etc-cleaner.png \
	    $(bindir)etc-cleaner $(bindir)rpmconf-sudo-askpass
	gtk-update-icon-cache -t $(datadir)/icons/hicolor

install-home:
	prefix=$(HOME)                               \
	python_sitelib=$(HOME)/.local/lib/$(sitelib) \
	datadir=$(HOME)/.local/share                 \
	bindir=$(HOME)/bin                           \
	$(MAKE) install
	mkdir -p $(HOME)/.local/share/etc-cleaner/plugins

install-local:
	prefix=$(DESTDIR)/usr/local                        \
	python_sitelib=$(DESTDIR)/usr/local/lib/$(sitelib) \
	datadir=$(DESTDIR)/usr/local/share                 \
	bindir=$(DESTDIR)/usr/local/bin                    \
	$(MAKE) install

install-usr:
	prefix=$(DESTDIR)/usr                        \
	python_sitelib=$(DESTDIR)/usr/lib/$(sitelib) \
	datadir=$(DESTDIR)/usr/share                 \
	bindir=$(DESTDIR)/usr/bin                    \
	$(MAKE) install
	mkdir -p $(DESTDIR)/etc/etc-cleaner/plugins

install-src:
	ln -sf $(PWD)/data/ui.glade etc_cleaner
	ln -sf $(PWD)/plugins  etc_cleaner
	ln -sf $(PWD)/etc-cleaner.8  etc_cleaner

install-src:
	ln -sf $(PWD)/data/ui.glade etc_cleaner
	ln -sf $(PWD)/plugins  etc_cleaner
	ln -sf $(PWD)/etc-cleaner.8  etc_cleaner

uninstall-home:
	python_sitelib=$(HOME)/.local/lib/$(sitelib) \
	datadir=$(HOME)/.local/share                 \
	bindir=$(HOME)/bin                           \
	$(MAKE) uninstall

uninstall-local:
	python_sitelib=/usr/local/lib/$(sitelib) \
	datadir=/usr/local/share                 \
	bindir=/usr/local/bin                    \
	$(MAKE) uninstall

uninstall-usr:
	python_sitelib=/usr/lib/$(sitelib) \
	datadir=/usr/share                 \
	bindir=/usr/bin                    \
	$(MAKE) uninstall

dist: .PHONY
	mv -f setup.py setup.py.OLD
	git checkout setup.py
	python ./setup.py sdist

.PHONY:
