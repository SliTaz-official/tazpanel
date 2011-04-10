#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS. Use the main css form
# command so we are faster and do not load unneeded functions. If necessary
# you can use the lib/ dir to handle external resources.
#
# Copyright (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN



#
# Things to do before displaying the page
#

case "$QUERY_STRING" in
	panel-pass=*)
		new=${QUERY_STRING#*=}
		sed -i s@/:root:.*@/:root:$new@ $HTTPD_CONF ;;
	*) continue ;;
esac

#
# Commands
#

case "$QUERY_STRING" in
	debug*)
		TITLE="- Debug"
		query_string_parser
		xhtml_header
		cat << EOT
<pre>
QUERY_STRING="$QUERY_STRING" 

Fuction: query_string_parser (<a href="?debug=test=var1=var2">test</a>)

CASE="$CASE"
WANT="$WANT"
VAR_1="$VAR_1"
VAR_2="$VAR_2"
</pre>
EOT
		;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		debug_info
		case "$QUERY_STRING" in
			gen-locale=*)
				new_locale=${QUERY_STRING#gen-locale=} ;;
			rdate)
				echo "" ;;
		esac
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Host:"` `hostname`</h2>
	<p>`gettext "SliTaz administration and configuration Panel"`<p>
</div>

<h3>`gettext "Summary"`</h3>
<div id="summary">
	<p>
		`gettext "Uptime:"` `uptime`
	</p>
	<p>
		`gettext "Memory in Mb"`
		`free -m | grep Mem: | awk \
		'{print "| Total:", $2, "| Used:", $3, "| Free:", $4}'`
	</p>
<!-- Close summary -->
</div>

<h4>`gettext "Network status"`</h4>
`list_network_interfaces`

<h4>`gettext "Filesystem usage statistics"`</h4>
<pre>
`df -h | grep ^/dev`
</pre>

<h3>`gettext "Panel settings"`</h3>
<form method="get" action="$SCRIPT_NAME">
	<div>
		`gettext "Panel password:"`
		<input type="password" name="panel-pass"/>
		<input type="submit" value="`gettext "Change"`" />
	</div>
</form>
<p>
	$(gettext "TazPanel provide a debuging mode and page:")
	<a href='$SCRIPT_NAME?debug'>debug</a>
</p>

EOT
		;;
esac

xhtml_footer
exit 0
