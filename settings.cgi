#!/bin/sh
#
# System settings CGI interface: user, locale, keyboard, date. Since we
# don't have multiple pages here there is only one case used to get command
# values and the full content is followed directly.
#
# Copyright (C) 2011-2015 SliTaz GNU/Linux - BSD License
#


# Common functions from libtazpanel

. lib/libtazpanel
get_config
header

TITLE=$(gettext 'TazPanel - Settings')


# Get system database. LDAP compatible.

getdb()
{
	getent $1 2>/dev/null || cat /etc/$1
}

listdb()
{
	for item in $(getdb $1 | cut -d ":" -f 1); do
		echo "<option>$item</option>\n"
	done
}


#############################
# Get info from locale file #
#############################

get_locale_info()
{
	# Commands like `LC_ALL=fr_FR locale -k LC_MEASUREMENT` will do the job
	#   only when your locale is generated and exists in the /usr/lib/locale.
	# Here we manually parse locale definition files from /usr/share/i18n/locales/.
	# Strange, bloated and not script-friendly format :(

	[ ! -e /usr/share/i18n/locales/$1 ] && return

	# Prepare file
	if [ ! -e /tmp/tazpanel-$1 ]; then
		sed 's|^[ \t]*||;/^%/d;/^comment_char/d;/^escape_char/d' /usr/share/i18n/locales/$1 | tr '\n' '&' | sed 's|/&||g' | tr '&' '\n' | sed 's|<U\([0-9a-fA-F]*\)>|\&#x\1;|g' | sed 's|&#x00|\&#x|g' > /tmp/tazpanel-$1
	fi

	local ANS=$(grep -e "^$2[ 	]" /tmp/tazpanel-$1 | sed 's|^[^ \t][^ \t]* *||')
	if [ -z "$ANS" ]; then
		# Not found, then section is copied from other locale definition file...
		case $2 in
			measurement)
				section='LC_MEASUREMENT';;
			width|height)
				section='LC_PAPER';;
			currency_symbol|int_curr_symbol)
				section='LC_MONETARY';;
			day|abday|mon|abmon|d_t_fmt|d_fmt|t_fmt|am_pm|t_fmt_ampm|date_fmt)
				section='LC_TIME';;
		esac
		# Recursive call
		get_locale_info $(sed -n '/^'$section'/,/^END '$section'/p' /tmp/tazpanel-$1 | grep 'copy' | cut -d'"' -f2) $2
	else
		case $2 in
			day|abday|mon|abmon|am_pm)		# semicolon-separated list in double quotes
				echo "$ANS";;
			*)		# single value in double qoutes
				echo "$ANS" | cut -d'"' -f2;;
		esac
	fi
}


# Get info from locale file about measurement system

get_locale_info_measurement()
{
	# faster to use pre-processed values
	case $1 in
		en_AG|en_US|es_PR|es_US|nl_AW|yi_US) gettext 'US' ;;
		POSIX) ;;
		*) gettext 'metric' ;;
	esac
}


# Get info from locale file about paper size

get_locale_info_paper()
{
	# faster to use pre-processed values
	case $1 in
		en_AG|en_US|es_PR|es_US|nl_AW|yi_US) echo '8½×11 (US Letter)';;
		en_CA|en_PH|es_CL|es_CO|es_CR|es_GT|es_MX|es_NI|es_PA|es_SV|es_VE|fil_PH|fr_CA|ik_CA|iu_CA|shs_CA|tl_PH) echo '216×279 (US Letter)';;
		POSIX) ;;
		*) echo '210×297 (A4)';;
	esac
}


# Get info from locale file about date and time format

get_locale_info_date_time()
{
	case $2 in
		c) get_locale_info $1 d_t_fmt ;;
		x) get_locale_info $1 d_fmt ;;
		X) get_locale_info $1 t_fmt ;;
		r) get_locale_info $1 t_fmt_ampm ;;
		*) get_locale_info $1 date_fmt ;;
	esac | sed 's|&#x20;| |g; s|&#x25;|%|g; s|&#x2C;|,|g; s|&#x2D;|-|g; s|&#x2E;|.|g; s|&#x2F;|/|g; s|&#x3A;|:|g; s|&#x41;|A|g; s|&#x42;|B|g; s|&#x43;|C|g; s|&#x46;|F|g; s|&#x48;|H|g; s|&#x49;|I|g; s|&#x4D;|M|g; s|&#x4F;|O|g; s|&#x52;|R|g; s|&#x53;|S|g; s|&#x54;|T|g; s|&#x58;|X|g; s|&#x59;|Y|g; s|&#x5A;|Z|g; s|&#x61;|a|g; s|&#x62;|b|g; s|&#x65;|e|g; s|&#x64;|d|g; s|&#x6B;|k|g; s|&#x6D;|m|g; s|&#x6E;|n|g; s|&#x6F;|o|g; s|&#x70;|p|g; s|&#x72;|r|g; s|&#x74;|t|g; s|&#x78;|x|g; s|&#x79;|y|g; s|&#x7A;|z|g;'

}


parse_date()
{
	local weekday month day abday mon abmon rtime d_fmt t_fmt am_pm
	weekday=$(( $(date +%w) + 1 ))											# 1=Sunday ...
	  month=$(date +%-m)													# 1=January ...
	  day=$(get_locale_info $1   day | cut -d'"' -f$(( 2 * $weekday )) | sed 's|&|\\\&|g')	# translated day of week
	abday=$(get_locale_info $1 abday | cut -d'"' -f$(( 2 * $weekday )) | sed 's|&|\\\&|g')	#   same, abbreviated
	  mon=$(get_locale_info $1   mon | cut -d'"' -f$(( 2 * $month   )) | sed 's|&|\\\&|g')	# translated month
	abmon=$(get_locale_info $1 abmon | cut -d'"' -f$(( 2 * $month   )) | sed 's|&|\\\&|g')	#   same, abbreviated
	# next %-codes expanded into other %-codes
	rtime=$(get_locale_info_date_time $1 r | sed 's|&|\\\&|g')									# %r: 12-hour time
	d_fmt=$(get_locale_info_date_time $1 x | sed 's|&|\\\&|g')									# %x: date
	t_fmt=$(get_locale_info_date_time $1 X | sed 's|&|\\\&|g')									# %X: time

	case $(LC_ALL=POSIX date +%P) in										# translated am/pm
		am) am_pm=$(get_locale_info $1 am_pm | cut -d'"' -f2 | sed 's|&|\\\&|g');;
		pm) am_pm=$(get_locale_info $1 am_pm | cut -d'"' -f4 | sed 's|&|\\\&|g');;
	esac

	# r x X | OC | Y y Oy Ey | m -m Om | d -d Od | e -e Oe | F | H OH k | I OI l | M OM | S OS | R T | Z z | t | P p Op A a B b
	# Note: %P=am/pm; %p=AM/PM. But here they the same because it is not a simple job to convert letters.
	echo "$2" | sed "s|%r|$rtime|; s|%x|$d_fmt|; s|%X|$t_fmt|; \
		s|%OC|S(date +%OC)|; \
		s|%Y|$(date +%Y)|; s|%y|$(date  +%y )|; s|%Oy|$(date +%Oy)|; s|%Ey|$(date +%Ey)|; \
		s|%m|$(date +%m)|; s|%-m|$(date +%-m)|; s|%Om|$(date +%Om)|; \
		s|%d|$(date +%d)|; s|%-d|$(date +%-d)|; s|%Od|$(date +%Od)|; \
		s|%e|$(date +%e)|; s|%-e|$(date +%-e)|; s|%Oe|$(date +%Oe)|; \
		s|%F|$(date +%F)|; \
		s|%H|$(date +%H)|; s|%OH|$(date +%OH)|; s|%k|$(date +%k)|; \
		s|%I|$(date +%I)|; s|%OI|$(date +%OI)|; s|%l|$(date +%l)|; \
		s|%M|$(date +%M)|; s|%OM|$(date +%OM)|; \
		s|%S|$(date +%S)|; s|%OS|$(date +%OS)|; \
		s|%R|$(date +%R)|; s|%T|$(date  +%T )|; \
		s|%Z|$(date +%Z)|; s|%z|$(date  +%z )|; \
		s|%t|\t|; \
		s|%P|$am_pm|; s|%p|$am_pm|; s|%Op|$am_pm|; s|%A|$day|; s|%a|$abday|; s|%B|$mon|; s|%b|$abmon|;"

}

list_of()
{
	cd /usr/share/i18n/locales
	#mon=$(date +%-m); monn=$(( $mon * 2 ))
	#echo "mon=\"$mon\" monn=\"$monn\""

	echo '<pre>'
for LOC in be_BY ca_IT el_CY fr_CH ru_RU ru_UA; do
	case $LOC in
		iso*|translit*) ;;
		*)
			#echo -e "$LOC:\t$(parse_date $LOC $(get_locale_info_date_time $LOC c | sed 's|&|\\\&|g'))";;
			FMT="$(get_locale_info_date_time $LOC c)"
			echo -e "$LOC:\t$FMT"
			parse_date $LOC "$FMT"
			echo;;
	esac
done
	echo '</pre>'
}





#
# Commands executed before page loading.
#

case " $(GET) " in
	*\ do\ *)
		 users=$(echo $QUERY_STRING | awk 'BEGIN{RS="&";FS="="}{if($1=="user") print $2}')
		groups=$(echo $QUERY_STRING | awk 'BEGIN{RS="&";FS="="}{if($1=="group")print $2}')

		case $(GET do) in

			# Groups page
			delgroups)
				for i in $groups; do delgroup $i; done ;;
			addgroup)
				addgroup $groups ;;
			addmember)
				addgroup $(GET member) $groups ;;
			delmember)
				delgroup $(GET member) $groups ;;

			# Users page
			delusers)
				for i in $users; do deluser $i; done ;;
			lockusers)
				for i in $users; do passwd -l $i | log; done ;;
			unlockusers)
				for i in $users; do passwd -u $i | log; done ;;
			chpasswd)
				echo "$users:$(GET password)" | chpasswd -m | log ;;
			adduser)
				if [ -n "$users" ]; then
					name=$(GET name); name=${name:-SliTaz User}
					adduser -D -s /bin/sh -g "$name" -G users -h /home/$users $users
					echo "$user:$(GET passwd)" | chpasswd -m | log
					for i in audio cdrom floppy video tty; do addgroup $users $i; done
				fi ;;

			# System time
			settz)
				GET tz > /etc/TZ;;
			date) # normalize to two digits
				date $(printf '%02d%02d%02d%02d%d.%02d' "$(GET month)" "$(GET day)" "$(GET hour)" "$(GET min)" "$(GET year)" "$(GET sec)") >/dev/null;;
			rdate)
				rdate -s tick.greyware.com ;;
			hwclock)
				hwclock -w -u ;;

		esac
		;;


	*\ gen_locale\ *)
		new_locale=$(GET gen_locale) ;;
	*\ gen_keymap\ *)
		new_keymap=$(GET gen_keymap) ;;
	*\ apply_xorg_kbd\ *)
		sed -i "s/XkbLayout.*/XkbLayout \" \"$(GET apply_xorg_kbd)\"/" \
			/etc/X11/xorg.conf.d/40-Keyboard.conf ;;
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
	*\ group*)
		#
		# Groups management
		#
		cat <<EOT
<h2 id="groups">$(gettext 'Manage groups')</h2>


<section>
	<form class="wide">
		<header>
			<input type="hidden" name="groups"/>
			<!-- $(gettext 'Selection:') -->
			<button name="do" value="delgroups" data-icon="delete">$(gettext 'Delete group')</button>
		</header>

		<div class="scroll">
			<table class="wide zebra scroll">
				<thead>
					<tr class="thead">
						<td>$(gettext 'Group')</td>
						<td>$(gettext 'Group ID')</td>
						<td>$(gettext 'Members')</td>
					</tr>
				</thead>
				<tbody>
EOT
		for group in $(getdb group | cut -d ":" -f 1); do
			IFS=':'
			set -- $(getdb group | grep "^$group:")
			unset IFS
			gid=$3
			members=$4
			cat <<EOT
					<tr>
						<td><input type="checkbox" name="group" value="$group" id="$group"/>
							<label for="$group" data-icon="group">$group</label></td>
						<td>$gid</td>
						<td>${members//,/, }</td>
					</tr>
EOT
		done
		cat <<EOT
				</tbody>
			</table>
		</div>
	</form>
</section>


<section>
	<header>$(gettext 'Add a new group')</header>
	<form>
		<input type="hidden" name="groups"/>
		<table>
			<tr><td>$(gettext 'Group name:')</td>
				<td><input type="text" name="group"/></td>
			</tr>
			<tr><td colspan="2">
				<button type="submit" name="do" value="addgroup" data-icon="add">$(gettext 'Create group')</button>
			</td></tr>
		</table>
	</form>
</section>


<section>
	<header>$(gettext 'Manage group membership')</header>
	<form>
		<input type="hidden" name="groups"/>
		<table>
			<tr>
				<td>$(gettext 'Group name:')</td>
				<td><select name="group">$(listdb group)</select></td>
				<td>$(gettext 'User name:')</td>
				<td><select name="member">$(listdb passwd)</select></td>
			</tr>
			<tr>
				<td colspan="2">
					<button name="do" value="addmember" data-icon="add">$(gettext 'Add user')</button>
				</td>
				<td colspan="2">
					<button name="do" value="delmember" data-icon="delete">$(gettext 'Remove user')</button>
				</td>
			</tr>
		</table>
	</form>
</section>

EOT
		;;


	*\ user*)
		#
		# Users management
		#
		cat <<EOT
<h2 id="users">$(gettext 'Manage users')</h2>

<section>
	<form class="wide">
		<header>
			<!--$(gettext 'Selection:')-->
			<button name="do" value="delusers"    data-icon="delete">$(gettext 'Delete user')</button>
			<button name="do" value="lockusers"   data-icon="lock"  >$(gettext 'Lock user'  )</button>
			<button name="do" value="unlockusers" data-icon="unlock">$(gettext 'Unlock user')</button>
		</header>

		<table class="wide zebra center">
			<thead>
				<tr>
					<td>$(gettext 'Login')</td>
					<td>$(gettext 'User ID')</td>
					<td>$(gettext 'Name')</td>
					<td>$(gettext 'Home')</td>
					<td>$(gettext 'Shell')</td>
				</tr>
			</thead>
			</tbody>
EOT
		for login in $(getdb passwd | cut -d ":" -f 1); do
			if [ -d /home/$login ]; then
				colorlogin=$login
				grep -qs "^$login:!" /etc/shadow &&
					colorlogin="<span style='color: red;'>$login</span>"
				IFS=':'
				set -- $(getdb passwd | grep "^$login:")
				unset IFS
				cat <<EOT
<tr>
	<td style="white-space: nowrap">
		<input type="checkbox" name="user" value="$login" id="$login"/>
		<label for="$login" data-icon="user">$colorlogin</label></td>
	<td>$3:$4</td>
	<td>$(echo $5 | sed s/,.*//)</td>
	<td>$6</td>
	<td>$7</td>
</tr>
EOT
			fi
		done
		cat <<EOT
			</tbody>
		</table>
EOT
		cat <<EOT
		<footer>
			<div>
				$(gettext 'Password:')
				<input type="password" name="password"/>
				<button type="submit" name="do" value="chpasswd" data-icon="ok">$(gettext 'Change password')</button>
			</div>
		</footer>
	</form>
</section>


<section>
	<header>$(gettext 'Add a new user')</header>

	<form>
		<input type="hidden" name="users"/>
		<table class="summary">
			<tr><td>$(gettext 'User login:')</td>
				<td><input type="text" name="user" size="30" pattern="[a-z]*"/></td></tr>
			<tr><td>$(gettext 'User name:')</td>
				<td><input type="text" name="name" size="30"/></td></tr>
			<tr><td>$(gettext 'User password:')</td>
				<td><input type="password" name="passwd" size="30"/></td></tr>
		</table>

		<footer>
			<button type="submit" name="do" value="adduser" data-icon="add">$(gettext 'Create user')</button>
		</footer>
	</form>
</section>


<section>
	<header>$(gettext 'Current user sessions')</header>
	<pre>$(who)</pre>
</section>


<section>
	<header>$(gettext 'Last user sessions')</header>
	<div class="scroll"><pre>$(last)</pre></div>
</section>
EOT
		;;


	*\ locale*)
		#
		# Choose locale
		#
		LOADING_MSG="$(gettext 'Please wait...')"; loading_msg

		cur_loc=$(locale | grep LANG | cut -d= -f2)
		cat <<EOT
<h2 id="locale">$(gettext 'Choose locale')</h2>

<section>
	<header>$(gettext 'Current locale settings:')</header>
	<div>
		<pre>$(locale)</pre>
	</div>
</section>

<section>
	<header>$(gettext 'Locales that are currently installed on the machine:')</header>
	<div>
		<pre>$(locale -a)</pre>
	</div>
</section>
EOT

		is_installed "glibc-locale"
		[ $? = 1 ] &&
			msg tip $(gettext \
			"Can't see your language?<br/>You can \
<a href='/pkgs.cgi?do=Install&amp;glibc-locale'>install glibc-locale</a> \
to see a larger list of available locales.")


		cat <<EOT
<section>
	<header>$(gettext 'Available locales:')</header>
	<form class="wide">
		<table class="wide zebra">
			<thead>
				<tr><td>$(gettext 'Code')</td>
					<td>$(gettext 'Language')</td>
					<td>$(gettext 'Territory')</td>
					<td>$(gettext 'Description')</td>
				</tr>
			</thead>
			<tbody>
EOT
	for locale in $(find /usr/share/i18n/locales -type f | sort); do
		locale_name=$(basename $locale)
		locale_title=$(grep -m 1 -e '^	*title' $locale | cut -d'"' -f2)
		if [ -n "$locale_title" ]; then
			sel=''; [ "$locale_name" == "$cur_loc" ] && sel='checked="checked"'
			cat <<EOT
				<tr>
					<td>
						<input type="radio" name="gen_locale" value="$locale_name" $sel id="$locale_name"/>
						<label for="$locale_name">$locale_name</label>
					</td>
					<td>$(gettext -d iso_639  "$(grep -m 1 -e '^	*language'  $locale | cut -d '"' -f2)")</td>
					<td>$(gettext -d iso_3166 "$(grep -m 1 -e '^	*territory' $locale | cut -d '"' -f2)")</td>
					<td>$locale_title</td>
				</tr>
EOT
		fi
	done
	cat <<EOT
			</tbody>
		</table>

		<footer>
			<button type="submit" data-icon="ok">$(gettext 'Activate')</button>
		</footer>
	</form>
</section>
EOT
		;;


	*)
		#
		# Default system settings page
		#
		list_of
		cat <<EOT
<h2>$(gettext 'System settings')</h2>

<p>$(gettext 'Manage system time, users or language settings')<p>

<form><!--
	--><button name="users"  data-icon="user" >$(gettext 'Manage users' )</button><!--
	--><button name="groups" data-icon="group">$(gettext 'Manage groups')</button>
</form>

<section>
	<header>$(gettext 'System time')</header>
	<div>
	<form class="wide">
		<fieldset><legend>$(gettext 'Time zone:')</legend>
			<select name="tz">
				$(cd /usr/share/zoneinfo; find * -type f ! -name '*.tab' | sort | \
				awk -vtz="$(cat /etc/TZ)" \
				'{printf("<option%s>%s</option>", ($1 == tz)?" selected":"", $1)}')
			</select>
			<button name="do" value="settz" data-icon="ok">$(gettext 'Change')</button>
		</fieldset>
		<fieldset><legend>$(gettext 'System time:')</legend>
			$(date | sed 's|[0-9][0-9]:[0-9:]*|<span id="time">&</span>|')
			<button name="do" value="rdate" data-icon="sync">$(gettext 'Sync online')</button>
		</fieldset>
		<fieldset><legend>$(gettext 'Hardware clock:')</legend>
			$(hwclock -ur | sed 's|0.000000 seconds||')
			<button name="do" value="hwclock" data-icon="clock">$(gettext 'Set hardware clock')</button>
		</fieldset>
		<fieldset><legend>$(gettext 'Set date')</legend>
			<input type="number" name="day" value="$(date +%d)" min="1" max="31" size="4" required/>
			<select name="month" value="$(date +%m)">
				$(for i in $(seq 12); do
					printf '<option value="%s">%s</option>' $(date -d $i.01-01:01 '+%m %B')
				done)
			</select>
			<input type="number" name="year" value="$(date +%Y)" min="2015" max="2030" size="6" required/>
		-	<input type="number" name="hour" value="$(date +%H)" min="0"    max="23"   size="4" required/><!--
		-->:<input type="number" name="min"  value="$(date +%M)" min="0"    max="59"   size="4" required/><!--
		-->:<input type="number" name="sec"  value="00"          min="0"    max="59"   size="4" required/>
			<button name="do" value="date" data-icon="ok">$(gettext 'Set date')</button>
		</fieldset>
	</form>
	</div>

<script type="text/javascript">
// Live time on page
Date.prototype.timeNow = function() {
	return ((this.getHours() < 10)?"0":"") + this.getHours() + ":" + ((this.getMinutes() < 10)?"0":"") + this.getMinutes() + ":" + ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
}
setInterval(function(){document.getElementById('time').innerText = new Date().timeNow()}, 1000);
</script>
</section>
EOT


		#
		# Locale settings
		#
		cat <<EOT
<section>
	<header id="locale">$(gettext 'System language')</header>
	<div>
	<form>
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
			cat <<EOT
		$(gettext 'Current system locale:')
		<strong>$(locale | grep LANG | cut -d= -f2)</strong>
		<button name="locale" data-icon="locale">$(gettext 'Change')</button>
EOT
		fi
		cat <<EOT
	</div>
	</form>
</section>


<section>
	<header id="keymap">$(gettext 'Keyboard layout')</header>
	<div>
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
		if [ -n "$keymap" ]; then
			case "$keymap" in
			fr_CH*)
				keymap="ch" ;;
			ru)
				keymap="us,ru" ;;
			slovene)
				keymap=si ;;
			*)
				keymap=${keymap%-lat*}
				keymap=${keymap%-abnt2} ;;
			esac
			keyboard_config=/etc/X11/xorg.conf.d/40-Keyboard.conf
			cat <<EOT
		<form id="settings"></form>
		<form id="index" action="index.cgi"></form>
		<br/>
		$(gettext 'Suggested keymap for Xorg:') $keymap
		<button form="settings" name="apply_xorg_kbd" value="$keymap" data-icon="ok">$(gettext 'Activate')</button>
		<button form="index" name="file" value="$keyboard_config" data-icon="edit">$(gettext 'Edit')</button>
		<br/>
EOT
		fi
		cat <<EOT
		<form>
			$(gettext 'Available keymaps:')
			<select name="gen_keymap">
				$(list_keymaps)
			</select>
			<button type="submit" data-icon="ok">$(gettext 'Activate')</button>
		</form>
	</div>
</section>


<section>
	<header>$(gettext 'Panel configuration')</header>
	<div>
	<form class="wide">
		<fieldset><legend>$(gettext 'Style:')</legend>
			<select name="style">$(list_styles)</select>
			<button data-icon="ok">$(gettext 'Activate')</button>
		</fieldset>

		<fieldset><legend>$(gettext 'Panel password:')</legend>
			<input type="password" name="panel_pass"/>
			<button data-icon="ok">$(gettext 'Change')</button>
		</fieldset>
	</form>

	<fieldset><legend>$(gettext 'Configuration files:')</legend>
		<button form="index" name="file" value="$CONFIG" data-icon="edit">$(gettext 'Panel')</button>
		<button form="index" name="file" value="$HTTPD_CONF" data-icon="edit">$(gettext 'Server')</button>
	</fieldset>

	<p>$(gettext 'TazPanel provides a debugging mode and page:')
		<a href="/index.cgi?debug">debug</a>
	</p>
	</div>
</section>
EOT
	;;
esac

xhtml_footer
exit 0
