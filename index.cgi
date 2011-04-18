#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS. Use the main css form
# command so we are faster and do not load unneeded functions. If necessary
# you can use the lib/ dir to handle external resources.
#
# Copyright (C) 2011 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

# Check whether a configuration file has been modified after installation
file_is_modified()
{
	grep -l "  $1$" $INSTALLED/*/md5sum | while read file; do
	
		# Found, but can we do diff ?
		[ "$(grep -h "  $1$" $file)" != "$(md5sum $1)" ] || break
		org=$(dirname $file)/volatile.cpio.gz
		zcat $org 2>/dev/null | cpio -t 2>/dev/null | \
			grep -q "^${1#/}$" || break

		case "$2" in
		diff)
			tmp=/tmp/tazpanel$$
			mkdir -p $tmp
			( cd $tmp ; zcat $org | cpio -id ${1#/} )
			diff -u $tmp$1 $1
			rm -rf $tmp ;;
		button)
			cat <<EOT
	<a class="button" href='$SCRIPT_NAME?file=$1&action=diff'>
		<img src="$IMAGES/help.png" />`gettext "Differences"`</a>
EOT
		esac
		break
	done
}

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
		# Handle files
		#
		TITLE="- File"
		xhtml_header
		file="$(GET file)"
		echo "<h2>$file</h2>"
		if [ "$(GET action)" == "edit" ]; then
			cat <<EOT
<form method="post" action="$SCRIPT_NAME?file=$file">
<img src="$IMAGES/edit.png" />
<input type="submit" value="`gettext "Save"`">
<textarea name="content" rows="30" style="width: 100%;">
$(cat $file)
</textarea>
</form>
EOT
		elif [ "$(GET action)" == "diff" ]; then
			echo '<pre id="diff">'
			file_is_modified $file diff | syntax_highlighter diff
			echo '</pre>'
		else
			[ -n "$(POST content)" ] && 
				sed "s/`echo -en '\r'` /\n/g" > $file <<EOT
$(POST content)
EOT
			cat <<EOT
<div id="actions">
	<a class="button" href='$SCRIPT_NAME?file=$file&action=edit'>
		<img src="$IMAGES/edit.png" />`gettext "Edit"`</a>
EOT
			file_is_modified $file button
			echo -e "</div>\n<pre>"
			# Handle file type by extension as a Web Server does it.
			case "$file" in
				*.conf|*.lst)
					syntax_highlighter conf ;;
				*.sh|*.cgi)
					syntax_highlighter sh ;;
				*)
					cat ;;
			esac < $file
			echo '</pre>'
		fi ;;
	*\ top\ *)
		TITLE="- $(gettext "Process activity")"
		xhtml_header
		echo '<pre>'
		top -n1 -b | sed \
			-e s"#^[A-Z].*:\([^']\)#<span class='sh-comment'>\0</span>#"g \
			-e s"#PID.*\([^']\)#<span class='top'>\0</span>#"g
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
	<h2>$(gettext "Host:") $(hostname)</h2>
	<p>$(gettext "SliTaz administration and configuration Panel")<p>
</div>
<div id="actions">
	<a class="button" href="$SCRIPT_NAME?top">$(gettext "Process activity")</a>
</div>

<h3>$(gettext "Summary")</h3>
<div id="summary">
	<p>
		$(gettext "Uptime:") $(uptime)
	</p>
	<p>
		$(gettext "Memory in Mb")
		$(free -m | grep Mem: | awk \
		'{print "| Total:", $2, "| Used:", $3, "| Free:", $4}')
	</p>
<!-- Close summary -->
</div>

<h4>$(gettext "Network status")</h4>
$(list_network_interfaces)

<h4>$(gettext "Filesystem usage statistics")</h4>
EOT
		# Disk stats (management is done is hardwar.cgi)
		table_start
		df_thead
		df -h | grep ^/dev | while read fs size used av pct mp
		do
				cat << EOT
<tr>
	<td><a href="hardware.cgi">
		<img src="$IMAGES/harddisk.png" />$fs</a></td>
	<td>$size</td>
	<td>$av</td>
	<td class="pct"><div class="pct"
		style="width: $pct;">$used - $pct</div></td>
	<td>$mp</td>
</tr>
EOT
		done
		table_end
		cat << EOT
<h3>$(gettext "Panel Activity")</h3>
<pre id="panel-activity">
$(cat $LOG_FILE | tail -n 8 | sort -r | syntax_highlighter activity)
</pre>

EOT
		;;
esac

xhtml_footer
exit 0
