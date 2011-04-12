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
query_string_parser

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
	file=*)
		#
		# Handle files (may have an edit function, we will see)
		#
		TITLE="- File"
		xhtml_header
		echo "<h2>$WANT</h2>"
		echo '<pre>'
		# Handle file type by extension as a Web Server does it.
		# HTML entities: -e 's|&|\&amp;|g' -e 's|<|\&lt;|g' -e 's|>|\&gt;|g'
		case "$WANT" in
			*.conf|*.lst)
				cat $WANT | sed \
					-e s"#^\#\([^']*\)#<span style='color: \#555;'>\0</span>#"g \
					-e s"#^[A-Z]\([^']*\)=#<span style='color: \#000073;'>\0</span>#"g \
					-e s"#^[a-z]\([^']*\)#<span style='color: \#730c00;'>\0</span>#"g \
					-e s"#\"\([^']*\)\"#<span style='color: \#730c00;'>\0</span>#"g ;;
			*)
				cat $WANT ;;
		esac
		echo '</pre>' ;;
	debug*)
		TITLE="- Debug"
		xhtml_header
		cat << EOT
<h2>QUERY_STRING</h2>
<pre>
QUERY_STRING="$QUERY_STRING" 

Fuction: query_string_parser (<a href="?debug=test=var1=var2">test</a>)

CASE="$CASE"
WANT="$WANT"
VAR_1="$VAR_1"
VAR_2="$VAR_2"
</pre>
EOT
		echo '<h2>HTTP Environment</h2>'
		local var
		local info
		echo '<pre>'
		for var in SERVER_SOFTWARE SERVER_NAME SERVER_PORT GATEWAY_INTERFACE \
			AUTH_TYPE REMOTE_ADDR REMOTE_PORT HTTP_HOST HTTP_USER_AGENT  \
			HTTP_ACCEPT_LANGUAGE REQUEST_METHOD REQUEST_URI QUERY_STRING \
			CONTENT_LENGTH CONTENT_TYPE SCRIPT_NAME SCRIPT_FILENAME PWD
		do
			eval info=\$$var
			echo "$var=\"$info\""
		done
		echo '</pre>' ;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
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
	$(gettext "TazPanel provides a debuging mode and page:")
	<a href='$SCRIPT_NAME?debug'>debug</a>
</p>

EOT
		;;
esac

xhtml_footer
exit 0
