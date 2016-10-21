#!/bin/sh
#
# Manage /etc/hosts CGI interface - to use hosts as Ad blocker
#
# Copyright (C) 2015 SliTaz GNU/Linux - BSD License
#


# Common functions from libtazpanel

. lib/libtazpanel
get_config
header

TITLE=$(_ 'Network')
xhtml_header "$(_ 'Use hosts file as Ad blocker')"

found=$(mktemp)

# Find the hosts list
hosts=$(echo "$QUERY_STRING&" | awk '
	BEGIN { RS="&"; FS="=" }
	$1=="host" { printf "%s ", $2 }
')
hosts=$(httpd -d "${hosts% }")
# now hosts='host1 host2 ... hostn'

# Folder to save downloaded and installed hosts lists
HOSTSDIR='/var/lib/tazpanel/hosts'
mkdir -p "$HOSTSDIR"




# List the lists data: name, about URL, download URL, update frequency, code letter
listlist() {
	# Another free to use list, but not free to modify with its EULA (and very big: 12MB!)
	# hpHosts List	http://hosts-file.net/
	echo "
MVPs.org List	http://winhelp2002.mvps.org/hosts.htm	http://winhelp2002.mvps.org/hosts.zip	monthly	M
Dan Pollock List	http://someonewhocares.org/hosts/	http://someonewhocares.org/hosts/zero/hosts	regularly	P
Malware Domain List	http://www.malwaredomainlist.com/	http://www.malwaredomainlist.com/hostslist/hosts.txt	regularly	D
Peter Lowe List	http://pgl.yoyo.org/adservers/	http://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&mimetype=plaintext	regularly	L
"
}

# Get the list specifications: name and download URL
getlistspec() {
	# Input: code letter
	local line="$(listlist | grep "$1\$")"
	name="$(echo "$line" | cut -d$'\t' -f1)"
	url="$( echo "$line" | cut -d$'\t' -f3)"
}

# Install the list
instlist() {
	# Input: list=code letter, url=download URL
	file="$HOSTSDIR/$list"
	[ -f "$file" ] && rm "$file"
	busybox wget -O "$file" "$url"
	case $url in
		*zip)
			mv "$file" "$file.zip"
			busybox unzip "$file.zip" HOSTS >/dev/null
			mv HOSTS "$file"
			rm "$file.zip"
			;;
	esac
	# Add entries to hosts file
	awk -vl="$list" '$1=="0.0.0.0"||$1=="127.0.0.1"{printf "0.0.0.0 %s #%s\n", $2, l}' "$file" | fgrep -v localhost >> /etc/hosts
	# Clean the list
	echo -n > "$file"
	touch "$file.checked"

	# Remove the duplicate entries
	hostsnew=$(mktemp)
	grep "^0.0.0.0" /etc/hosts | sort -k2,2 -u -o "$hostsnew"
	sed -i '/^0.0.0.0/d' /etc/hosts
	cat "$hostsnew" >> /etc/hosts
	rm "$hostsnew"

	# Prevent user-disabled entries to re-appear
	grep "^#0.0.0.0" /etc/hosts | while read null host; do
		sed -i "/^0.0.0.0 $host #/d" /etc/hosts
	done
}

# Remove the list
remlist() {
	# Input: list=code letter
	sed -i "/#$list$/d" /etc/hosts
	file="$HOSTSDIR/$list"
	rm "$file" "$file.checked" "$file.avail"
}



case " $(GET) " in

	*\ add\ *)
		# Add given host

		host="$(GET add)"

		echo "0.0.0.0 $host #U" >> /etc/hosts
		echo -n '<p><span data-img="@info@"></span>'
		_ 'Host "%s" added to /etc/hosts.' "$host"
		echo '</p>'
		;;

	*\ disable\ *)
		# Disable given hosts

		for host in $hosts; do
			sed -i "s|^0.0.0.0[ \t][ \t]*$host\$|#\0|" /etc/hosts
			sed -i "s|^0.0.0.0[ \t][ \t]*$host .*|#\0|" /etc/hosts
		done
		r=$(echo "$hosts" | tr ' ' '\n' | wc -l)
		echo -n '<p><span data-img="@info@"></span>'
		_p  '%d record disabled' \
			'%d records disabled' "$r"   "$r"
		echo '</p>'
		;;

	*\ instlist\ *)
		# Install list

		list="$(GET instlist)"
		getlistspec "$list"
		echo "<p>$(_ 'Installing the "%s"...' "$name") "
		instlist
		echo "$(_ 'Done')</p>"
		# Don't show diff because it's huge
		rm "$HOSTSDIR/diff"
		;;

	*\ uplist\ *)
		# Update list

		list="$(GET uplist)"
		getlistspec "$list"
		echo "<p>$(_ 'Updating the "%s"...' "$name") "

		old_sublist=$(mktemp)
		# Note, old sublist already sorted. Only hostnames here
		awk -vlist="#$list" '$3 == list {print $2}' /etc/hosts > "$old_sublist"

		remlist; instlist

		new_sublist=$(mktemp)
		awk -vlist="#$list" '$3 == list {print $2}' /etc/hosts > "$new_sublist"

		# The diff: just '+' and '-', no header, no context
		diff -dU0 "$old_sublist" "$new_sublist" | sed '1,2d;/^@/d' > "$HOSTSDIR/diff"

		echo "$(_ 'Done')</p>"

		# Show diff
		if [ -s "$HOSTSDIR/diff" ]; then
			echo '<section><pre class="scroll">'
			cat "$HOSTSDIR/diff" | syntax_highlighter diff
			echo '</pre></section>'
		fi

		# Clean
		rm "$old_sublist" "$new_sublist" "$HOSTSDIR/diff"
		;;

	*\ remlist\ *)
		# Remove list

		list="$(GET remlist)"
		getlistspec "$list"
		echo "<p>$(_ 'Removing the "%s"...' "$name") "
		remlist
		echo "$(_ 'Done')</p>"
		;;

esac

# When search term given
term=$(GET term)
if [ -z "$term" ]; then
	getdb hosts | fgrep 0.0.0.0 > "$found"
	r=$(wc -l < "$found")
	echo -n '<p><span data-img="@info@"></span>'
	_p  '%d record used for Ad blocking' \
		'%d records used for Ad blocking' "$r"   "$r"
else
	getdb hosts | fgrep 0.0.0.0 | fgrep "$term" > "$found"
	r=$(wc -l < "$found")
	echo -n '<p><span data-img="@info@"></span>'
	_p  '%d record found for "%s"' \
		'%d records found for "%s"' "$r"   "$r" "$term"
fi

[ "$r" -gt 100 ] && _ ' (The list is limited to the first 100 entries.)'
echo '</p>'

cat <<EOT
<section>
	<header>
		<span data-icon="@list@">$(_ 'Hosts')</span>
		<form>
			<input type="search" name="term" value="$(GET term)" results="5" autosave="hosts" autocomplete="on"/>
		</form>
	</header>
	<form class="wide">
		<pre class="scroll">
EOT
head -n100 "$found" | awk '{
	printf "<label><input type=\"checkbox\" name=\"host\" value=\"%s\"/> %s</label>\n", $2, $2;
}'
rm "$found"
cat <<EOT
</pre>
		<footer>
			<button type="submit" name="disable" data-icon="@delete@" data-root>$(_ 'Disable selected')</button>
		</footer>
	</form>
</section>

<section>
	<header><span data-icon="@add@">$(_ 'Add')</span></header>
	<form class="wide">
		<div>
			$(_ 'Host:')
			<input type="text" name="add"/>
		</div>
		<footer>
			<button type="submit" data-icon="@add@" data-root>$(_ 'Add')</button>
		</footer>
	</form>
</section>

<section>
	<header><span data-icon="@admin@">$(_ 'Manage lists')</span></header>
	<div>$(_ 'You can use one or more prepared hosts files to block advertisements, malware and other irritants.')</div>
	<form class="wide">
	<table class="wide zebra">
		<thead>
			<tr>
				<td>$(_ 'Name')</td>
				<td>$(_ 'Details')</td>
				<td>$(_ 'Updates')</td>
				<td>$(_ 'Actions')</td>
			</tr>
		</thead>
		<tbody>
EOT

IFS=$'\t'
listlist | while read name info url updated letter; do
	[ -z "$name" ] && continue

	cat <<EOT
<tr>
	<td>$name</td>
	<td><a data-icon="@info@" target="_blank" rel="noopener" href="$info">$(_ 'info')</a></td>
	<td>
		$([ "$updated" == 'monthly'   ] && _ 'Updated monthly')
		$([ "$updated" == 'regularly' ] && _ 'Updated regularly')
	</td>
	<td>
EOT

	if [ -e "$HOSTSDIR/$letter" -o -n "$(grep -m1 "#$letter\$" /etc/hosts)" ]; then
		# List installed

		# If /var/run/tazpkg/hosts/ was mistakenly cleaned
		[ ! -f "$HOSTSDIR/$letter" ] && touch "$HOSTSDIR/$letter"

		# Check for upgrades (once a day)
		if [ -f "$HOSTSDIR/$letter.checked" ]; then
			# Update checked previously
			if [ "$(($(date -u +%s) - 86400))" -gt "$(date -ur "$HOSTSDIR/$letter.checked" +%s)" ]; then
				# Update checked more than one day (86400 seconds) ago
				check='yes'
			else
				# Update checked within one day
				check='no'
			fi
		else
			# Update not checked yet
			check='yes'
		fi

		if [ "$check" == 'yes' ]; then
			# Check for update (not really download)
			busybox wget -s --header "If-Modified-Since: $(date -Rur "$HOSTSDIR/$letter")" "$url"
			if [ "$?" -eq 0 ]; then
				# Update available
				touch "$HOSTSDIR/$letter.avail"
			else
				# Update not available
				rm "$HOSTSDIR/$letter.avail" 2>/dev/null
			fi
			touch "$HOSTSDIR/$letter.checked"
		fi

		if [ -f "$HOSTSDIR/$letter.avail" ]; then
			cat <<EOT
<button name="uplist" value="$letter" data-icon="@upgrade@">$(_ 'Upgrade')</button>
EOT
		fi

		cat <<EOT
<button name="remlist" value="$letter" data-icon="@remove@">$(_ 'Remove')</button>
EOT

	else
		# List not installed
		cat <<EOT
<button name="instlist" value="$letter" data-icon="@install@">$(_ 'Install')</button>
EOT
	fi
	echo '</td></tr>'
done

	cat <<EOT
			</tbody>
		</table>
	</form>
</section>
EOT

xhtml_footer
exit 0
