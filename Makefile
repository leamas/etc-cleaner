help_msg = \
Plain 'make' doesn't do anything. Targets: \n\
  - install-home: Personal user install. \n\
  - install-usr:  Instll in /usr (as root). \n\
  - install-local:  Install in /usr/local (as root).

pythonvers = $(shell python -c "import distutils; \
    print distutils.__version__.rsplit('.',1)[0]")

sitelib = python$(pythonvers)/site-packages
home_sitelib = $(HOME)/.local/lib/$(sitelib)
local_sitelib = /usr/local/lib/$(sitelib)
usr_sitelib = /usr/lib/$(sitelib)

all:
	@echo -e "$(help_msg)"

install-home:
	sed -i  '/^PATH/s|= .*|= "$(HOME)/.local/bin"|' etc-cleaner
	sed -i  '/^PYTHONPATH/s|= .*|= "$(home_sitelib)"|' etc-cleaner
	python ./setup.py  install \
	    --prefix=$(HOME) \
	    --install-lib=$(home_sitelib) \
	    --install-scripts=$(HOME)/bin \
	    --install-data=$(HOME)/.local/share
	ln -sf ~/.local/share/etc-cleaner/ui.glade \
	    $(home_sitelib)/etc_cleaner
	ln -sf ~/.local/share/etc-cleaner/plugins \
	    $(home_sitelib)/etc_cleaner
	gtk-update-icon-cache -t ~/.local/share/icons/hicolor

install-local:
	sed -i  '/^PATH/s|= .*|= "/usr/local/bin"|' etc-cleaner
	sed -i  '/^PYTHONPATH/s|= .*|= "$(local_sitelib)"|' etc-cleaner
	python ./setup.py  --quiet install \
	    --prefix=/usr/local \
	    --install-lib=$(local_sitelib) \
	    --install-scripts=/usr/local/bin \
	    --install-data=/usr/local/share
	ln -sf /usr/local/share/etc-cleaner/ui.glade \
	    $(local_sitelib)/etc_cleaner
	ln -sf /usr/local/share/etc-cleaner/plugins \
	    $(local_sitelib)/etc_cleaner
	gtk-update-icon-cache -t /usr/local/share/icons/hicolor

install-usr:
	sed -i  '/^PATH/s|= .*|= "/usr/bin"|' etc-cleaner
	sed -i  '/^PYTHONPATH/s|= .*|= "$(usr_sitelib)"|' etc-cleaner
	python ./setup.py  --quiet install \
	    --prefix=/usr \
	    --install-lib=$(usr_sitelib) \
	    --install-scripts=/usr/bin \
	    --install-data=/usr/share
	ln -sf /usr/share/etc-cleaner/ui.glade \
	    $(usr_sitelib)/etc_cleaner
	ln -sf /usr/share/etc-cleaner/plugins \
	    $(usr_sitelib)/etc_cleaner
	gtk-update-icon-cache /usr/share/icons/hicolor

uninstall-home:
	rm -rf $(home_sitelib)/etc_cleaner* \
	    $(HOME)/.local/share/etc-cleaner \
	    $(HOME)/.local/share/applications/etc-cleaner.desktop \
	    $(HOME)/.local/share/icons/hicolor/*/apps/etc-cleaner.png \
	    $(HOME)/bin/etc-cleaner $(HOME)/bin/show-sudo-prompt
	gtk-update-icon-cache -t ~/.local/share/icons/hicolor

uninstall-local:
	rm -rf $(local_sitelib)/etc_cleaner* \
	    /usr/local/share/etc-cleaner \
	    /usr/local/share/applications/etc-cleaner.desktop \
	    /usr/local/share/icons/hicolor/*/apps/etc-cleaner.png \
	    /usr/local/bin/etc-cleaner /usr/local/bin/show-sudo-prompt
	gtk-update-icon-cache -t /usr/local/share/icons/hicolor

uninstall-usr:
	rm -rf $(usr_sitelib)/etc_cleaner* \
	    /usr/share/etc-cleaner \
	    /usr/share/applications/etc-cleaner.desktop \
	    /usr/share/icons/hicolor/*/apps/etc-cleaner.png \
	    /usr/bin/etc-cleaner /usr/bin/show-sudo-prompt
	gtk-update-icon-cache  /usr/share/icons/hicolor

