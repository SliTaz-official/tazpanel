# Makefile for TazPanel.
#
PREFIX?=/usr
SYSCONFDIR?=/etc/slitaz
DESTDIR?=
LINGUAS?=fr

# i18n

pot:
	xgettext -o po/tazpkg-cgi/tazpkg-cgi.pot -L Shell \
		--package-name="Tazpkg CGI" ./tazpkg.cgi

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

# Installation.

install: msgfmt
	install -m 0755 -d $(DESTDIR)$(PREFIX)/bin
	install -m 0777 tazpanel $(DESTDIR)$(PREFIX)/bin
	mkdir -p $(DESTDIR)$(PREFIX)/share/locale
	cp -a po/mo/* $(DESTDIR)$(PREFIX)/share/locale
