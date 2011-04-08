#!/bin/sh
#
# Boot CGI script - All what appens before login (grub, rcS, slim)
#
# Copyright (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel and source main boot config file.
. lib/libtazpanel
. /etc/rcS.conf
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

TITLE="- Hardware"

#
# Commands
#

case "$QUERY_STRING" in
	*)
		#
		# Everything until user login
		#
		. /etc/rcS.conf
		TITLE="- Boot"
		xhtml_header
		debug_info
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Boot &amp; startup"`</h2>
	<p>
		`gettext "Everything that appends before user login."` 
	</p>
</div>

<h3>`gettext "Kernel cmdline"`</h3>
<pre>
`cat /proc/cmdline`
</pre>
EOT
		# Demon list
		table_start
		cat << EOT
<thead>
	<tr>
		<td>`gettext "Name"`</td>
		<td>`gettext "Dessciption"`</td>
		<td>`gettext "Status"`</td>
	</tr>
</thead>
EOT
		for d in `echo $RUN_DAEMONS`
		do
			echo '<tr>'
			echo "<td>$d</td>"
			if [ -d "$LOCALSTATE/installed/$d" ]; then
				. $LOCALSTATE/installed/$d/receipt
				echo "<td>$SHORT_DESC</td>"
			else
				# Standard SliTaz deamons
				case "$d" in
					firewall)
						gettext "<td>SliTaz Firewall with iptable rules</td>" ;;
					hald)
						. $LOCALSTATE/installed/hal/receipt
						echo "<td>$SHORT_DESC</td>" ;;
					*)
						echo "<td>N/A</td>" ;;
				esac
			fi
			# Running or not
			if pidof $d; then
				echo "<td>`gettext \"Running\"` (`pidof $d`)</td>"
			else
				gettext "<td>Stopper</td>"
			fi
			echo '</tr>'
		done

		
		table_end
		cat << EOT
<h3>`gettext "Local startup commands"`</h3>
<pre>
`cat /etc/init.d/local.sh`
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
