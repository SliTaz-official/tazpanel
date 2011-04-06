# Makefile for TazPanel.
#
PREFIX?=/usr
SYSCONFDIR?=/etc/slitaz
DESTDIR?=
LINGUAS?=pt
PANEL?=/var/www/tazpanel

VERSION:=$(shell grep ^VERSION tazpanel | cut -d '=' -f 2)

# i18n

pot:
	xgettext -o po/tazpanel.pot -L Shell \
		--package-name="TazPanel" \
		--package-version="$(VERSION)" \
		./tazpanel ./index.cgi ./pkgs.cgi ./live.cgi ./network.cgi

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/$$l.po po/tazpanel-pkgs.pot; \
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
		$(DESTDIR)$(SYSCONFDIR) \
		$(DESTDIR)$(PANEL)
	cp -a tazpanel $(DESTDIR)$(PREFIX)/bin
	cp -a *.conf data/httpd.conf $(DESTDIR)$(SYSCONFDIR)
	cp -a *.cgi lib/ styles/ $(DESTDIR)$(PANEL)	
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale

# Clean source

clean:
	rm -rf po/mo

