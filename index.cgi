#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS
#
echo "Content-Type: text/html"
echo ""

# We need a config file first
CONFIG="/etc/slitaz/tazpanel.conf"
[ -f $CONFIG ] && . $CONFIG
[ -f tazpanel.conf ] && . tazpanel.conf
[ -z $PANEL ] && echo "No config file found" && exit 1

# xHTML 5 header
xhtml_header() {
	cat $HEADER | sed s/'- %TITLE%'/"$TITLE"/
}

table_start() {
	cat << EOT
<table>
	<tbody>
EOT
}

table_end () {
	cat << EOT
	</tbody>
</table>
EOT
}

#
# Commands
#

case "$QUERY_STRING" in
	boot)
		# Everything until user login
		TITLE="- Network"
		xhtml_header
		cat << EOT
<div id="wrapper">
<h2>`gettext "Boot &amp; startup"`</h2>
<p>
	`gettext "Everything that appends before user login."` 
</p>

<h3>`gettext "Kernel cmdline"`</h3>
<pre>
`cat /proc/cmdline`
</pre>
EOT
		echo '</div>' ;;
	users|user=*)
		# Manage system user accounts
		TITLE="- Users"
		xhtml_header

		cmdline=`echo ${QUERY_STRING#user*=} | sed s'/&/ /g'`		
		#user=`echo ${cmdline} | sed s'/=/ /' | awk '{print $1}'`
		#cmd=`echo ${cmdline} | sed s'/=/ /' |awk '{print $2}'`
		
		[ $DEBUG == "1" ] && echo \
			"<p class='debug'>$cmdline</p>"
			#$REQUEST_METHOD $QUERY_STRING
		# Parse cmdline
		for opt in $cmdline
		do
			case $opt in
				adduser=*)
					user=${opt#adduser=}
					cmd=adduser ;;
				deluser=*)
					user=${opt#deluser=}
					deluser $user ;;
				passwd=*)
					pass=${opt#passwd=} ;;
			esac
		done
		case "$cmd" in
			adduser)
				echo "$user"
				echo $pass
				adduser -D $user
				echo "$pass" | chpasswd
				for g in audio cdrom floppy video
				do
					addgroup $user $g
				done ;;
			*) continue ;;
		esac
		cat << EOT
<div id="wrapper">
<h2>`gettext "Manage users"`</h2>
<div>`gettext "Manage human users on your SliTaz system"`</div>
<form method="get" action="$SCRIPT_NAME">
EOT
		table_start
		cat << EOT
<tr id="thead">
	<td>`gettext "Name"`</td>
	<td>`gettext "User ID"`</td>
	<td>`gettext "Name"`</td>
	<td>`gettext "Home"`</td>
	<td>`gettext "SHell"`</td>
</tr>
EOT
		for i in `cat /etc/passwd | cut -d ":" -f 1`
		do
			if [ -d /home/$i ]; then
				login=$i
				uid=`cat /etc/passwd | grep $i | cut -d ":" -f 3`
				gid=`cat /etc/passwd | grep $i | cut -d ":" -f 4`
				name=`cat /etc/passwd | grep $i | cut -d ":" -f 5 | \
					sed s/,,,//`
				home=`cat /etc/passwd | grep $i | cut -d ":" -f 6`
				shell=`cat /etc/passwd | grep $i | cut -d ":" -f 7`
				echo '<tr>'
				echo "<td><input type='hidden' name='user' />
					<input type='checkbox' name='deluser' value='$login' />
					<img src='$IMAGES/user.png' />$login</td>"
				echo "<td>$uid:$gid</td>"
				echo "<td>$name</td>"
				echo "<td>$home</td>"
				echo "<td>$shell</td>"
				echo '</tr>'
			fi
		done
		table_end
		#`gettext "Selection:"`
		cat << EOT
<div>
	<input type="submit" value="`gettext "Delete selected user"`" />
</div>

</form>
</div>

<h3>`gettext "Add a user"`</h3>
<form method="get" action="$SCRIPT_NAME">
<input type="hidden" name="user" size="30" />
<p>
	`gettext ""`
	<input type="text" name="adduser" size="30" />
</p>
<p>
	`gettext ""`
	<input type="password" name="passwd" size="30" />
</p>
<input type="submit" value="`gettext ""`Create user" />
</form
EOT
		;;
	network)
		# Network configuration
		TITLE="- Network"
		xhtml_header
		cat << EOT
<div id="wrapper">
<h2>`gettext "Connections`</h2>
EOT
		echo '<pre>'
		ifconfig
		echo '</pre>'
		echo '</div>' ;;
	hardware)
		TITLE="- Hardware"
		xhtml_header
		cat << EOT
<div id="wrapper">
<h2>`gettext "Drivers &amp; Devices"`</h2>
EOT
		echo '<pre>'
		lspci
		echo '</pre>'
		echo '</div>' ;;
	*)
		# Default xHTML content
		xhtml_header
		cat << EOT
<div id="wrapper">
<h2>`gettext "Host:"` `hostname`</h2>
<p>
	Uptime: `uptime`
</p>
EOT
		echo '</div>'
		;;
esac

# xHTML 5 footer
cat $FOOTER
