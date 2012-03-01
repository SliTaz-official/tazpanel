#!/bin/sh
#
# System settings CGI interface: user, locale, keyboard, date. Since we
# don't have multiple pages here there is only one case used to get command
# values and the full content is followed directly.
#
# Copyright (C) 2011 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE="- Settings"

#
# Commands executed before page loading.
#

case " $(GET) " in
	*\ do\ *)
		# Assume no array support in httpd_helper.sh ;^)
		users=""
		IFS="&"
		for i in $QUERY_STRING ; do
			case "$i" in
			user=*)	users="$users ${i#user=}" ;;
			esac
		done
		unset IFS
		for cmd in "Delete user" "Lock user" "Unlock user" \
			   "Change password" ; do
			[ "$(GET do)" == "$(gettext "$cmd")" ] || continue
			for user in $users ; do
				case "$cmd" in
				Delete*)	deluser $user ;;
				Lock*)		passwd -l $user | log ;;
				Unlock*)	passwd -u $user | log ;;
				Change*)	echo "$user:$(GET password)" | chpasswd -m | log ;;
				esac
			done
		done ;;
	*\ adduser\ *)
		#
		# Manage system user accounts
		#
		user=$(GET adduser)
		passwd=$(GET passwd)
		if [ -n "$user" ]; then
			adduser -D -s /bin/sh -g "SliTaz User" -G users -h /home/$user $user
			echo "$user:$passwd" | chpasswd -m | log
			for g in audio cdrom floppy video tty
			do
				addgroup $user $g
			done
		fi ;;
	*\ gen_locale\ *)
		new_locale=$(GET gen_locale) ;;
	*\ gen_keymap\ *)
		new_keymap=$(GET gen_keymap) ;;
	*\ apply_xorg_kbd\ *)
		sed -i "s/XkbLayout.*/XkbLayout \" \"$(GET apply_xorg_kbd)\"/" \
			/etc/X11/xorg.conf.d/40-Keyboard.conf ;;
	*\ rdate\ *)
		rdate -s tick.greyware.com ;;
	*\ hwclock\ *)
		hwclock -w -u ;;
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
<a name="users"></a>
<h3>`gettext "Manage users"`</h3>
<form method="get" action="$SCRIPT_NAME">
<div id="actions">
	<div class="float-left">
		$(gettext "Selection:")
		<input type="submit" name="do" value="`gettext "Delete user"`" />
		<input type="submit" name="do" value="`gettext "Lock user"`" />
		<input type="submit" name="do" value="`gettext "Unlock user"`" />
	</div>
</div>
EOT
		table_start
		cat << EOT
<tr class="thead">
	<td>`gettext "Login"`</td>
	<td>`gettext "User ID"`</td>
	<td>`gettext "Name"`</td>
	<td>`gettext "Home"`</td>
	<td>`gettext "Shell"`</td>
</tr>
EOT
		for login in `cat /etc/passwd | cut -d ":" -f 1`
		do
			if [ -d /home/$login ]; then
				colorlogin=$login
				grep -qs "^$login:!" /etc/shadow &&
					colorlogin="<span style='color: red;'>$login</span>"
				IFS=':'
				set -- $(grep "^$login:" /etc/passwd)
				unset IFS
				uid=$3
				gid=$4
				name="$(echo $5 | sed s/,.*//)"
				home="$6"
				shell=$7
				cat <<EOT
<tr>
	<td><input type='checkbox' name='user' value='$login' />
		<img src='$IMAGES/user.png' />$colorlogin</td>
	<td>$uid:$gid</td>
	<td>$name</td>
	<td>$home</td>
	<td>$shell</td>
</tr>
EOT
			fi
		done
		table_end
		cat << EOT
<p>
	$(gettext "Password":)
	<input type="password" name="password" />
	<input type="submit" name="do" value="`gettext "Change password"`" />
</p>
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

<h4>`gettext "Current user sessions"`</h4>
<pre>
$(who)
</pre>

<h4>`gettext "Last user sessions"`</h4>
<pre>
$(last)
</pre>
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

<a name="keymap"></a>
<h3>`gettext "Console keymap"`</h3>
<p>
EOT
		# Check if a new keymap was requested
		if [ -n "$new_keymap" ]; then
			echo "$new_keymap" > /etc/keymap.conf
			if [ -x /bin/loadkeys ]; then
				loadkeys $new_keymap
			else
				loadkmap < /usr/share/kmap/$new_keymap.kmap
			fi
		fi
		gettext "Current console keymap: "
		keymap=$(cat /etc/keymap.conf)
		echo $keymap
		echo "</p>"
		if [ -n "$keymap" ]; then
			case "$keymap" in
			fr_CH*)
				keymap="ch" ;;
			ru)
				keymap="us,ru(winkeys)" ;;
			slovene)
				keymap=si ;;
			*)
				keymap=${keymap%-lat*}
				keymap=${keymap%-abnt2} ;;
			esac
			keyboard_config=/etc/X11/xorg.conf.d/40-Keyboard.conf
			cat << EOT
<form method="get" action="$SCRIPT_NAME">
	$(gettext "Suggested keymap for Xorg:")
	<input type="submit" name "apply_xorg_kbd" value="$keymap" />
	<a class="button" href="index.cgi?file=$keyboard_config">
		<img src="$IMAGES/edit.png" />$(gettext "Edit")</a>
</form>
EOT
		fi
		cat << EOT
<form method="get" action="$SCRIPT_NAME">
	$(gettext "Available keymaps:")
	<select name="gen_keymap">
		$(list_keymaps)
	</select>
	<input type="submit" value="$(gettext "Activate")" />
</form>

<h2>$(gettext "Panel configuration")</h2>
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
