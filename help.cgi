#!/bin/sh
#
# help.cgi - Display TazPanel doc and README.
#
# Copyright (C) 2011 SliTaz GNU/Linux - BSD License
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. lib/libtazpanel
get_config

# Cat translated help content
TITLE="- Help \&amp; Doc"

xhtml_header

if [ -d doc ]; then
	cat doc/tazpanel.html
else
	cat /usr/share/doc/tazpanel/tazpanel.html
fi

echo '<h3>README</h3>'
echo '<pre>'
cat $PANEL/README
echo '</pre>'

xhtml_footer
exit 0
