#!/bin/sh
#
# TazPKG CGI interface - Manage packages via the a browse
#
# This CGI interface intensively use tazpkg to manage package and have
# it how code for some tasks. Please KISS it important and keep speed
# in mind. Thanks, Pankso.
#
# (C) 2011 SliTaz GNU/Linux - GNU gpl v2
#
echo "Content-Type: text/html"
echo ""

. tazpanel.conf

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpkg-cgi'
export TEXTDOMAIN

# xHTML 5 header
cat $HEADER | sed s'/%TITLE%/Tazpkg/'
cat << EOT
<form class="search" method="get" action="$SCRIPT_NAME">
	<p>
		`gettext "Search":`
		<input type="text" name="search" size="20">
	</p>
</form>
EOT

# DEBUG mode
[ $DEBUG == "1" ] && echo "<p class='debug'>$REQUEST_METHOD ${QUERY_STRING}</p>"

# We need packages information for list and search
parse_packages_desc() {
while read line
	do
		echo '<tr>'
		pkg=$(echo $line | cut -d "|" -f 1)
		vers=$(echo $line | cut -d "|" -f 2)
		desc=$(echo $line | cut -d "|" -f 3)
		web=$(echo $line | cut -d "|" -f 5)
		imgs=styles/$STYLE/images
		if [ -d installed/$pkg ]; then
			echo -e "<td><input type='checkbox' name='pkg' value=\"$pkg\">\n
				<img src='$IMAGES/tazpkg-installed.png'/>$pkg</td>"
		else
			echo -e "<td><input type='checkbox' name='pkg' value=\"$pkg\">\n
				<img src='$IMAGES/tazpkg.png'/>$pkg</td>"
		fi
		echo "<td>$vers</td>"
		echo "<td class='desc'>$desc</td>"
		echo "<td><a href='$web'>web</a></td>"
		echo '</tr>'
	done
}

# Remove status and ESC char from tazpkg commands output
filter_tazpkg_msgs() {
	grep ^[a-zA-Z0-9] | sed s'/\.*\]//'
}

# Display a full summary of packages stats
packages_summary() {
	gettext "Installed packages : "
	ls $INSTALLED | wc -l
	gettext "Mirrored packages  : "
	cat $LOCALSTATE/packages.list | wc -l
	gettext "Last recharge      : "
	stat -c %y $LOCALSTATE/packages.list | sed 's/\(:..\):.*/\1/'
	gettext "Installed files    : "
	cat $INSTALLED/*/files.list | wc -l
}

#
# xHTML functions
#

table_start() {
	cat << EOT
<table>
	<tbody>
		<tr id="thead">
			<td>`gettext "Name"`</td>
			<td>`gettext "Version"`</td>
			<td>`gettext "Description"`</td>
			<td>`gettext "Web"`</td>
		</tr>
EOT
}

table_end () {
	cat << EOT
	</tbody>
</table>
EOT
}

list_actions() {
	cat << EOT
	<p>
		`gettext "Selection:"`
		<input type="submit" name="do" value="remove" />
		`gettext "List:"`
		<a href='$SCRIPT_NAME?list-all'>`gettext "All packages"`</a> |
		<a href='$SCRIPT_NAME?recharge'>`gettext "Recharge"`</a>
	</p>
EOT
}

list_all_actions() {
	cat << EOT
	<p>
		`gettext "Selection:"`
		<input type="submit" name="do" value="install" />
		<input type="submit" name="do" value="remove" />
		`gettext "List:"`
		<a href='$SCRIPT_NAME?list'>`gettext "My packages"`</a> |
		<a href='$SCRIPT_NAME?recharge'>`gettext "Recharge"`</a>
	</p>
EOT
}

#
# Commands
#

case "$QUERY_STRING" in
	list)
		# List installed packages. This is the default because parsing
		# the full packages.desc can be long and take some resources
		cd /var/lib/tazpkg/installed
		echo "<form method='get' action='$SCRIPT_NAME'>"
		list_actions
		table_start
		for pkg in *
		do
			. $pkg/receipt
			echo '<tr>'
			# Use default tazpkg icon since all packages displayed are
			# installed
			echo "<td class='pkg'>
				<input type='checkbox' name='pkg' value=\"$pkg\" />
				<a href='$SCRIPT_NAME?info=$pkg'><img
					src='$IMAGES/tazpkg.png'/></a>$pkg</td>"
			echo "<td>$VERSION</td>"
			echo "<td class='desc'>$SHORT_DESC</td>"
			echo "<td><a href='$WEB_SITE'>web</a></td>"
			echo '</tr>'
		done
		table_end
		list_actions
		echo '</form>' ;;
	list-all)
		# List all available packages on mirror
		cd /var/lib/tazpkg
		echo "<form method='get' action='$SCRIPT_NAME'>"
		list_all_actions
		table_start
		cat packages.desc | parse_packages_desc
		table_end
		list_all_actions
		echo '</form>' ;;
	search=*)
		# Search for packages
		pkg=${QUERY_STRING#*=}
		cd /var/lib/tazpkg
		cat << EOT
<form method="get" action="$SCRIPT_NAME">
	<p>
		`gettext "Selection:"`
		<input type="submit" name="do" value="install" />
		<input type="submit" name="do" value="remove" />
		`gettext "List:"`
		<a href='$SCRIPT_NAME?list'>`gettext "My packages"`</a> |
		<a href='$SCRIPT_NAME?list-all'>`gettext "All packages"`</a> |
		<a href='$SCRIPT_NAME?recharge'>`gettext "Recharge"`</a>
	</p>
EOT
		table_start
		grep $pkg packages.desc | parse_packages_desc
		table_end
		echo '</form>' ;;
	recharge)
		# Let recharge the packages list
		echo '<p>'
		gettext "Recharging the packages lists..."
		echo '</p><pre>'
		tazpkg recharge | filter_tazpkg_msgs
		echo '</pre><p>'
		gettext "Packages lists are up-to-date"
		echo '</p>' ;;
	do=*)
		# Do an action on one or some packages
		cmdline=`echo ${QUERY_STRING#do=} | sed s'/&/ /g'`		
		cmd=`echo ${cmdline} | awk '{print $1}'`		
		pkgs=`echo $cmdline | sed -e s'/+/ /g' -e s'/pkg=//g' -e s/$cmd//`
		[ $cmd == install ] && cmd=get-install
		[ $DEBUG == "1" ] && echo "<p class='debug'>cmd: $cmd</p><p>pkgs: $pkgs </p>"
		for pkg in $pkgs
		do
			echo '<p>'
			gettext "Executing: tazpkg $cmd $pkg"
			echo '</p><pre>'
			echo 'y' | tazpkg $cmd $pkg 2>/dev/null | filter_tazpkg_msgs
			echo '</pre>'
		done ;;
	info=*)
		pkg=${QUERY_STRING#*=}
		. $INSTALLED/$pkg/receipt
		cat << EOT
<p>
	`gettext "List:"`
	<a href='$SCRIPT_NAME?list'>`gettext "My packages"`</a>
</p>
<pre>
Name        : $PACKAGE
Version     : $VERSION
Description : $SHORT_DESC
Depends     : 

Website     : <a href="$WEB_SITE">$WEB_SITE</a>
Sizes       : $PACKED_SIZE/$UNPACKED_SIZE
Files       : `cat $INSTALLED/$pkg/files.list | wc -l`
</pre>

<p>`gettext "Installed files"`</p>
<pre>
`cat $INSTALLED/$pkg/files.list`
</pre>
EOT
		;;
	*)
		# Default to summary
		cat << EOT
`gettext "List:"`
<a href='$SCRIPT_NAME?list'>`gettext "My packages"`</a> |
<a href='$SCRIPT_NAME?recharge'>`gettext "Recharge"`</a>
<pre>
`packages_summary`
</pre>
EOT
		echo "" ;;
esac

# xHTML 5 footer
cd $PANEL && cat $FOOTER

exit 0
