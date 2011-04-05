#!/bin/sh
#
# CGI template interface for TazPanel (must go in $PANEL root to work).
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. ../lib/libtazpanel
get_config

# Cat translated help content
TITLE="- Help \&amp; Doc"

xhtml_header
cat tazpanel.html

echo '<h3>README</h3>'
echo '<pre>'
cat $PANEL/README
echo '</pre>'

xhtml_footer
exit 0
