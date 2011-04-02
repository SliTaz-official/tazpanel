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
		if [ -d $INSTALLED/$pkg ]; then
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
	gettext "Installed packages   : "
	ls $INSTALLED | wc -l
	gettext "Mirrored packages    : "
	cat $LOCALSTATE/packages.list | wc -l
	gettext "Last recharge        : "
	stat -c %y $LOCALSTATE/packages.list | sed 's/\(:..\):.*/\1/'
	gettext "Upgradeable packages : "
	cat $LOCALSTATE/upgradeable-packages.list | wc -l
	gettext "Installed files      : "
	cat $INSTALLED/*/files.list | wc -l
	gettext "Blocked packages     : "
	cat $LOCALSTATE/blocked-packages.list | wc -l
}

#
# xHTML functions
#

search_form() {
	cat << EOT
<div class="search">
<form method="get" action="$SCRIPT_NAME">
	<p>
		`gettext "Search":`
		<input type="text" name="search" size="20">
	</p>
</form>
</div>
EOT
}

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

sub_block() {
	cat << EOT
<div id="sub_block">
	`gettext "List:"`
	<a href='$SCRIPT_NAME?list'>`gettext "My packages"`</a> |
	<a href='$SCRIPT_NAME?list-all'>`gettext "All packages"`</a> |
	<a href='$SCRIPT_NAME?recharge'>`gettext "Recharge"`</a> |
	<a href='$SCRIPT_NAME?upgradeable'>`gettext "Upgradeable"`</a>
</div>
EOT
}

# For my packages list
list_actions() {
	cat << EOT
<p>
	`gettext "Selection:"`
	<input type="submit" name="do" value="remove" />
</p>
EOT
}

# For list-all
list_all_actions() {
	cat << EOT
<p>
	`gettext "Selection:"`
	<input type="submit" name="do" value="install" />
	<input type="submit" name="do" value="remove" />
</p>
EOT
}

# For search and upgrade with JS function to toogle all pkgs
list_full_actions() {
	cat << EOT
<p>
	`gettext "Selection:"`
	<input type="submit" name="do" value="install" />
	<input type="submit" name="do" value="remove" />
	<a href="`cat $PANEL/checkbox.js`">`gettext "Toogle all"`</a>
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
		cd $INSTALLED
		search_form
		sub_block
		cat << EOT
<h2>`gettext "My packages"`</h2>
<form method='get' action='$SCRIPT_NAME'>
<div id="actions">
EOT
		list_actions
		echo '</div>'
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
					src='$IMAGES/tazpkg-installed.png'/></a>$pkg</td>"
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
		cd  $LOCALSTATE
		search_form
		sub_block
		cat << EOT
<h2>`gettext "All packages"`</h2>
<form method='get' action='$SCRIPT_NAME'>
<div id="actions">
EOT
		list_all_actions
		echo '</div>'
		table_start
		cat packages.desc | parse_packages_desc
		table_end
		list_all_actions
		echo '</form>' ;;
	search=*)
		# Search for packages
		pkg=${QUERY_STRING#*=}
		cd  $LOCALSTATE
		search_form
		sub_block
		cat << EOT
<h2>`gettext "All packages"`</h2>
<form method="get" action="$SCRIPT_NAME">
<div id="actions">
EOT
		list_full_actions
		echo '</div>'
		table_start
		grep $pkg packages.desc | parse_packages_desc
		table_end
		echo '</form>' ;;
	recharge)
		# Let recharge the packages list
		search_form
		sub_block
		cat << EOT
<h2>`gettext "Recharge"`</h2>
<form method='get' action='$SCRIPT_NAME'>
<div id="actions">
	<p>`gettext "Recharge lists will check for new or updated packages"`</p>
</div>	
<pre>
EOT
		gettext "Recharging the packages list... please wait"; echo
		tazpkg recharge | filter_tazpkg_msgs
		echo '</pre>'
		echo '<p>'
		gettext "Packages lists are up-to-date"
		echo '</p>' ;;
	upgradeable)
		cd $LOCALSTATE
		search_form
		sub_block
		cat << EOT
<h2>`gettext "Upgradeable packages"`</h2>
<form method="get" action="$SCRIPT_NAME">
<div id="actions">
EOT
		list_full_actions
		tazpkg upgradeable
		echo '</div>'
		table_start
		for pkg in `cat upgradeable-packages.list`
		do
			grep "^$pkg |" $LOCALSTATE/packages.desc | parse_packages_desc
		done
		table_end
		echo '</form>' ;;
	do=*)
		# Do an action on one or some packages
		cmdline=`echo ${QUERY_STRING#do=} | sed s'/&/ /g'`		
		cmd=`echo ${cmdline} | awk '{print $1}'`		
		pkgs=`echo $cmdline | sed -e s'/+/ /g' -e s'/pkg=//g' -e s/$cmd//`
		[ $cmd == install ] && cmd=get-install opt=--forced
		search_form
		sub_block
		cat << EOT
<h2>Tazpkg: $cmd</h2>
<form method="get" action="$SCRIPT_NAME">
<div id="actions">
<p>
EOT
		gettext "Performing task on packages"
		[ $DEBUG == "1" ] && echo "<p class='debug'>cmd: $cmd</p><p>pkgs: $pkgs </p>"
		echo '</p></div>'
		for pkg in $pkgs
		do
			echo '<pre class="nomargin">'
			echo 'y' | tazpkg $cmd $pkg $opt 2>/dev/null | filter_tazpkg_msgs
			echo '</pre>'
		done ;;
	info=*)
		pkg=${QUERY_STRING#*=}
		search_form
		sub_block
		. $INSTALLED/$pkg/receipt
		cat << EOT
<h2>`gettext "Upgradeable packages"`</h2>
<div id="actions">
	<p>`gettext "Detailled information on:" $PACKAGE`</p>
</div>
<pre>
Name        : $PACKAGE
Version     : $VERSION
Description : $SHORT_DESC
Depends     : `for i in $DEPENDS; do echo -n \
	"<a href="$SCRIPT_NAME?info=$i">$i</a> "; done`
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
		
		sub_block
		search_form
		cat << EOT
<h2>`gettext "Summary"`</h2>
<div id="actions">
	<p>`gettext "Overview of all installed and mirrored packages"`</p>
</div>
<pre>
`packages_summary`
</pre>
EOT
		echo "" ;;
esac

# xHTML 5 footer
cd $PANEL && cat $FOOTER

exit 0
