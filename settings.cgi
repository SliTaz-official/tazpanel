#!/bin/sh
#
# System settings CGI interface: user, locale, keyboard, date. Since we
# dont have multiple pages here there is only one case used to get command
# values and the full content is following directly.
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

TITLE="- Settings"

# Get the list of system locales
list_locales() {
	cd /usr/share/i18n/locales
	for locale in `ls -1 [a-z][a-z]_[A-Z][A-Z]`
	do
		echo "<option value='$locale'>$locale</option>"
	done
}

#
# Commands executed before page loading.
#

case "$QUERY_STRING" in
	users|user=*)
		#
		# Manage system user accounts
		#
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
				adduser -D $user
				echo "$pass" | chpasswd
				for g in audio cdrom floppy video
				do
					addgroup $user $g
				done ;;
			*) continue ;;
		esac ;;
	gen-locale=*)
		new_locale=${QUERY_STRING#gen-locale=} ;;
	rdate)
		rdate -s tick.greyware.com ;;
	hwclock)
		hwclock -w ;;
	*)
		continue ;;
esac

#
# Default xHTML content
#
xhtml_header

cat << EOT
<div id="wrapper">
	<h2>`gettext "System settings"`</h2>
	<p>`gettext "Manage system time, users or language settings"`<p>
</div>

<pre>
`gettext "Time zome      :"` `cat /etc/TZ`
`gettext "System time    :"` `date`
`gettext "Hardware clock :"` `hwclock -r`
</pre>
<a class="button" href="$SCRIPT_NAME?rdate">`gettext "Sync online"`</a>
<a class="button" href="$SCRIPT_NAME?hwclock">`gettext "Set hardware clock"`</a>
EOT
#
# Users management
#

cat <<EOT
<h3>`gettext "Users"`</h3>
<form method="get" action="$SCRIPT_NAME">
EOT
table_start
cat << EOT
<tr class="thead">
	<td>`gettext "Login"`</td>
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

<h4>`gettext "Add a new user"`</h4>
<form method="get" action="$SCRIPT_NAME">
	<input type="hidden" name="user" />
	<p>`gettext "User login:"`</p>
	<p><input type="text" name="adduser" size="30" /></p>
	<p>`gettext "User password:"`</p>
	<p><input type="password" name="passwd" size="30" /></p>
	<input type="submit" value="`gettext "Create user"`" />
</form>
EOT

#
# Locale settings
#
cat << EOT
<a name="locale"></a>
<h3>`gettext "System language"`</h3>
<p>
EOT
		# Check if a new locale was requested
		if [ -n "$new_locale" ]; then
			rm -rf /usr/lib/locale/$new_locale
			localedef -i $new_locale -c -f UTF-8 \
				/usr/lib/locale/$new_locale
			# System configuration
			echo "LANG=$new_locale" > /etc/locale.conf
			echo "LC_ALL=$new_locale" >> /etc/locale.conf
			eval_gettext "You must logout and login again to your current
				session to use \$new_locale locale."
		else
			eval_gettext "Current system locales: "
			locale -a
		fi
		cat << EOT
</p>
<form method="get" action="$SCRIPT_NAME">
	`gettext "Available locales:"`
	<select name="gen-locale">
		<option value="en_US">en_US</options>
		`list_locales`
	</select>
	<input type="submit" value="`gettext "Generated and use"`" />
</form>
EOT

xhtml_footer
exit 0
