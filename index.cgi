#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS. Use the main cas form
# command so we are faster and dont load unneeded function. If nececarry
# you can use the lib/ dir to handle external resources.
#
echo "Content-Type: text/html"
echo ""

# Common functions from libtazpanel
. lib/libtazpanel
get_config

#
# Commands
#

case "$QUERY_STRING" in
	boot)
		#
		# Everything until user login
		#
		TITLE="- Network"
		xhtml_header
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
		;;
	users|user=*)
		#
		# Manage system user accounts
		#
		TITLE="- Users"
		xhtml_header
		cmdline=`echo ${QUERY_STRING#user*=} | sed s'/&/ /g'`		
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
	<p>`gettext "Manage human users on your SliTaz system"`</p>
</div>
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
		cat << EOT
	<div>
		<input type="submit" value="`gettext "Delete selected user"`" />
	</div>
</form>

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
		#
		# Network configuration
		#
		TITLE="- Network"
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Networking`</h2>
	<p>`gettext "Manage network connection and services`</p>
</div>

<h3>Output of: ifconfig -a</h3>
<pre>
`ifconfig -a`
</pre>
EOT
		;;
	hardware)
		#
		# Hardware drivers, devices, filesystem, screen
		#
		TITLE="- Hardware"
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Drivers &amp; Devices"`</h2>
	<p>`gettext "Manage your computer hardware`</p>
</div>
EOT
		echo '<pre>'
			fdisk -l | fgrep Disk
		echo '</pre>'
		echo '<pre>'
			df -h | grep ^/dev
		echo '</pre>'
		echo '<pre>'
			lspci
		echo '</pre>'
		;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>`gettext "Host:"` `hostname`</h2>
	<p>`gettext "SliTaz administration et configuration Panel"`<p>
</div>

<h3>`gettext "Summary"`</h3>
<div id="summary">

<p>
	`gettext "Uptime:"` `uptime`
</p>
<p>
	`gettext "Memory in Mb:"`
	`free -m | grep Mem: | awk \
	'{print "| Total:", $2, "| Used:", $3, "| Free:", $4}'`
</p>
<p>
	`gettext "Filesystem usage statistics:"`
</p>
<pre>
`df -h | grep ^/dev`
</pre>

<!-- Close summary -->
</div>
EOT
		;;
esac

xhtml_footer
exit 0
