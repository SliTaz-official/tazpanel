#!/bin/sh
#
# Main CGI interface for TazPanel. In on word: KISS. Use the main CSS form
# command so we are faster and do not load unneeded functions. If necessary
# you can use the lib/ dir to handle external resources.
#
# Copyright (C) 2011-2015 SliTaz GNU/Linux - BSD License
#


# Common functions from libtazpanel

. lib/libtazpanel
get_config

TITLE="TazPanel"



# Check whether a configuration file has been modified after installation

file_is_modified() {
	grep -l "  $1$" $INSTALLED/*/md5sum | while read file; do

		# Found, but can we do diff?
		[ "$(grep -h "  $1$" $file)" != "$(md5sum $1)" ] || break
		orig=$(dirname $file)/volatile.cpio.gz
		zcat $orig 2>/dev/null | cpio -t 2>/dev/null | grep -q "^${1#/}$" || break

		case "$2" in
			diff)
				tmp=$(mktemp -d)
				( cd $tmp; zcat $orig | cpio -id ${1#/} )
				diff -abu $tmp$1 $1 | sed "s|$tmp||"
				rm -rf $tmp;;
			button)
				echo -n '<button name="action" value="diff" data-icon="diff">'$(_ 'Differences')'</button>';;
		esac
		break
	done
}



# OK status in table

ok_status_t() {
	echo '<td><span class="diff-add" data-img="ok"></span></td></tr>'
}



# Terminal prompt

term_prompt() {
	if [ "$user" == 'root' ]; then
		local color1='color31' sign='#'
	else
		local color1='color32' sign='$'
	fi
	echo -n "<span class='$color1'>$user@$(hostname)</span>:<span class='color33'>"
	pwd | sed "s|^$HOME|~|" | tr -d '\n'; echo -n "</span>$sign "
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
		# Execute command and display its result in a terminal-like window

		header; TITLE=$(_ 'TazPanel - exec'); xhtml_header

		exec="$(GET exec)"
		font="${TERM_FONT:-monospace}"
		palette=$(echo $TERM_PALETTE | tr A-Z a-z)

		cat <<EOT
<section>
	<header>
		$exec
		$(back_button "$(GET back)" "$(GET back_caption)" "$(GET back_icon)")
	</header>
	<div class="term_">
		<pre class="term $palette" style="font-family: '$font'">$($exec 2>&1 | htmlize | filter_taztools_msgs)</pre>
	</div>
</section>
EOT
		;;


	*\ file\ *)
		#
		# Handle files
		#
		header
		file="$(GET file)"
		action="$(POST action)"; [ -z "$action" ] && action="$(GET action)" # receive 'action' both on POST or GET
		title="$(POST title)";   [ -z "$title"  ] && title="$(GET title)"   # (optional)

		case $file in
			*.html)
				cat $file; exit 0 ;;
			*)
				TITLE=$(_ 'TazPanel - File'); xhtml_header ;;
		esac

		case "$action" in
			edit)
				cat <<EOT
<section>
	<header>
		<span data-icon="edit">${title:-$file}</span>
		<form id="editform" method="post" action="?file=$file">
			<button data-icon="save">$(_ 'Save')</button>
			<button name="action" value="diff" data-icon="diff">$(_ 'Differences')</button>
		</form>
	</header>
	<textarea form="editform" name="content" class="wide" rows="30" autofocus>$(cat $file | htmlize)</textarea>
</section>
EOT
#The space before textarea gets muddled when the form is submitted.
#It prevents anything else from getting messed up
			;;

		setvar)
			data="$(. $(GET file) ;eval echo \$$(GET var))"
			cat <<EOT
<section>
	<header>$(GET var)</header>
	<form method="post" action="?file=$file" class="nogap">
		<input type="hidden" name="var" value="$(GET var)">
		<input type="text" name="content" value="${data:-$(GET default)}">
		<button type="submit" data-icon="save">$(_ 'Save')</button>
	</form>
</section>
EOT
			;;

		diff)
			cat <<EOT
<section>
	<pre id="diff">$(file_is_modified $file diff | syntax_highlighter diff)</pre>
</section>
EOT
			;;

		*)
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
<section class="bigNoScrollable">
	<header>
		<span data-icon="text">${title:-$file}</span>
EOT
			if [ -w "$file" ]; then
				cat <<EOT
		<span class="float-right">
			<button onclick='editFile()' id="edit_button" data-icon="edit">$(_ 'Edit')</button>
			<button onclick='saveFile("$file", "$title")' id="save_button" 
				data-icon="save" style="display:none">$(_ 'Save')</button>
		</span>
		<!--form>
			<input type="hidden" name="file" value="$file"/>
			<button name="action" value="edit" data-icon="edit">$(_ 'Edit')</button><!--
			-->$(file_is_modified $file button)
		</form-->
EOT
			elif [ -r "$file" ]; then
				cat <<EOT
		<form>
			<input type="hidden" name="file" value="$file"/>
			$(file_is_modified $file button)
		</form>
EOT
			fi
			cat <<EOT
	</header>

	<div>
		<pre id="fileContent" class="bigScrollable">
EOT
			end_code=''
			# Handle file type by extension as a Web Server does it.
			case "$file" in
				*.sh|*.cgi|*/receipt|*.conf)
					echo '<code class="language-bash">'; end_code='</code>'
					cat | htmlize ;;
				*.ini)
					echo '<code class="language-ini">'; end_code='</code>'
					cat | htmlize ;;
				*.conf|*.lst)
					syntax_highlighter conf ;;
				*Xorg.0.log)
					syntax_highlighter xlog ;;
				*dmesg.log)
					syntax_highlighter kernel ;;
				*)
					cat | htmlize ;;
			esac < $file
			cat <<EOT
$end_code</pre>
	</div>
</section>
EOT
		esac
		;;



	*\ terminal\ *|*\ cmd\ *)
		# Cmdline terminal

		header; TITLE=$(_ 'TazPanel - Terminal'); xhtml_header

		user="$REMOTE_USER"
		HOME="$(awk -F: -vu=$user '$1==u{print $6}' /etc/passwd)"
		historyfile="$HOME/.ash_history"

		cmd=$(GET cmd)
		path="$(GET path)"; path="${path:-/tmp}"; cd "$path"

		font="${TERM_FONT:-monospace}"
		palette=$(echo $TERM_PALETTE | tr A-Z a-z)

		[ -n "$cmd" -a "$cmd" != "$(tail -n1 $historyfile)" ] && echo "$cmd" >> $historyfile


		# Terminal history

		if [ "$cmd" == 'history' ]; then
			cat <<EOT
<section>
	<header>
		$(_ 'History')
		<form><button name="terminal" data-icon="terminal">$(_ 'Back')</button></form>
	</header>
	<form>
		<input type="hidden" name="path" value="$path"/>
		<pre class="term $palette" style="font-family: '$font'">
EOT
			htmlize < $historyfile | awk -vrun="$(_ 'run')" -vpath="$path" '
			BEGIN { num=1 }
			{
			printf("%3d ", num);
			cmd = $0
			gsub("%",  "%25", cmd); gsub("+",  "%2B", cmd); gsub(" ",    "+",   cmd);
			gsub("\"", "%22", cmd); gsub("!",  "%21", cmd); gsub("'\''", "%27", cmd);
			printf("<a data-icon=\"run\" href=\"?cmd=%s&path=%s\">%s</a> ", cmd, path, run);
			printf("<input type=\"checkbox\" name=\"rm\" value=\"%d\" id=\"hist%d\">", num, num);
			printf("<label for=\"hist%d\">%s</label>\n", num, $0);
			num++
			}'
			cat <<EOT
		</pre>
		<footer>
			<button name="rmhistory" data-icon="remove">$(_ 'Clear')</button>
		</footer>
	</form>
</section>
EOT
			xhtml_footer
			exit 0
		fi


		# Terminal window

		cat <<EOT
<span id="num_hist"></span>
<section>
	<pre class="term $palette" style="font-family: '$font'" onclick="document.getElementById('typeField').focus()">
EOT
		if [ -n "$cmd" ]; then
			term_prompt
			echo "$cmd" | htmlize
		fi

		case "$cmd" in
		usage|help)
			_ 'Small non-interactive terminal emulator.'; echo
			_ 'Run any command at your own risk, avoid interactive commands (%s)' 'nano, mc, ...'; echo
			;;
		wget*)
			dl=/var/cache/downloads
			[ ! -d "$dl" ] && mkdir -p $dl
			_ 'Downloading to: %s' $dl; echo
			cd $dl; $cmd 2>&1 ;;
		cd|cd\ *)
			path="${cmd#cd}"; path="${path:-$HOME}";
			path="$(realpath $path)"; cd "$path" ;;
		ls|ls\ *)
			$cmd -w80 --color=always 2>&1 | filter_taztools_msgs ;;
		cat)
			# Cmd must be used with an arg.
			_ '%s needs an argument' "$cmd" ;;
		mc|nano|su)
			# List of restricted (interactive) commands
			_ "Please, don't run interactive command \"%s\"" "$cmd"; echo; echo ;;
		*)
			unset HTTP_REFERER  # for fooling /lib/libtaz.sh formatting utils (<hr> in the terminal is so-so)
			export DISPLAY=:0.0 # for run X applications
			/bin/sh -c "$cmd" 2>&1 | htmlize | filter_taztools_msgs
			;;
	esac

	cat <<EOT
<form id="term">
<div class="cmdline" id="cmdline"><span id="prompt">$(term_prompt)</span><span id="typeField"> </span></div>
<input type="hidden" name="path" value="$(pwd)"/>
<input type="hidden" name="cmd" id="cmd"/>
</form>
</pre>
</section>

<form>
	<button name="termsettings" data-icon="settings">$(_ 'Settings')</button>
	<button name="cmd" value="history" data-icon="history">$(_ 'History')</button>
</form>

<script type="text/javascript">
with (document.getElementById('typeField')) {
	contentEditable=true;
	focus();
}
document.onkeydown=keydownHandler;
EOT

	# Export history as array.
	# Escape "all \"quotes\" in quotes", and all '\'
	#  (because \u, \x, \c has special meaning and can produce syntax error and stop js)
	sed 's|\\|\\\\|g; s|"|\\"|g' $historyfile | awk '
	BEGIN{ i=1; printf("ash_history=[") }
	{ printf("\"%s\",", $0); i++ }
	END{
		printf("\"\"];")
		i--; printf("cur_hist=\"%d\";max_hist=\"%d\";", i, i)
	}'
	cat <<EOT
</script>
EOT
	;;


	*\ rmhistory\ *)
		# Manage shell commandline history
		user="$REMOTE_USER"
		[ -z "$HOME" ] && HOME="$(awk -F: -vu=$user '$1==u{print $6}' /etc/passwd)"
		historyfile="$HOME/.ash_history"

		# Return sed command for removing history lines ('8d12d' to remove 8 and 12 lines)
		rms=$(echo $QUERY_STRING | awk 'BEGIN{RS="&";FS="="}{if($1=="rm")printf "%dd", $2}')

		if [ -n "$rms" ]; then
			# Actually remove lines
			sed -i $rms $historyfile
			# Redirects back to the history table
			header "HTTP/1.1 301 Moved Permanently" "Location: ?terminal&cmd=history&path=$(GET path)"
			exit 0
		fi
		;;


	*\ termsettings\ *)
		# Terminal settings
		TITLE=$(_ 'TazPanel - Terminal'); header; xhtml_header;
		user="$REMOTE_USER"
		font="$(GET font)"; font="${font:-$TERM_FONT}"
		palette="$(GET palette)"; palette="${palette:-$TERM_PALETTE}"
		pal=$(echo $palette | tr A-Z a-z)

		# Add or change settings in TazPanel config
		if [ -z "$TERM_FONT" ]; then
			echo -e "\n# Terminal font family\nTERM_FONT=\"$font\"" >> $CONFIG
		else
			sed -i "s|TERM_FONT=.*|TERM_FONT=\"$font\"|" $CONFIG
		fi
		if [ -z "$TERM_PALETTE" ]; then
			echo -e "\n# Terminal color palette\nTERM_PALETTE=\"$palette\"" >> $CONFIG
		else
			sed -i "s|TERM_PALETTE=.*|TERM_PALETTE=\"$palette\"|" $CONFIG
		fi

		cat <<EOT
<section style="position: absolute; top: 0; bottom: 0; left: 0; right: 0; margin: 0.5rem;">
	<header>
		$(_ 'Terminal settings')
		<form>
			<button name="terminal" data-icon="terminal">$(_ 'Terminal')</button>
		</form>
	</header>
	<pre class="term $pal" style="height: auto; font-family: '$font'">
<span class='color31'>$user@$(hostname)</span>:<span class='color33'>~</span># palette

$(
	for i in $(seq 30 37); do
		for b in 0 1; do
			for j in $(seq 40 47); do
				echo -n "<span class=\"color$b color$i color$j\">$i:$j</span>"
			done
		done
		echo
	done
)
	</pre>
	<footer>
		<form class="wide">
			$(_ 'Font:')
			<select name="font">
				<option value="">$(_ 'Default')</option>
				$(fc-list :spacing=mono:lang=en family | sed '/\.pcf/d;/,/d;s|\\-|-|g' | sort -u | \
				awk -vfont="$font" '{
				printf("<option value=\"%s\"%s>%s</option>\n", $0, ($0 == font)?" selected":"", $0)
				}')
			</select>
			$(_ 'Palette:')
			<select name="palette">
				$(echo -e 'Tango\nLinux\nXterm\nRxvt\nEcho' | awk -vpal="$palette" '{
				printf("<option value=\"%s\"%s>%s</option>\n", $0, ($0 == pal)?" selected":"", $0)
				}')
			</select>
			<button name="termsettings" data-icon="ok">$(_ 'Apply')</button>
		</form>
	</footer>
</section>
EOT

		;;


	*\ top\ *)
		header; TITLE=$(_ 'TazPanel - Process activity'); xhtml_header

		r=$(GET refresh)
		cat <<EOT
<form>
	<p>$(_ 'Refresh:')
	<input type="hidden" name="top"/>
	<input type="radio" name="refresh" value="1"  id="r1" $([ "$r" == 1  ] && echo checked) onchange="this.form.submit()"/>
	<label for="r1">$(_ '1s'  )</label>
	<input type="radio" name="refresh" value="5"  id="r2" $([ "$r" == 5  ] && echo checked) onchange="this.form.submit()"/>
	<label for="r2">$(_ '5s'  )</label>
	<input type="radio" name="refresh" value="10" id="r3" $([ "$r" == 10 ] && echo checked) onchange="this.form.submit()"/>
	<label for="r3">$(_ '10s' )</label>
	<input type="radio" name="refresh" value=""   id="r4" $([ -z "$r"    ] && echo checked) onchange="this.form.submit()"/>
	<label for="r4">$(_ 'none')</label>
	</p>
</form>
EOT
		[ -n "$r" ] && echo "<meta http-equiv=\"refresh\" content=\"$r\">"

		echo '<section><div><pre class="term log">'
		top -n1 -b | htmlize | sed \
			-e 's|^[A-Z].*:|<span class="color1 color31">\0</span>|g' \
			-e 's|^\ *PID|<span class="color1 color32">\0</span>|g'
		echo '</pre></div></section>' ;;


	*\ debug\ *)
		header; TITLE=$(_ 'TazPanel - Debug'); xhtml_header

		cat <<EOT
<h2>$(_ 'HTTP Environment')</h2>

<section>
	<div>
		<pre>$(httpinfo | syntax_highlighter conf)</pre>
	</div>
</section>
EOT
		;;


	*\ report\ *)
		header; TITLE=$(_ 'TazPanel - System report'); xhtml_header

		[ -d /var/cache/slitaz ] || mkdir -p /var/cache/slitaz
		output=/var/cache/slitaz/sys-report.html

		cat <<EOT

<section>
	<header>$(_ 'Reporting to: %s' "$output")</header>
	<table class="wide zebra">
		<tbody>
			<tr><td>$(_ 'Creating report header...')</td>
EOT
		cat > $output <<EOT
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<meta charset="utf-8"/>
	<title>$(_ 'SliTaz system report')</title>
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
		cat <<EOT
	$(ok_status_t)
	<tr><td>$(_ 'Creating system summary...')</td>
EOT
		cat >> $output <<EOT
<h1>$(_ 'SliTaz system report')</h1>
$(_ 'Date:') $(date)
<pre>
uptime   : $(uptime)
cmdline  : $(cat /proc/cmdline)
version  : $(cat /etc/slitaz-release)
packages : $(ls /var/lib/tazpkg/installed | wc -l) installed
kernel   : $(uname -r)
</pre>
EOT
		cat <<EOT
	$(ok_status_t)
	<tr><td>$(_ 'Getting hardware info...')</td>
EOT
		cat >> $output <<EOT
<h2>free</h2>
<pre>$(free)</pre>

<h2>lspci -k</h2>
<pre>$(lspci -k)</pre>

<h2>lsusb</h2>
<pre>$(lsusb)</pre>

<h2>lsmod</h2>
<pre>$(lsmod)</pre>

EOT
		cat <<EOT
	$(ok_status_t)
	<tr><td>$(_ 'Getting networking info...')</td>
EOT
		cat >> $output <<EOT
<h2>ifconfig -a</h2>
<pre>$(ifconfig -a)</pre>

<h2>route -n</h2>
<pre>$(route -n)</pre>

<h2>/etc/resolv.conf</h2>
<pre>$(cat /etc/resolv.conf)</pre>
EOT
		cat <<EOT
	$(ok_status_t)
	<tr><td>$(_ 'Getting filesystems info...')</td>
EOT
		cat >> $output <<EOT
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
		cat <<EOT
	$(ok_status_t)
	<tr><td>$(_ 'Getting boot logs...')</td>
EOT
		cat >> $output <<EOT
<h2>$(_ 'Kernel messages')</h2>
<pre>$(cat /var/log/dmesg.log)</pre>

<h2>$(_ 'Boot scripts')</h2>
<pre>$(cat /var/log/boot.log | filter_taztools_msgs)</pre>
EOT
		cat <<EOT
	$(ok_status_t)
	<tr><td>$(_ 'Creating report footer...')</td>
EOT
		cat cat >> $output <<EOT
</body>
</html>
EOT
		cat <<EOT
	$(ok_status_t)
		</tbody>
	</table>
	<footer>
		<form><button name="file" value="$output" data-icon="view">$(_ 'View')</button></form>
	</footer>
</section>


	$(msg tip "$(_ 'This report can be attached with a bug report on:')
	<a href="http://bugs.slitaz.org/" target="_blank">bugs.slitaz.org</a></p>")
EOT
		;;


	*)
		#
		# Default xHTML content
		#
		header; xhtml_header
		[ -n "$(GET gen_locale)" ] && new_locale=$(GET gen_locale)
		[ -n "$(GET rdate)" ] && echo ""
		hostname=$(hostname)

		cat <<EOT
<h2>$(_ 'Host: %s' $hostname)</h2>
<p>$(_ 'SliTaz administration and configuration Panel')<p>

<form class="nogap"><!--
	--><button name="terminal" data-icon="terminal">$(_ 'Terminal')</button><!--
	--><button name="top"      data-icon="proc"    >$(_ 'Process activity')</button><!--
	--><button name="report"   data-icon="report"  data-root>$(_ 'Create a report')</button><!--
--></form>

<section>
	<header>$(_ 'Summary')</header>
	<table>
		<tr><td>$(_ 'Uptime:')</td>
			<td id="uptime">$(uptime | sed 's|\([0-9.:][0-9.:]*\)|<b>\1</b>|g')</td>
		</tr>
		<tr><td>$(_ 'Memory in Mb:')</td>
			<td>$(free -m | grep Mem: | \
				awk -vline="$(gettext 'Total: %d, Used: %d, Free: %d')" \
				'{ printf(line, $2, $3, $4) }' | \
				sed 's|\([0-9][0-9]*\)|<b>\1</b>|g')</td>
		</tr>
		<tr><td>$(_ 'Linux kernel:')</td>
			<td>$(uname -r)</td>
		</tr>
	</table>
</section>


<section>
	<header>
		$(_ 'Network status')
		<form action="network.cgi">
			<button data-icon="wifi">$(_ 'Network')</button>
		</form>
	</header>
	$(list_network_interfaces)
</section>


<section>
	<header>
		$(_ 'Filesystem usage statistics')
		<form action="hardware.cgi">
			<button data-icon="hdd">$(_ 'Disks')</button>
		</form>
	</header>
	<table class="wide zebra center">
EOT
		# Disk stats (management is done as hardware.cgi)
		df_thead
		echo '<tbody>'
		df -h | grep ^/dev | while read fs size used av pct mp; do
				cat <<EOT
			<tr>
				<td><span data-icon="hdd">${fs#/dev/}</span></td>
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
		cat <<EOT
		</tbody>
	</table>
</section>

<section>
	<header>
		$(_ 'Panel Activity')
		<form>
			<button name="file" value="$LOG_FILE" data-icon="view">$(_ 'View')</button>
		</form>
	</header>
	<div>
		<pre id="panel-activity">
$(cat $LOG_FILE | tail -n 8 | sort -r | syntax_highlighter activity)</pre>
	</div>
</section>
EOT
		;;
esac

xhtml_footer
exit 0
