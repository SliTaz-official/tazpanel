#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS. Use the main css form
# command so we are faster and do not load unneeded functions. If necessary
# you can use the lib/ dir to handle external resources.
#
# Copyright (C) 2011-2012 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE="TazPanel"

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
		<img src="$IMAGES/help.png" />$(gettext 'Differences')</a>
EOT
		esac
		break
	done
}


# OK status in table
ok_status_t() {
	echo "	<td>[<span class='diff-add'> OK </span>]</td></tr>"
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
	*\ exec\ *)
		exec="$(GET exec)"
		TITLE=$(gettext 'TazPanel - exec')
		xhtml_header
		cat << EOT
<h2>$exec</h2>
<pre>
$($exec 2>&1 | htmlize)
</pre>
EOT
		;;
	*\ file\ *)
		#
		# Handle files
		#
		file="$(GET file)"
		case $file in
			*.html)
				cat $file && exit 0 ;;
			*)
				TITLE=$(gettext 'TazPanel - File')
				xhtml_header
				echo "<h2>$file</h2>" ;;
		esac

		if [ "$(GET action)" == "edit" ]; then
			cat <<EOT
<form method="post" action="$SCRIPT_NAME?file=$file">
	<img src="$IMAGES/edit.png" />
	<input type="submit" value="$(gettext 'Save')">
		<a class="button" href='$SCRIPT_NAME?file=$file&action=diff'>
			<img src="$IMAGES/help.png" />$(gettext 'Differences')</a>
		<textarea name="content" rows="30" style="width: 100%;">
$(cat $file | htmlize)
</textarea>
</form>
EOT
#The space before textarea gets muddled when the form is submitted.
#It prevents anything else from getting messed up
		elif [ "$(GET action)" == "setvar" ]; then
			data="$(. $(GET file) ;eval echo \$$(GET var))"
			cat <<EOT
<form method="post" action="$SCRIPT_NAME?file=$file">
	<img src="$IMAGES/edit.png" />
	<input type="submit" value="$(gettext 'Save')">
	$(GET var) : 
	<input type="hidden" name="var" value="$(GET var)">
	<input type="text" name="content" value="${data:-$(GET default)}">
</form>
EOT
		elif [ "$(GET action)" == "diff" ]; then
			echo '<pre id="diff">'
			file_is_modified $file diff | syntax_highlighter diff
			echo '</pre>'
		else
			R=$(echo -en '\r')
			if [ -n "$(POST content)" ]; then
				if [ -n "$(POST var)" ]; then
					sed -i "s|^\\($(POST var)=\\).*|\1\"$(POST content)\"|" $file
				else
					sed "s/$R /\n/g;s/$R%0//g" > $file <<EOT
$(POST content)
EOT
				fi
			fi
			cat <<EOT
<div id="actions">
	<a class="button" href='$SCRIPT_NAME?file=$file&action=edit'>
		<img src="$IMAGES/edit.png" />$(gettext 'Edit')</a>
EOT
			file_is_modified $file button
			cat << EOT
</div>
<pre>
EOT
			# Handle file type by extension as a Web Server does it.
			case "$file" in
				*.conf|*.lst)
					syntax_highlighter conf ;;
				*.sh|*.cgi)
					syntax_highlighter sh ;;
				*)
					cat | htmlize ;;
			esac < $file
			echo '</pre>'
		fi ;;


	*\ terminal\ *|*\ cmd\ *)
		# Cmdline terminal.
		commands='cat du help ls ping pwd who wget'
		cmd=$(GET cmd)
		TITLE=$(gettext 'TazPanel - Terminal')
		xhtml_header
		cat << EOT
<section>
<form method="get" action="$SCRIPT_NAME">
	<div class="box">
		root@$(hostname):~# <input autofocus type="text" name="cmd" style="width: 80%;" />
	</div>
</form>
EOT
	echo '<pre id="terminal">'
	# Allow only a few commands for the moment.
	case "$cmd" in
		usage|help)
			gettext 'Small terminal emulator, commands options are supported.'
			echo ""
			eval_gettext 'Commands: $commands'
			echo ;;
		wget*)
			dl=/var/cache/downloads
			[ ! -d "$dl" ] && mkdir -p $dl
			eval_gettext 'Downloading to: $dl' && echo
			cd $dl && $cmd ;;
		du*|ls*|ping*|pwd|who)
			$cmd ;;
		cat*)
			# Cmd must be used with an arg.
			arg=$(echo $cmd | awk '{print $2}')
			[ "$arg" == "" ] && eval_gettext '$cmd needs an argument' && break
			$cmd ;;
		*)
			[ "$cmd" == "" ] || \
				eval_gettext 'Unknown command: $cmd' && echo
			eval_gettext 'Commands: $commands' ;;
	esac
	echo '</pre></section>'
	;;


	*\ top\ *)
		TITLE=$(gettext 'TazPanel - Process activity')
		xhtml_header
		echo $(gettext 'Refresh:') $(GET refresh)
		cat << EOT
<br/>
<form method="get">
	<input type="hidden" name="top"/>
	<input type="submit" name="refresh" value="$(gettext '1s')"/>
	<input type="submit" name="refresh" value="$(gettext '5s')"/>
	<input type="submit" name="refresh" value="$(gettext '10s')"/>
	<input type="submit" value="$(gettext 'none')"/>
</form>
EOT
		if [ -n "$(GET refresh)" ]; then
			echo -n '<meta http-equiv="refresh" content="'
			echo -n "$(GET refresh)" | sed 's|\([^0-9]*\)\([0-9]\+\).*|\2|'
			echo '">'
		fi

		echo '<pre>'
		top -n1 -b | htmlize | sed \
			-e s"#^[A-Z].*:\([^']\)#<span class='sh-comment'>\0</span>#"g \
			-e s"#PID.*\([^']\)#<span class='top'>\0</span>#"g
		echo '</pre>' ;;


	*\ debug\ *)
		TITLE=$(gettext 'TazPanel - Debug')
		xhtml_header
		cat << EOT
<h2>$(gettext 'HTTP Environment')</h2>

<pre>$(httpinfo)</pre>
EOT
		;;


	*\ report\ *)
		TITLE=$(gettext 'TazPanel - System report')
		[ -d /var/cache/slitaz ] || mkdir -p /var/cache/slitaz
		output=/var/cache/slitaz/sys-report.html
		xhtml_header
		cat << EOT
<h2>$(eval_gettext 'Reporting to: $output')</h2>
<table class="zebra outbox">
<tbody>
	<tr><td>$(gettext 'Creating report header...')</td>
EOT
		cat > $output << EOT
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta charset="utf-8" />
	<title>$(gettext 'SliTaz system report')</title>
	<style type="text/css">
		body { padding: 20px 60px; font-size: 13px; }
		h1, h2 { color: #444; }
		pre { background: #f1f1f1; border: 1px solid #ddd;
			padding: 10px; border-radius: 4px; }
		span.diff-rm { color: red; }
		span.diff-add { color: green; }
	</style>
</head>
<body>
EOT
		cat << EOT
	$(ok_status_t)
	<tr><td>$(gettext 'Creating system summary...')</td>
EOT
		cat >> $output << EOT
<h1>$(gettext 'SliTaz system report')</h1>
$(gettext 'Date:') $(date)
<pre>
uptime   : $(uptime)
cmdline  : $(cat /proc/cmdline)
version  : $(cat /etc/slitaz-release)
packages : $(ls /var/lib/tazpkg/installed | wc -l) installed
kernel   : $(uname -r)
</pre>
EOT
		cat << EOT
	$(ok_status_t)
	<tr><td>$(gettext 'Getting hardware info...')</td>
EOT
		cat >> $output << EOT
<h2>free</h2>
<pre>$(free)</pre>

<h2>lspci -k</h2>
<pre>$(lspci -k)</pre>

<h2>lsusb</h2>
<pre>$(lsusb)</pre>

<h2>lsmod</h2>
<pre>$(lsmod)</pre>

EOT
		cat << EOT
	$(ok_status_t)
	<tr><td>$(gettext 'Getting networking info...')</td>
EOT
		cat >> $output << EOT
<h2>ifconfig -a</h2>
<pre>$(ifconfig -a)</pre>

<h2>route -n</h2>
<pre>$(route -n)</pre>

<h2>/etc/resolv.conf</h2>
<pre>$(cat /etc/resolv.conf)</pre>
EOT
		cat << EOT
	$(ok_status_t)
	<tr><td>$(gettext 'Getting filesystems info...')</td>
EOT
		cat >> $output << EOT
<h2>blkid</h2>
<pre>$(blkid)</pre>

<h2>fdisk -l</h2>
<pre>$(fdisk -l)</pre>

<h2>mount</h2>
<pre>$(mount)</pre>

<h2>df -h</h2>
<pre>$(df -h)</pre>

<h2>df -i</h2>
<pre>$(df -i)</pre>
EOT
		cat << EOT
	$(ok_status_t)
	<tr><td>$(gettext 'Getting boot logs...')</td>
EOT
		cat >> $output << EOT
<h2>$(gettext 'Kernel messages')</h2>
<pre>$(cat /var/log/dmesg.log)</pre>

<h2>$(gettext 'Boot scripts')</h2>
<pre>$(cat /var/log/boot.log | filter_taztools_msgs)</pre>
EOT
		cat << EOT
	$(ok_status_t)
	<tr><td>$(gettext 'Creating report footer...')</td>
EOT
		cat cat >> $output << EOT
</body>
</html>
EOT
		cat << EOT
	$(ok_status_t)
</tbody>
</table>
<p><a class="button" href="$SCRIPT_NAME?file=$output">
	<img src="/styles/default/images/browser.png" />
	$(gettext 'View report')</a>
	$(msg tip "$(gettext 'This report can be attached with a bug report on:')
	<a href="http://bugs.slitaz.org/">bugs.slitaz.org</a></p>")
EOT
		;;


	*)
		#
		# Default xHTML content
		#
		xhtml_header
		[ -n "$(GET gen_locale)" ] && new_locale=$(GET gen_locale)
		[ -n "$(GET rdate)" ] && echo ""
		hostname=$(hostname)
		cat << EOT
<div id="wrapper">
	<h2>$(eval_gettext 'Host: $hostname')</h2>
	<p>$(gettext 'SliTaz administration and configuration Panel')<p>
</div>
<div id="actions">
	<a class="button" href="$SCRIPT_NAME?terminal">
		<img src="$IMAGES/terminal.png" />$(gettext 'Terminal')</a>
	<a class="button" href="$SCRIPT_NAME?top">
		<img src="$IMAGES/monitor.png" />$(gettext 'Process activity')</a>
	<a class="button" href="$SCRIPT_NAME?report">
		<img src="$IMAGES/text.png" />$(gettext 'Create a report')</a>
</div>

<section>
<h3>$(gettext 'Summary')</h3>
<div id="summary">
<table>
	<tr><td>$(gettext 'Uptime:')</td>
		<td>$(uptime)</td>
	</tr>
	<tr><td>$(gettext 'Memory in Mb:')</td>
EOT
		free -m | grep Mem: | awk '{print $2, $3, $4}' | while read memtotal memused memfree
		do
			cat << EOT
		<td>$(eval_gettext 'Total: $memtotal, Used: $memused, Free: $memfree')</td>
EOT
		done
		cat << EOT
	</tr>
	<tr><td>$(gettext 'Linux kernel:')</td>
		<td>$(uname -r)</td>
	</tr>
</table>
<!-- Close summary -->
</div>
</section>

<section>
<h4>$(gettext 'Network status')</h4>
$(list_network_interfaces)
</section>

<section>
<h4>$(gettext 'Filesystem usage statistics')</h4>
EOT
		# Disk stats (management is done as hardware.cgi)
		cat << EOT
<table class="zebra outbox">
EOT
		df_thead
		echo '<tbody>'
		df -h | grep ^/dev | while read fs size used av pct mp
		do
				cat << EOT
<tr>
	<td><a href="hardware.cgi">
		<img src="$IMAGES/harddisk.png" />${fs#/dev/}</a></td>
	<td>$(blkid $fs | sed '/LABEL=/!d;s/.*LABEL="\([^"]*\).*/\1/')</td>
	<td>$(blkid $fs | sed '/TYPE=/!d;s/.*TYPE="\([^"]*\).*/\1/')</td>
	<td>$size</td>
	<td>$av</td>
	<td class="meter"><meter min="0" max="100" value="$(echo $pct | cut -d% -f1)"
		low="$DU_WARN" high="$DU_CRIT" optimum="10"></meter>
		<span>$used - $pct</span>
	</td>
	<td>$mp</td>
	<td>$(blkid $fs | sed '/UUID=/!d;s/.*UUID="\([^"]*\).*/\1/')</td>
</tr>
EOT
		done
		cat << EOT
</tbody>
</table>
</section>

<section>
<h3>$(gettext 'Panel Activity')</h3>
<pre id="panel-activity">
$(cat $LOG_FILE | tail -n 8 | sort -r | syntax_highlighter activity)
</pre>
</section>
EOT
		;;
esac

xhtml_footer
exit 0
