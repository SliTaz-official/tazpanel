#!/bin/sh
#
# System settings CGI interface: user, locale, keyboard, date. Since we
# dont have multiple pages here there is only one case used to get command
# values and the full content is following directly.
#
# Copyright (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE="- Settings"

# Get the list of system locales
list_locales() {
	cd /usr/share/i18n/locales
	for locale in `ls -1 [a-z][a-z]_[A-Z][A-Z]`
	do
		echo "<option value='$locale'>$locale</option>"
	done
}

# Get the list of panle styles
list_styles() {
	cd $PANEL/styles
	for style in *
	do
		echo "<option value='$style'>$style</option>"
	done
}

#
# Commands executed before page loading.
#

case " $(GET) " in
	*\ user*)
		#
		# Manage system user accounts
		#
		if [ "$(GET deluser)" ]; then
			deluser $(GET deluser)
		fi
		user=$(GET adduser)
		if [ -n "$user" ]; then
			adduser -D $user
			echo "$(GET passwd)" | chpasswd
			for g in audio cdrom floppy video
			do
				addgroup $user $g
			done
		fi ;;
	*\ gen_locale\ *)
		new_locale=$(GET gen_locale) ;;
	*\ rdate\ *)
		rdate -s tick.greyware.com ;;
	*\ hwclock\ *)
		hwclock -w ;;
	*\ panel_pass*)
		sed -i s@/:root:.*@/:root:$(GET panel_pass)@ $HTTPD_CONF ;;
	*\ style*)
		sed -i s/'^STYLE.*'/"STYLE=\"$(GET style)\""/ $CONFIG
		. $CONFIG ;;	
esac

#
# Default xHTML content
#
xhtml_header

case " $(GET) " in
	*\ user*)
		#
		# Users management
		#
		cat <<EOT
<h3>`gettext "Manage users"`</h3>
<form method="get" action="$SCRIPT_NAME">
$(table_start)
<thead>
	<tr>
		<td>`gettext "Login"`</td>
		<td>`gettext "User ID"`</td>
		<td>`gettext "Name"`</td>
		<td>`gettext "Home"`</td>
		<td>`gettext "SHell"`</td>
	</tr>
</thead>
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
		;;
	*)
		#
		# Defaut system settings page
		#
		cat << EOT
<div id="wrapper">
	<h2>$(gettext "System settings")</h2>
	<p>$(gettext "Manage system time, users or language settings")<p>
</div>
<div id="actions">
	<a class="button" href="$SCRIPT_NAME?users">
		<img src="$IMAGES/users.png" />$(gettext "Manage users")</a>
</div>

<h3>`gettext "System time"`</h3>
<pre>
`gettext "Time zome      :"` `cat /etc/TZ`
`gettext "System time    :"` `date`
`gettext "Hardware clock :"` `hwclock -r`
</pre>
<a class="button" href="$SCRIPT_NAME?rdate">`gettext "Sync online"`</a>
<a class="button" href="$SCRIPT_NAME?hwclock">`gettext "Set hardware clock"`</a>
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
			gettext "Current system locales: "
			locale -a
		fi
		cat << EOT
</p>
<form method="get" action="$SCRIPT_NAME">
	$(gettext "Available locales:")
	<select name="gen_locale">
		<option value="en_US">en_US</options>
		$(list_locales)
	</select>
	<input type="submit" value="$(gettext "Activate")" />
</form>

<h3>$(gettext "Panel configuration")</h3>
<form method="get" action="$SCRIPT_NAME">
	<p>
		$(gettext "Style:")
		<select name="style">
			$(list_styles)
		</select>
		<input type="submit" value="$(gettext "Activate")" />
	</p>
</form>
<form method="get" action="$SCRIPT_NAME">
	<p>
		$(gettext "Panel password:")
		<input type="password" name="panel_pass"/>
		<input type="submit" value="$(gettext "Change")" />
	</p>
</form>
<p>
	$(gettext "Configuration files: ")
	<a class="button" href="index.cgi?file=$CONFIG">
		<img src="$IMAGES/edit.png" />$(gettext "Panel")</a>
	<a class="button" href="index.cgi?file=$HTTPD_CONF">
		<img src="$IMAGES/edit.png" />$(gettext "Server")</a>
</p>
<p>
	$(gettext "TazPanel provides a debuging mode and page:")
	<a href='/index.cgi?debug'>debug</a>
</p>
EOT
	;;
esac

xhtml_footer
exit 0
