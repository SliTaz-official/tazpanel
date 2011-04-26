# Makefile for TazPanel.
#
PREFIX?=/usr
SYSCONFDIR?=/etc/slitaz
DESTDIR?=
LINGUAS?=fr pt
PANEL?=/var/www/tazpanel

VERSION:=$(shell grep ^VERSION tazpanel | cut -d '=' -f 2)

# i18n

pot:
	xgettext -o po/tazpanel.pot -L Shell \
		--package-name="TazPanel" \
		--package-version="$(VERSION)" \
		./tazpanel ./index.cgi ./pkgs.cgi ./live.cgi \
		./network.cgi ./boot.cgi ./hardware.cgi \
		./settings.cgi ./lib/libtazpanel

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/tazpanel.pot; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/tazpanel.mo po/$$l.po; \
	done;

# Installation

install: msgfmt
	mkdir -p $(DESTDIR)$(PREFIX)/bin \
		$(DESTDIR)$(PREFIX)/share/locale \
		$(DESTDIR)$(PREFIX)/share/applications \
		$(DESTDIR)$(PREFIX)/share/pixmaps \
		$(DESTDIR)$(SYSCONFDIR) \
		$(DESTDIR)$(PANEL)
	cp -a tazpanel $(DESTDIR)$(PREFIX)/bin
	cp -a data/*.conf $(DESTDIR)$(SYSCONFDIR)
	cp -a *.cgi lib/ styles/ doc/ README $(DESTDIR)$(PANEL)	
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale
	cp -a data/*.desktop $(DESTDIR)$(PREFIX)/share/applications
	cp -a data/*.png $(DESTDIR)$(PREFIX)/share/pixmaps

# Clean source

clean:
	rm -rf po/mo
	rm -f po/*.mo
	rm -f po/*.*~

