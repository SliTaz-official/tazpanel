# Makefile for TazPanel.
#
PREFIX?=/usr
SYSCONFDIR?=/etc/slitaz
DESTDIR?=
LINGUAS?=fr
PANEL?=/var/www/tazpanel

VERSION:=$(shell grep ^VERSION tazpanel | cut -d '=' -f 2)

# i18n

pot:
	xgettext -o po/tazpanel-pkgs/tazpanel-pkgs.pot -L Shell \
		--package-name="Tazpanel pkgs CGI" \
		--package-version="$(VERSION)" ./pkgs.cgi
	xgettext -o po/tazpanel/tazpanel.pot -L Shell \
		--package-name="TazPanel cmdline" \
		--package-version="$(VERSION)" ./tazpanel
	xgettext -o po/tazpanel-cgi/tazpanel-cgi.pot -L Shell \
		--package-name="TazPanel CGI" \
		--package-version="$(VERSION)" ./index.cgi
	xgettext -o po/tazpanel-live/tazpanel-live.pot -L Shell \
		--package-name="Tazpanel live CGI" \
		--package-version="$(VERSION)" ./live.cgi

msgmerge:
	@for l in $(LINGUAS); do \
		echo -n "Updating $$l po file."; \
		msgmerge -U po/tazpkg-cgi/$$l.po po/tazpkg-cgi/tazpkg-cgi.pot; \
	done;

msgfmt:
	@for l in $(LINGUAS); do \
		echo "Compiling $$l mo file..."; \
		mkdir -p po/mo/$$l/LC_MESSAGES; \
		msgfmt -o po/mo/$$l/LC_MESSAGES/tazpkg-cgi.mo po/tazpkg-cgi/$$l.po; \
	done;

# Installation

install:
	mkdir -p $(DESTDIR)$(PREFIX)/bin \
		$(DESTDIR)$(PREFIX)/share/locale \
		$(DESTDIR)$(SYSCONFDIR) \
		$(DESTDIR)$(PANEL)
	cp -f tazpanel $(DESTDIR)$(PREFIX)/bin
	cp -f *.conf data/httpd.conf $(DESTDIR)$(SYSCONFDIR)
	cp -a *.cgi lib/ styles/ $(DESTDIR)$(PANEL)	
	#cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale

