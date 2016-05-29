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

TITLE=$(_ 'System settings')


listdb() {
	for item in $(getdb $1 | cut -d: -f1); do
		echo "<option>$item</option>\n"
	done
}


restart_lxpanel() {
	# `lxpanelctl restart` exists, but it breaks often leaving us without any panel

	# parameters needed to run graphical application from script
	if [ -z "$XAUTHORITY" ]; then
		if [ -e "$HOME/.Xauthority" ]; then
			export XAUTHORITY="$HOME/.Xauthority"
		elif [ -e '/var/run/slim.auth' ]; then
			export XAUTHORITY='/var/run/slim.auth'
		fi
	fi
	[ -z "$DISPLAY" ] && export DISPLAY=':0.0'

	# find LXPanel ProcessID, filter out zombie '[lxpanel]' (if any)
	lxpanel_pid="$(ps -o comm,pid,args 2>/dev/null | grep lxpanel | grep -v -E 'grep|sh|\[' | awk '{print $2}')"

	# if LXPanel not running, just run it with default option
	if [ -z "$lxpanel_pid" ]; then
		(pstree | grep -q pcmanfm) && pcmanfm /etc/xdg/autostart/lxpanel.desktop ||
			sh -l -c "lxpanel -p slitaz" &
	else
		# who started LXPanel?..
		lxpanel_user="$(ps -o pid,user 2>/dev/null | fgrep "$lxpanel_pid " | awk '{print $2}')"

		# ... current user?
		if [ "$USER" == "$lxpanel_user" ]; then
			# custom command?
			lxpanel_comm="$(ps -o pid,args 2>/dev/null | grep -e "^\ *$lxpanel_pid " | awk '{$1="";print}')"
			[ -z "$lxpanel_comm" ] && lxpanel_comm='lxpanel -p slitaz'

			# stop LXPanel and start it again with the same command
			kill $lxpanel_pid
			(pstree | grep -q pcmanfm) && pcmanfm /etc/xdg/autostart/lxpanel.desktop ||
				sh -l -c "$lxpanel_comm" &
		fi
	fi

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
			delgroups) for i in $groups; do delgroup $i; done ;;
			addgroup)  addgroup $groups ;;
			addmember) addgroup $(GET member) $groups ;;
			delmember) delgroup $(GET member) $groups ;;

			# Users page
			delusers)    for i in $users; do deluser $i; done ;;
			lockusers)   for i in $users; do passwd -l $i | log; done ;;
			unlockusers) for i in $users; do passwd -u $i | log; done ;;
			chpasswd)    echo "$users:$(GET password)" | chpasswd -m | log ;;
			adduser)
				if [ -n "$users" ]; then
					name="$(GET name)"
					adduser -D -s /bin/sh -g "${name:-SliTaz User}" -G users -h /home/$users $users
					echo "$user:$(GET passwd)" | chpasswd -m | log
					for i in audio cdrom floppy video tty; do addgroup $users $i; done
					passwd -u $users | log
				fi ;;

			# System time
			calendar)
				# display Yad date picker (AJAX)
				new_date="$(DISPLAY=':0.0' XAUTHORITY='/var/run/slim.auth' \
					yad --calendar --on-top --mouse --undecorated \
					--window-icon=config-date --title="$(_ 'Set date')" \
					--date-format='%x<span style="display:none">%F</span>')"
				header
				echo "$new_date"; exit 0;;

			settz)
				# set timezone
				GET tz > /etc/TZ ;;

			date)
				# only accepted format is MMDDhhmm[[YY]YY][.ss]
				if [ -n "$(GET dateFull)" ]; then
					dateFull="$(GET dateFull)" # %F = YYYY-MM-DD
					date $(printf '%02d%02d%02d%02d%d.%02d' "${dateFull:5:2}" \
						"${dateFull:8:2}" "$(GET hour)" "$(GET min)" \
						"${dateFull:0:4}" "$(GET sec)") >/dev/null
				else
					date $(printf '%02d%02d%02d%02d%d.%02d' "$(GET month)" \
						"$(GET day)" "$(GET hour)" "$(GET min)" "$(GET year)" \
						"$(GET sec)") >/dev/null
				fi;;

			rdate)
				# get and possibly set the system date/time from a remote host
				sh -l -c "rdate -s tick.greyware.com" ;;

			hwclock)
				# query and set hardware clock (RTC)
				hwclock -w -u ;;

			gethwclock)
				# get date/time from hardware clock (AJAX)
				header; sh -l -c "hwclock -ur | sed 's|0.000000 seconds||'"; exit 0;;

		esac
		;;


	*\ gen_locale\ *) new_locale=$(GET gen_locale) ;;
	*\ gen_keymap\ *) new_keymap=$(GET gen_keymap) ;;

	*\ apply_xorg_kbd\ *)
		sed -i "s/XkbLayout.*/XkbLayout \" \"$(GET apply_xorg_kbd)\"/" \
			/etc/X11/xorg.conf.d/40-Keyboard.conf ;;
	*\ style*)
		sed -i s/'^STYLE.*'/"STYLE=\"$(GET style)\""/ $CONFIG
		. $CONFIG ;;


	*\ tweak\ *)
		HOME="$(getdb passwd | awk -F: -vu=$REMOTE_USER '$1==u{print $6}')"
		[ ! -d "$HOME" ] && exit 0

		dd="$HOME/.local/share/desktop-directories"; sd="$dd/SliTazMenu.directory"

		case "$REMOTE_USER" in
			root) color='31'; ind='#';;
			*)    color='32'; ind='$';;
		esac

		case $(GET tweak) in
			monochrome)
				# PS1='\u@\h:\w\$ '
				sed -i "s|^PS1=.*|PS1='\\\\u@\\\\h:\\\\w\\\\$ind '|" $HOME/.profile;;
			colored)
				# PS1='\[\e[0;32m\]\u@\h\[\e[0m\]:\[\e[0;33m\]\w\[\e[0m\]\$ '
				sed -i "s|^PS1=.*|PS1='\\\\\\[\\\\e\[0;${color}m\\\\\\]\\\\u@\\\\h\\\\\\[\\\\e\\[0m\\\\\\]:\\\\\\[\\\\e\\[0;33m\\\\\\]\\\\w\\\\\\[\\\\e\\[0m\\\\\\]\\\\$ind '|" $HOME/.profile;;
			slitaz-*)
				lxpanel="$HOME/.config/lxpanel"
				if [ ! -e "$lxpanel" ]; then
					mkdir -p "$lxpanel"; cp /etc/lxpanel/default /etc/lxpanel/slitaz $lxpanel
				fi

				for panel in $(find $lxpanel -type f -iname panel); do
					awk -vicon="/usr/share/pixmaps/$(GET tweak).png" '
					BEGIN{ found = "0"; }
					{
						if ($1 == "Plugin") { found = "1"; }

						if (found == "1" && $1 == "type") {
							if ($3 == "menu") found = "2"; else found = "0";
						}

						if (found == "2" && $1 == "Plugin") { found = "0"; }

						if (found == "2" && index($1, "image")) {
							printf "        image=%s\n", icon;
							found = 0;
						} else {
							print;
						}
					}
					' $panel > $panel.new
					mv -f $panel.new $panel
				done

				restart_lxpanel;;
			menu-notext)
				mkdir -p $dd
				echo -e '[Desktop Entry]\nType=Directory\nName=' > $sd
				restart_lxpanel;;
			menu-text)
				[ -f "$sd" ] && rm "$sd"
				restart_lxpanel;;
		esac
		exit 0
		;;


	*\ menuIcon\ *)
		# return specified image (AJAX)
		icon="/usr/share/pixmaps/$(GET menuIcon).png"
		[ ! -r $icon ] && exit 0
		header "Content-Type: image/png"; cat $icon; exit 0
		;;
esac





#
# Default xHTML content
#

header

case " $(GET) " in
	*\ group*)
		#
		# Groups management
		#
		xhtml_header "$(_ 'Manage groups')"
		check_root_tazpanel

		cat <<EOT
<section id="groups">
	<form class="wide">
		<header>
			<input type="hidden" name="groups"/>
			<!-- $(_ 'Selection:') -->
			<button name="do" value="delgroups" data-icon="@delete@">$(_ 'Delete group')</button>
		</header>

		<div class="scroll">
			<table class="wide zebra scroll">
				<thead>
					<tr class="thead">
						<td>$(_ 'Group')</td>
						<td>$(_ 'Group ID')</td>
						<td>$(_ 'Members')</td>
					</tr>
				</thead>
				<tbody>
EOT
		for group in $(getdb group | cut -d: -f1); do
			IFS=':'
			set -- $(getdb group | grep "^$group:")
			unset IFS
			cat <<EOT
					<tr>
						<td><input type="checkbox" name="group" value="$group" id="$group"/>
							<label for="$group" data-icon="@group@">$group</label></td>
						<td>$3</td>
						<td>${4//,/, }</td>
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
	<header>$(_ 'Add a new group')</header>
	<form class="wide">
		<input type="hidden" name="groups"/>
		<footer>$(_ 'Group name:') <input type="text" name="group"/>
			<button type="submit" name="do" value="addgroup" data-icon="@add@">$(_ 'Create group')</button>
		</footer>
	</form>
</section>


<section>
	<header>$(_ 'Manage group membership')</header>
	<form class="wide">
		<input type="hidden" name="groups"/>
		<div>
			$(_ 'Group name:') <select name="group">$(listdb group)</select>
			$(_ 'User login:') <select name="member">$(listdb passwd)</select>
		</div>
		<footer>
			<button name="do" value="addmember" data-icon="@add@">$(_ 'Add user')</button>
			<button name="do" value="delmember" data-icon="@delete@">$(_ 'Remove user')</button>
		</footer>
	</form>
</section>

EOT
		;;


	*\ user*)
		#
		# Users management
		#
		xhtml_header "$(_ 'Manage users')"
		check_root_tazpanel

		cat <<EOT
<section id="users">
	<form class="wide">
		<header>
			<!--$(_ 'Selection:')-->
			<button name="do" value="delusers"    data-icon="@delete@">$(_ 'Delete user')</button>
			<button name="do" value="lockusers"   data-icon="@lock@"  >$(_ 'Lock user'  )</button>
			<button name="do" value="unlockusers" data-icon="@unlock@">$(_ 'Unlock user')</button>
		</header>

		<table class="wide zebra center">
			<thead>
				<tr>
					<td>$(_ 'Login')</td>
					<td>$(_ 'User ID')</td>
					<td>$(_ 'User Name')</td>
					<td>$(_ 'Home')</td>
					<td>$(_ 'Shell')</td>
				</tr>
			</thead>
			</tbody>
EOT
		for login in $(getdb passwd | cut -d: -f1); do
			if [ -d "/home/$login" ]; then
				blocked=''; usericon='@user@'
				if getdb shadow | grep -qs "^$login:!"; then
					blocked='class="color31"'
					usericon='@lock@'
				fi
				IFS=':'
				set -- $(getdb passwd | grep "^$login:")
				unset IFS
				cat <<EOT
<tr>
	<td style="white-space: nowrap">
		<input type="checkbox" name="user" value="$login" id="$login"/>
		<label for="$login" data-icon="$usericon" $blocked>$login</label></td>
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
			$(_ 'Password:')
			<input type="password" name="password" placeholder="$(_ 'New password')"/>
			<button type="submit" name="do" value="chpasswd" data-icon="@ok@">$(_ 'Change password')</button>
		</footer>
	</form>
</section>


<section>
	<header>$(_ 'Add a new user')</header>

	<form>
		<input type="hidden" name="users"/>
		<table class="summary">
			<tr><td>$(_ 'User login:')</td>
				<td><input type="text" name="user" size="30" pattern="[a-z]*"/></td></tr>
			<tr><td>$(_ 'User name:')</td>
				<td><input type="text" name="name" size="30"/></td></tr>
			<tr><td>$(_ 'User password:')</td>
				<td><input type="password" name="passwd" size="30"/></td></tr>
		</table>

		<footer>
			<button type="submit" name="do" value="adduser" data-icon="@add@">$(_ 'Create user')</button>
		</footer>
	</form>
</section>
EOT

		# `who` output is empty in the SLiM sessions
		if [ -n "$(who)" ]; then
			cat <<EOT
<section>
	<header>$(_ 'Current user sessions')</header>
	<pre>$(who)</pre>
</section>
EOT
		fi

		# `last` output is empty (just header) in the Live mode
		if [ "$(last | wc -l)" != "1" ]; then
			cat <<EOT
<section>
	<header>$(_ 'Last user sessions')</header>
	<div class="scroll"><pre>$(last)</pre></div>
</section>
EOT
		fi
		;;


	*\ locale*)
		#
		# Choose locale
		#
		xhtml_header "$(_ 'Choose locale')"
		check_root_tazpanel

		loading_msg "$(_ 'Please wait...')"

		cur_loc=$(locale | grep LANG | cut -d= -f2)
		cat <<EOT
<section id="locale">
	<header>$(_ 'Current locale settings:')</header>
	<div>
		<pre>$(locale)</pre>
	</div>
</section>

<section>
	<header>$(_ 'Locales that are currently installed on the machine:')</header>
	<div>
		<pre>$(locale -a)</pre>
	</div>
</section>
EOT

		is_installed "glibc-locale"
		[ $? = 1 ] &&
			msg tip $(_ \
			"Can't see your language?<br/>You can \
<a href='pkgs.cgi?do=Install&amp;glibc-locale'>install glibc-locale</a> \
to see a larger list of available locales.")


		cat <<EOT
<section>
	<header>$(_ 'Available locales:')</header>
	<form class="wide">
		<table class="wide zebra">
			<thead>
				<tr><td>$(_ 'Code')</td>
					<td>$(_ 'Language')</td>
					<td>$(_ 'Territory')</td>
					<td>$(_ 'Description')</td>
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
			<button type="submit" data-icon="@ok@">$(_ 'Activate')</button>
		</footer>
	</form>
</section>
EOT
		;;


	*\ tweaks\ *)
		#
		# Small tweaks for user
		#
		user="$REMOTE_USER"; host="$(hostname)"
		xhtml_header "$(_ 'Small quick tweaks for user %s' "$user")"

		HOME="$(getdb passwd | awk -F: -vu=$user '$1==u{print $6}')"
		font="${TERM_FONT:-monospace}"; palette=$(echo $TERM_PALETTE | tr A-Z a-z)
		case $user in
			root) color=31; ind="#";;
			*)    color=32; ind="$";;
		esac

		prompt_bw="$user@$host:/usr/bin$ind"
		prompt_c="<span class=\"color$color\">$user@$host</span>:<span class=\"color33\">/usr/bin</span>$ind"
		cursor="<span class=\"color47\">_</span>"
		cat <<EOT
<script type="text/javascript">
function tweak(tweakName) {
	// Send request to the server
	var hiddenImg = document.createElement('IMG');
	hiddenImg.src = "settings.cgi?tweak=" + tweakName;
}
</script>

<section>
	<header>$(_ 'Small quick tweaks for user %s' "$user")</header>

	<div>
	<fieldset><legend>$(_ 'Terminal prompt')</legend>
		<table class="wide">
			<tr>
				<td>
					<label>
						<input type="radio" name="termPrompt" onclick="tweak('monochrome')"/>
						$(_ 'Monochrome')
					</label>
					<pre class="term $palette" style="font-family: '$font'; height: 5rem;">
$prompt_bw uname -r<br/>$(uname -r)<br/>$prompt_bw date<br/>$(date)<br/>$prompt_bw $cursor
</pre>
				</td>
				<td>
					<label>
						<input type="radio" name="termPrompt" onclick="tweak('colored')"/>
						$(_ 'Colored')
					</label>
					<pre class="term $palette" style="font-family: '$font'; height: 5rem;">
$prompt_c uname -r<br/>$(uname -r)<br/>$prompt_c date<br/>$(date)<br/>$prompt_c $cursor
</pre>
				</td>
			</tr>
		</table>

		<p>$(_ 'Manual edit: %s' "<a data-icon=\"@conf@\" href="index.cgi?file=$HOME/.profile">~/.profile</a>")<br/>
$(_ 'To take effect: log out and log in to system or execute a command in the terminal:')</p>

		<pre>. ~/.profile</pre>
	</fieldset>

	<br/>

	<fieldset>
		<legend>$(_ 'Menu button appearance')</legend>
		<table class="wide">
			<tr>
				<td style="vertical-align: top">
					<fieldset>
						<legend>$(_ 'Icon:')</legend>
						<label>
							<input type="radio" name="menuIcon" onclick="tweak('slitaz-menu-empty')"/>
							$(_ 'Do not show')
						</label><br/>
						<label>
							<input type="radio" name="menuIcon" onclick="tweak('slitaz-button-red')"/>
							<img src="?menuIcon=slitaz-button-red"/>
						</label><br/>
						<label>
							<input type="radio" name="menuIcon" onclick="tweak('slitaz-menu')"/>
							<img src="?menuIcon=slitaz-menu"/>
						</label><br/>
						<label>
							<input type="radio" name="menuIcon" onclick="tweak('slitaz-button')"/>
							<img src="?menuIcon=slitaz-button"/>
						</label>
					</fieldset>
				</td>
				<td style="vertical-align: top">
					<fieldset>
						<legend>$(_ 'Text:')</legend>
						<label>
							<input type="radio" name="menuText" onclick="tweak('menu-notext')"/>
							$(_ 'Do not show')
						</label><br/>
						<label>
							<input type="radio" name="menuText" onclick="tweak('menu-text')"/>
							$(_ 'Show text')
						</label>
					</fieldset>
				</td>
			</tr>
		</table>
		<p>$(_ 'Manual edit: %s' \
			"<a data-icon=\"@conf@\" href=\"index.cgi?file=$HOME/.local/share/desktop-directories/SliTazMenu.directory\">~/.local/share/desktop-directories/SliTazMenu.directory</a>
			$(
				find $HOME/.config/lxpanel -type f -name panel | awk -vh="$HOME" \
				'{ printf "<a data-icon=\"@conf@\" href=\"index.cgi?file=%s\">%s</a> ", $1, gensub(h, "~", "")}'
			)")</p>
	</fieldset>
	</div>
</section>
EOT
		;;


	*)
		#
		# Default system settings page
		#
		xhtml_header "$(_ 'Manage system time, users or language settings')"
		check_root_tazpanel

		cat <<EOT
<form><!--
	--><button name="users"  data-icon="@user@" >$(_ 'Manage users' )</button><!--
	--><button name="groups" data-icon="@group@">$(_ 'Manage groups')</button>
</form>

<section>
	<header>$(_ 'System time')</header>
	<div>
	<form class="wide" id="sysTimeForm">
		<fieldset><legend>$(_ 'Time zone:')</legend>
			<select name="tz">
				$(cd /usr/share/zoneinfo; find * -type f ! -name '*.tab' | sort | \
				awk -vtz="$(cat /etc/TZ)" \
				'{printf("<option%s>%s</option>", ($1 == tz)?" selected":"", $1)}')
			</select>
			<button name="do" value="settz" data-icon="@ok@">$(_ 'Change')</button>
		</fieldset>

		<fieldset><legend>$(_ 'System time:')</legend>
			$(sh -l -c date | sed 's|[0-9][0-9]:[0-9:]*|<span id="time">&</span>|')
			<button name="do" value="rdate" data-icon="@sync@">$(_ 'Sync online')</button>
		</fieldset>

		<fieldset id="hwclock1"><legend>$(_ 'Hardware clock:')</legend>
			<span id="hwclocks">$(hwclock -ur | sed 's|0.000000 seconds||')</span>
			<button name="do" value="hwclock" id="hwclock" data-icon="@clock@">$(_ 'Set hardware clock')</button>
		</fieldset>

		<fieldset><legend>$(_ 'Set date')</legend>
EOT
		if [ -z "$(which yad)" ]; then
			cat <<EOT
			<input type="number" name="day" value="$(date +%d)" min="1" max="31" size="4" required/>
			<select name="month" value="$(date +%m)">
				$(for i in $(seq 12); do
					sel=''; [ "$i" == "$(date +%-m)" ] && sel=' selected'
					printf "<option value=\"%s\"$sel>%s</option>" $(date -d $i.01-01:01 '+%m %B')
				done)
			</select>
			<input type="number" name="year" value="$(date +%Y)" min="2015" max="2030" size="6" required/>
EOT
		else
			cat <<EOT
			<button onclick="datePicker(); return false">
				<span id="dateTime" data-icon="@calendar@">$(date +%x)<span style="display:none">$(date +%F)</span></span>
			</button>
EOT
		fi
		cat <<EOT
		-	<input type="number" name="hour" value="$(date +%H)" min="0"    max="23"   size="4" required/><!--
		-->:<input type="number" name="min"  value="$(date +%M)" min="0"    max="59"   size="4" required/><!--
		-->:<input type="number" name="sec"  value="00"          min="0"    max="59"   size="4" required/>
EOT
		if [ -z "$(which yad)" ]; then
			cat <<EOT
			<button name="do" value="date" data-icon="@ok@">$(_ 'Set date')</button>
EOT
		else
			cat <<EOT

			<button data-icon="@ok@" onclick="submitSysTimeForm()">$(_ 'Set date')</button>
EOT
		fi
		cat <<EOT
		</fieldset>
	</form>
	</div>

<script type="text/javascript">
// Live time on page
Date.prototype.timeNow = function() {
	return ((this.getHours() < 10)?"0":"") + this.getHours() + ":" + ((this.getMinutes() < 10)?"0":"") + this.getMinutes() + ":" + ((this.getSeconds() < 10)?"0":"") + this.getSeconds();
}
setInterval(function(){
	document.getElementById('time').textContent = new Date().timeNow();
	//ajax('settings.cgi?do=gethwclock', '1', 'hwclocks');
}, 1000);


// Run date picker and return value to the 'dateTime' element
function datePicker() {
	ajax('settings.cgi?do=calendar', '1', 'dateTime');
}

// Actions to do before form submit and submit
function submitSysTimeForm() {
	sysTimeForm = document.getElementById('sysTimeForm');

	var dateFull = document.createElement('INPUT');
	dateFull.name = 'dateFull';
	dateFull.value = document.getElementById('dateTime').childNodes[1].textContent;
	dateFull.type = 'hidden';
	sysTimeForm.appendChild(dateFull);

	var submitDo = document.createElement('INPUT');
	submitDo.name = 'do'; submitDo.value = 'date';
	submitDo.type = 'hidden';
	sysTimeForm.appendChild(submitDo);

	sysTimeForm.submit();
}
</script>
</section>
EOT


		#
		# Locale settings
		#
		cat <<EOT
<section>
	<header id="locale">$(_ 'System language')</header>
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
			msg warn "$(_ \
			'You must logout and login again to your current session to use %s locale.' $new_locale)"
		else
			cat <<EOT
		$(_ 'Current system locale:')
		<strong>$(locale | grep LANG | cut -d= -f2)</strong>
		<button name="locale" data-icon="@locale@">$(_ 'Change')</button>
EOT
		fi
		cat <<EOT
	</div>
	</form>
</section>


<section>
	<header id="keymap">$(_ 'Keyboard layout')</header>
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
		_ 'Current console keymap: %s' $keymap
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
		$(_ 'Suggested keymap for Xorg:') $keymap
		<button form="settings" name="apply_xorg_kbd" value="$keymap" data-icon="@ok@">$(_ 'Activate')</button>
		<button form="index" name="file" value="$keyboard_config" data-icon="@edit@">$(_ 'Edit')</button>
		<input form="index" type="hidden" name="action" value="edit" />
		<br/>
EOT
		fi
		cat <<EOT
		<form>
			$(_ 'Available keymaps:')
			<select name="gen_keymap">
				$(list_keymaps)
			</select>
			<button type="submit" data-icon="@ok@">$(_ 'Activate')</button>
		</form>
	</div>
</section>


<section>
	<header>$(_ 'Panel configuration')</header>
	<div>
	<form class="wide">
		<fieldset><legend>$(_ 'Style:')</legend>
			<select name="style">$(list_styles)</select>
			<button data-icon="@ok@">$(_ 'Activate')</button>
		</fieldset>
	</form>

	<fieldset><legend>$(_ 'Configuration files:')</legend>
		<button form="index" name="file" value="$CONFIG" data-icon="@edit@">$(_ 'Panel')</button>
		<button form="index" name="file" value="$HTTPD_CONF" data-icon="@edit@">$(_ 'Server')</button>
	</fieldset>

	<p>$(_ 'TazPanel provides a debugging mode and page:')
		<a href="index.cgi?debug">debug</a>
	</p>
	</div>
</section>
EOT
	;;
esac

xhtml_footer
exit 0
