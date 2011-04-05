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

. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel-pkgs'
export TEXTDOMAIN

# xHTML 5 header
xhtml_header

# DEBUG mode
if [ $DEBUG == "1" ]; then
	echo "<p class='debug'>$REQUEST_METHOD ${QUERY_STRING}</p>"
fi

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

# Parse mirrors list to be able to have an icon an remove link
list_mirrors() {
	cat $LOCALSTATE/mirrors | while read line
	do
		cat << EOT
<li><a href="$SCRIPT_NAME?config=rm-mirror=$line"><img
	src="$IMAGES/clear.png" /></a><a href="$line">$line</a></li>
EOT
	done
}

#
# xHTML functions
#

# ENTER will search but user may search for a button, so put one.
search_form() {
	cat << EOT
<div class="search">
	<form method="get" action="$SCRIPT_NAME">
		<p>
			<input type="text" name="search" size="20">
			<input type="submit" value="`gettext "Search"`">
		</p>
	</form>
</div>
EOT
}

table_head() {
	cat << EOT
		<tr id="thead">
			<td>`gettext "Name"`</td>
			<td>`gettext "Version"`</td>
			<td>`gettext "Description"`</td>
			<td>`gettext "Web"`</td>
		</tr>
EOT
}

sub_block() {
	cat << EOT
<div id="sub_block">
	<a href='$SCRIPT_NAME?list'>`gettext "My packages"`</a> |
	<a href='$SCRIPT_NAME?list-all'>`gettext "All packages"`</a> |
	<a href='$SCRIPT_NAME?recharge'>`gettext "Recharge list"`</a> |
	<a href='$SCRIPT_NAME?upgradeable'>`gettext "Upgrade"`</a> |
	<a href='$SCRIPT_NAME?config'>`gettext "Configuration"`</a>
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
	<a href="`cat $PANEL/lib/checkbox.js`">`gettext "Toogle all"`</a>
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
		table_head
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
<h2>`gettext "Search packages"`</h2>
<form method="get" action="$SCRIPT_NAME">
<div id="actions">
EOT
		list_full_actions
		echo '</div>'
		table_start
		table_head
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
	<p>
		`gettext "Recharge will check for new or updated packages...
		please wait"`
	</p>
</div>	
<pre>
EOT
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
		table_head
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
		echo '</p></div>'
		echo '<pre class="pre_main">'
		gettext "Executing $cmd for:$pkgs"
		echo '</pre>'
		for pkg in $pkgs
		do
			echo '<pre>'
			echo 'y' | tazpkg $cmd $pkg $opt 2>/dev/null | filter_tazpkg_msgs
			echo '</pre>'
		done ;;
	info=*)
		pkg=${QUERY_STRING#*=}
		search_form
		sub_block
		. $INSTALLED/$pkg/receipt
		cat << EOT
<h2>`gettext "Package info"`</h2>
<div id="actions">
	<p>`gettext "Detailled information on:"` $PACKAGE</p>
</div>
<pre>
Name        : $PACKAGE
Version     : $VERSION
Description : $SHORT_DESC
Maintainer  : $MAINTAINER
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
	config*)
		# Tazpkg configuration page
		cmd=${QUERY_STRING#*=}
		case "$cmd" in
			clean)
				rm -rf /var/cache/tazpkg/* ;;
			add-mirror*=http*|add-mirror*=ftp*)
				# Decode url
				mirror=`httpd -d ${cmd#*=}`
				echo "$mirror" >> $LOCALSTATE/mirrors ;;
			rm-mirror=http://*|rm-mirror=ftp://*)
				mirror=${QUERY_STRING#*=rm-mirror=}
				sed -i -e "s@$mirror@@" -e '/^$/d' $LOCALSTATE/mirrors ;;
		esac
		cache_files=`find /var/cache/tazpkg -name *.tazpkg | wc -l`
		cache_size=`du -sh /var/cache/tazpkg`
		sub_block
		cat << EOT
<h2>`gettext "Configuration"`</h2>
<div>
	<p>`gettext "Tazpkg configuration and settings"`</p>
</div>
<div>
	<form method="get" action="$SCRIPT_NAME">
		<p>
			`gettext "Packages in the cache:"` $cache_files ($cache_size)
			<input type="hidden" name="config" value="clean" />
			<input type="submit" value="Clean" />
		</p>
	</form>
</div>

<h3>`gettext "Current mirror list"`</h3>
<div class="box">
	<ul>
		`list_mirrors`
	</ul>
</div>
<form method="get" action="$SCRIPT_NAME">
	<p>
		<input type="hidden" name="config" value="add-mirror" />
		<input type="text" name="mirror" size="60">
		<input type="submit" value="Add mirror" />
	</p>
</form>
EOT
		 ;;
	*)
		#
		# Default to summary
		#
		search_form
		sub_block
		cat << EOT
<h2>`gettext "Summary"`</h2>
<div id="actions">
	<p>`gettext "Overview of all installed and mirrored packages"`</p>
</div>
<pre class="pre_main">
`packages_summary`
</pre>
<h3>`gettext "Latest log entries"`</h3>
<pre>
`tail -n 6 /var/log/tazpkg.log | fgrep "-" | \
	awk '{print $1, $2, $3, $4, $5, $6, $7}'`
</pre>

EOT
		;;
esac

# xHTML 5 footer
xhtml_footer
exit 0
