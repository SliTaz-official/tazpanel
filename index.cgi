#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS. Use the main css form
# command so we are faster and do not load unneeded functions. If necessary
# you can use the lib/ dir to handle external resources.
#
# Copyright (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

#
# Things to do before displaying the page
#

[ -n "$(GET panel_pass)" ] &&
	sed -i s@/:root:.*@/:root:$(GET panel_pass)@ $HTTPD_CONF

#
# Commands
#

case " $(GET) " in
	*\ file\ *)
		#
		# Handle files (may have an edit function, we will see)
		#
		TITLE="- File"
		xhtml_header
		file="$(GET file)"
		echo "<h2>$file</h2>"
		echo '<pre>'
		# Handle file type by extension as a Web Server does it.
		case "$file" in
			*.conf|*.lst)
				syntax_highlighter conf ;;
			*.sh|*.cgi)
				syntax_highlighter sh ;;
			*)
				cat ;;
		esac < $file
		echo '</pre>' ;;
	*\ debug\ *)
		TITLE="- Debug"
		xhtml_header
		echo '<h2>HTTP Environment</h2>'
		echo '<pre>'
		httpinfo
		echo '</pre>' ;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		[ -n "$(GET gen_locale)" ] && new_locale=$(GET gen_locale)
		[ -n "$(GET rdate)" ] && echo ""
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

<h3>`gettext "Panel Activity"`</h3>
<pre>
$(cat $LOG_FILE | tail -n 6)
</pre>

<h3>`gettext "Panel settings"`</h3>
<form method="get" action="$SCRIPT_NAME">
	<div>
		`gettext "Panel password:"`
		<input type="password" name="panel_pass"/>
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
