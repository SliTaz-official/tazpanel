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

TITLE=$(gettext 'TazPanel - Settings')

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
			[ "$(GET do)" == "$(gettext "$cmd")" ] || continue			# BUGGY
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
<h3 id="users">$(gettext 'Manage users')</h3>

<form method="get" action="$SCRIPT_NAME">
<div id="actions">
	<div class="float-left">
		$(gettext 'Selection:')
		<input type="submit" name="do" value="$(gettext 'Delete user')" />
		<input type="submit" name="do" value="$(gettext 'Lock user')" />
		<input type="submit" name="do" value="$(gettext 'Unlock user')" />
	</div>
</div>

<table class="zebra outbox">
<thead>
<tr class="thead">
	<td>$(gettext 'Login')</td>
	<td>$(gettext 'User ID')</td>
	<td>$(gettext 'Name')</td>
	<td>$(gettext 'Home')</td>
	<td>$(gettext 'Shell')</td>
</tr>
</thead>
</tbody>
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
		cat << EOT
</tbody>
</table>
EOT
		cat << EOT
<p>
	$(gettext 'Password:')
	<input type="password" name="password" />
	<input type="submit" name="do" value="$(gettext 'Change password')" />
</p>
</form>

<section>
<h4>$(gettext 'Add a new user')</h4>

<form method="get" action="$SCRIPT_NAME">
	<input type="hidden" name="user" />
	<table>
		<tr><td>$(gettext 'User login:')</td>
			<td><input type="text" name="adduser" size="30" /></td></tr>
		<tr><td>$(gettext 'User password:')</td>
			<td><input type="password" name="passwd" size="30" /></td></tr>
		<tr><td colspan="2">
			<input type="submit" value="$(gettext 'Create user')" /></td></tr>
	</table>
</form>
</section>

<section>
<h4>$(gettext 'Current user sessions')</h4>

<pre>$(who)</pre>
</section>

<section>
<h4>$(gettext 'Last user sessions')</h4>

<pre>$(last)</pre>
</section>
EOT
		;;


	*\ locale*)
		#
		# Choose locale
		#
		LOADING_MSG="$(gettext 'Please wait...')"
		loading_msg
		cur_loc=$(locale | grep LANG | cut -d= -f2)
		cat << EOT
<h3 id="locale">$(gettext 'Choose locale')</h3>

<p>$(gettext 'Current locale settings:')</p>
<pre>$(locale)</pre>

<p>$(gettext 'Locales that are currently installed on the machine:')</p>
<pre>$(locale -a)</pre>

<p>$(gettext 'Available locales:')</p>
EOT

		is_installed "glibc-locale"
		[ $? = 1 ] &&
			msg tip $(gettext \
			"Can't see your language?<br/>You can \
<a href='/pkgs.cgi?do=Install&glibc-locale'>install glibc-locale</a> \
to see a larger list of available locales.")

		cat << EOT
<form method="get" action="$SCRIPT_NAME">
	<div class="outbox">
	<table class="zebra fixed">
	<thead>
		<tr><td style="width:9em">$(gettext 'Code')</td>
			<td style="width:10em">$(gettext 'Language')</td>
			<td style="width:10em">$(gettext 'Territory')</td>
			<td>$(gettext 'Description')</td>
		</tr>
	</thead>
	</table>

	<div style="max-height: 16em; overflow:auto">
	<table class="zebra fixed">
		<col style="width:9em">
		<col style="width:10em">
		<col style="width:10em">
		<col>
	<tbody style="max-height:10em; overflow:auto">
EOT
	for locale in $(find /usr/share/i18n/locales -type f | sort)
	do
		locale_name=$(basename $locale)
		locale_title=$(grep -m 1 -e '^	*title' $locale | cut -d'"' -f2)
		if [ -n "$locale_title" ]; then
			sel=""; [ "$locale_name" == "$cur_loc" ] && sel="checked"
			cat << EOT
		<tr><td><input type="radio" name="gen_locale" value="$locale_name" $sel />$locale_name</td>
			<td>$(gettext -d iso_639 "$(grep -m 1 -e '^	*language' $locale | cut -d '"' -f2)")</td>
			<td>$(gettext -d iso_3166 "$(grep -m 1 -e '^	*territory' $locale | cut -d '"' -f2)")</td>
			<td>$locale_title</td>
		</tr>
EOT
		fi
	done
	cat << EOT
	</tbody>
	</table>
	</div>
	</div>
	<p><input type="submit" value="$(gettext 'Activate')" /></p>
</form>
EOT
		;;


	*)
		#
		# Defaut system settings page
		#
		cat << EOT
<div id="wrapper">
	<h2>$(gettext 'System settings')</h2>
	<p>$(gettext 'Manage system time, users or language settings')<p>
</div>
<div id="actions">
	<a class="button" href="$SCRIPT_NAME?users">
		<img src="$IMAGES/users.png" />$(gettext 'Manage users')</a>
</div>

<section>
<h3>$(gettext 'System time')</h3>

<table>
	<tr><td>$(gettext 'Time zome:')</td><td>$(cat /etc/TZ)
		<a class="button" href="$SCRIPT_NAME">$(gettext 'Change')</a></td></tr>
	<tr><td>$(gettext 'System time:')</td><td>$(date)</td></tr>
	<tr><td>$(gettext 'Hardware clock:')</td><td>$(hwclock -r)</tr>
</table>
<a class="button" href="$SCRIPT_NAME?rdate">$(gettext 'Sync online')</a>
<a class="button" href="$SCRIPT_NAME?hwclock">$(gettext 'Set hardware clock')</a>
</section>
EOT
		#
		# Locale settings
		#
		cat << EOT
<section>
<h3 id="locale">$(gettext 'System language')</h3>
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
			msg warn "$(eval_gettext \
			'You must logout and login again to your current session to use $new_locale locale.')"
		else
			gettext 'Current system locale:'; echo -n " <strong>"
			locale | grep LANG | cut -d= -f2
		fi
		cat << EOT
</strong> <a class="button" href="$SCRIPT_NAME?locale">$(gettext 'Change')</a></p>
</section>

<section>
<h3 id="keymap">$(gettext 'Console keymap')</h3>
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
		keymap=$(cat /etc/keymap.conf)
		eval_gettext 'Current console keymap: $keymap'
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
	$(gettext 'Suggested keymap for Xorg:')
	<input type="submit" name "apply_xorg_kbd" value="$keymap" />
	<a class="button" href="index.cgi?file=$keyboard_config">
		<img src="$IMAGES/edit.png" />$(gettext 'Edit')</a>
</form>
EOT
		fi
		cat << EOT
<form method="get" action="$SCRIPT_NAME">
	$(gettext 'Available keymaps:')
	<select name="gen_keymap">
		$(list_keymaps)
	</select>
	<input type="submit" value="$(gettext 'Activate')" />
</form>
</section>

<section>
<h2>$(gettext 'Panel configuration')</h2>

<form method="get" action="$SCRIPT_NAME">
	<p>
		$(gettext 'Style:')
		<select name="style">
			$(list_styles)
		</select>
		<input type="submit" value="$(gettext 'Activate')" />
	</p>
</form>
<form method="get" action="$SCRIPT_NAME">
	<p>
		$(gettext 'Panel password:')
		<input type="password" name="panel_pass"/>
		<input type="submit" value="$(gettext 'Change')" />
	</p>
</form>
<p>
	$(gettext 'Configuration files:')
	<a class="button" href="index.cgi?file=$CONFIG">
		<img src="$IMAGES/edit.png" />$(gettext 'Panel')</a>
	<a class="button" href="index.cgi?file=$HTTPD_CONF">
		<img src="$IMAGES/edit.png" />$(gettext 'Server')</a>
</p>
<p>
	$(gettext 'TazPanel provides a debuging mode and page:')
	<a href="/index.cgi?debug">debug</a>
</p>
</section>
EOT
	;;
esac

xhtml_footer
exit 0
