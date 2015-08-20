# Makefile for TazPanel.
#
PREFIX?=/usr
SYSCONFDIR?=/etc/slitaz
DESTDIR?=
LINGUAS?=el es fr pl pt_BR ru sv
PANEL?=/var/www/tazpanel
BASECGI?=boot.cgi hardware.cgi help.cgi index.cgi network.cgi settings.cgi
EXTRACGI?=floppy.cgi powersaving.cgi

VERSION:=$(shell grep ^VERSION tazpanel | cut -d= -f2)

all: msgfmt
	mkdir build
	cp -a *.cgi bootloader tazpanel \
		lib/libtazpanel lib/*.js \
		styles/default/*.html styles/default/*.css \
		build
	./stripall.sh

# i18n

pot:
	xgettext -o po/tazpanel.pot -L Shell -k_ -k_n -k_p:1,2 \
		--from-code="UTF-8" \
		--package-name="TazPanel" \
		--package-version="$(VERSION)" \
		./tazpanel ./index.cgi ./network.cgi ./boot.cgi \
		./hardware.cgi ./settings.cgi ./lib/libtazpanel ./help.cgi \
		./styles/default/header.html ./styles/default/footer.html

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

install:
	mkdir -p \
		$(DESTDIR)$(PREFIX)/bin \
		$(DESTDIR)$(PREFIX)/share/locale \
		$(DESTDIR)$(PREFIX)/share/applications \
		$(DESTDIR)$(SYSCONFDIR) \
		$(DESTDIR)$(PANEL)/menu.d \
		$(DESTDIR)/var/log \
		$(DESTDIR)$(PANEL)/lib \
		$(DESTDIR)$(PANEL)/styles/default

	cp -a build/tazpanel $(DESTDIR)$(PREFIX)/bin
	-[ "$(VERSION)" ] && sed -i 's/^VERSION=[0-9].*/VERSION=$(VERSION)/' $(DESTDIR)$(PREFIX)/bin/tazpanel

	cp -a doc/ README README.html $(DESTDIR)$(PANEL)
	cp -a build/libtazpanel build/gz/*.js.gz $(DESTDIR)$(PANEL)/lib
	cp -a build/gz/*.css.gz build/*.html styles/default/*.ico styles/default/*.ttf $(DESTDIR)$(PANEL)/styles/default

	@for c in $(BASECGI); do \
		cp -a build/$$c $(DESTDIR)$(PANEL); \
	done;

	if [ -e $(DESTDIR)$(PANEL)/user ] ; then rm -rf $(DESTDIR)$(PANEL)/user; fi
	ln -s . $(DESTDIR)$(PANEL)/user

	cp -a po/mo/*        $(DESTDIR)$(PREFIX)/share/locale
	cp -a data/*.conf    $(DESTDIR)$(SYSCONFDIR)
	cp -a data/*.desktop $(DESTDIR)$(PREFIX)/share/applications
	cp -a data/icons     $(DESTDIR)$(PREFIX)/share
	touch $(DESTDIR)/var/log/tazpanel.log

	@# Remove this when TazWeb will support OpenType ligatures for web-fonts (maybe, after Webkit upgrade?)
	mkdir -p $(DESTDIR)/usr/share/fonts/TTF
	ln -fs $(PANEL)/styles/default/tazpanel.ttf $(DESTDIR)/usr/share/fonts/TTF/tazpanel.ttf

install_extra:
	mkdir -p \
		$(DESTDIR)$(PANEL)/menu.d/boot \
		$(DESTDIR)$(PANEL)/menu.d/hardware \
		$(DESTDIR)/usr/bin
	@for c in $(EXTRACGI); do \
		cp -a build/$$c $(DESTDIR)$(PANEL); \
	done;
	cp -a build/bootloader $(DESTDIR)/usr/bin
	ln -s ../../floppy.cgi $(DESTDIR)$(PANEL)/menu.d/boot/floppy
	ln -s ../../powersaving.cgi $(DESTDIR)$(PANEL)/menu.d/hardware/powersaving

# Clean source

clean:
	rm -rf build
	rm -rf po/mo
	rm -f po/*.mo
	rm -f po/*.*~

help:
	@echo "make [ pot | msgmerge | msgfmt | all | install | clean ]"
