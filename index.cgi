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
			diff -u $tmp$1 $1 | sed "s|$tmp||"
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
		file="$(GET file)"
		case $file in
			*.html)
				cat $file && exit 0 ;;
			*)
				TITLE="- File"
				xhtml_header
				echo "<h2>$file</h2>" ;;
		esac
		if [ "$(GET action)" == "edit" ]; then
			cat <<EOT
<form method="post" action="$SCRIPT_NAME?file=$file">
<img src="$IMAGES/edit.png" />
<input type="submit" value="`gettext "Save"`">
<a class="button" href='$SCRIPT_NAME?file=$file&action=diff'>
	<img src="$IMAGES/help.png" />`gettext "Differences"`</a>
<textarea name="content" rows="30" style="width: 100%;">
$(cat $file)
 </textarea>
</form>
EOT
#The space before textarea gets muddled when the form is submitted.
#It prevents anything else from getting messed up
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
	*\ terminal\ *|*\ cmd\ *)
		# Cmdline terminal.
		commands='cat du help ls ping pwd who wget'
		cmd=$(GET cmd)
		TITLE="- $(gettext "Terminal")"
		xhtml_header
		cat << EOT
<form method="get" action="$SCRIPT_NAME">
	<div class="box">
		root@$(hostname):~# <input type="text" name="cmd" style="width: 80%;" />
	</div>
</form>
EOT
	echo '<pre id="terminal">'
	# Allow only a few commands for the moment.
	case "$cmd" in
		usage|help)
			gettext "Small terminal emulator, commands options are supported."
			echo ""
			gettext "Commands:"; echo " $commands" ;;
		wget*)
			dl=/var/cache/downloads
			[ ! -d "$dl" ] && mkdir -p $dl
			gettext "Downloading to:"; echo " $dl"
			cd $dl && $cmd ;;
		du*|ls*|ping*|pwd|who)
			$cmd ;;
		cat*)
			# Cmd must be used with an arg.
			arg=$(echo $cmd | awk '{print $2}')
			[ "$arg" == "" ] && echo -n "$cmd " && \
				gettext "needs an argument $arg" && exit 0
			$cmd ;;
		*)
			[ "$cmd" == "" ] || \
				gettext "Unknown command: $cmd"
			gettext "Commands:"; echo " $commands" ;;
	esac
	echo '</pre>' ;;
	*\ top\ *)
		TITLE="- $(gettext "Process activity")"
		xhtml_header
		echo `gettext "Refresh: "` $(GET refresh)
		echo '<br/>
<form method="get">
	<input type="hidden" name="top"/>
	<input type="submit" name="refresh" value="1s"/>
	<input type="submit" name="refresh" value="5s"/>
	<input type="submit" name="refresh" value="10s"/>
	<input type="submit" value="none"/>
</form>	'
		[ -n $(GET refresh) ] && 
		echo '<meta http-equiv="refresh" content="' $(GET refresh) '">' | sed "s/s //"

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
	*\ report\ *)
		TITLE="- $(gettext "System report")"
		[ -d /var/cache/slitaz ] || mkdir -p /var/cache/slitaz
		output=/var/cache/slitaz/sys-report.html
		xhtml_header
		echo "<h2>$(gettext "Reporting to:") $output</h2>"
		echo '<pre>'
		gettext "Creating report header...  "
		cat > $output << EOT
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>SliTaz system report</title>
	<style type="text/css">
		body { padding: 20px 60px; font-size: 13px; } h1, h2 { color: #444; }
		pre { background: #f1f1f1; border: 1px solid #ddd;
			padding: 10px; border-radius: 4px; }
		span.diff-rm { color: red; }
		span.diff-add { color: green; }
	</style>
</head>
<body>
EOT
		ok_status
		gettext "Creating system summary... "
		cat >> $output << EOT
<h1>SliTaz system report</h1>
Date: $(date)
<pre>
uptime   : $(uptime)
cmdline  : $(cat /proc/cmdline)
version  : $(cat /etc/slitaz-release)
packages : $(ls /var/lib/tazpkg/installed | wc -l) installed
kernel   : $(uname -r)
</pre>
EOT
		ok_status
		gettext "Getting hardware info...   "
		cat >> $output << EOT
<h2>free</h2>
<pre>
$(free)
</pre>

<h2>lspci -k</h2>
<pre>
$(lspci -k)
</pre>

<h2>lsusb</h2>
<pre>
$(lsusb)
</pre>

<h2>lsmod</h2>
<pre>
$(lsmod)
</pre>

EOT
		ok_status
		gettext "Getting networking info... "
		cat >> $output << EOT
<h2>ifconfig -a</h2>
<pre>
$(ifconfig -a)
</pre>
<h2>route -n</h2>
<pre>
$(route -n)
</pre>
<h2>/etc/resolv.conf</h2>
<pre>
$(cat /etc/resolv.conf)
</pre>
EOT
		ok_status
		gettext "Getting filesystems info..."
		cat >> $output << EOT
<h2>blkid</h2>
<pre>
$(blkid)
</pre>
<h2>fdisk -l</h2>
<pre>
$(fdisk -l)
</pre>
<h2>mount</h2>
<pre>
$(mount)
</pre>
<h2>df -h</h2>
<pre>
$(df -h)
</pre>
<h2>df -i</h2>
<pre>
$(df -i)
</pre>
EOT
		ok_status
		gettext "Getting boot logs...       "
		cat >> $output << EOT
<h2>$(gettext "Kernel messages")</h2>
<pre>
$(cat /var/log/dmesg.log)
</pre>
<h2>$(gettext "Boot scripts")</h2>
<pre>
$(cat /var/log/boot.log | filter_taztools_msgs)
</pre>
EOT
		ok_status
		gettext "Creating report footer...  "
		cat cat >> $output << EOT
</body>
</html>
EOT
		ok_status
		echo '</pre>'
		echo "<p><a class='button' href='$SCRIPT_NAME?file=$output'>
			$(gettext "View report")</a>"
		gettext "This report can be attached with a bug report on: "
		echo '<a href="http://bugs.slitaz.org/">bugs.slitaz.org</a></p>' ;;
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
	<a class="button" href="$SCRIPT_NAME?terminal">
		<img src="$IMAGES/terminal.png" />$(gettext "Terminal")</a>
	<a class="button" href="$SCRIPT_NAME?top">
		<img src="$IMAGES/monitor.png" />$(gettext "Process activity")</a>
	<a class="button" href="$SCRIPT_NAME?report">
		<img src="$IMAGES/text.png" />$(gettext "Create a report")</a>
</div>

<h3>$(gettext "Summary")</h3>
<div id="summary">
<pre>
$(gettext "Uptime       :")$(uptime)
$(gettext "Memory in Mb :") $(free -m | grep Mem: | awk \
	'{print "Total:", $2, "Used:", $3, "Free:", $4}')
$(gettext "Linux kernel :") $(uname -r)
</pre>
<!-- Close summary -->
</div>

<h4>$(gettext "Network status")</h4>
$(list_network_interfaces)

<h4>$(gettext "Filesystem usage statistics")</h4>
EOT
		# Disk stats (management is done as hardware.cgi)
		table_start
		df_thead
		df -h | grep ^/dev | while read fs size used av pct mp
		do
				cat << EOT
<tr>
	<td><a href="hardware.cgi">
		<img src="$IMAGES/harddisk.png" />${fs#/dev/}</a></td>
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
