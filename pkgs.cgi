#!/bin/sh
#
# TazPKG CGI interface - Manage packages via the a browse
#
# This CGI interface intensively use tazpkg to manage package and have
# it own code for some tasks. Please KISS it important and keep speed
# in mind. Thanks, Pankso.
#
# (C) 2011 SliTaz GNU/Linux - GNU gpl v3
#
echo "Content-Type: text/html"
echo ""

. lib/libtazpanel
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='tazpanel'
export TEXTDOMAIN

# xHTML 5 header
TITLE="- Packages"
xhtml_header | sed 's/id="content"/id="content-sidebar"/'

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
				<a href='$SCRIPT_NAME?info=$pkg'>
				<img src='$IMAGES/tazpkg-installed.png'/>$pkg</a></td>"
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
	gettext "Last recharge        : "
	stat=`stat -c %y $LOCALSTATE/packages.list | \
		sed 's/\(:..\):.*/\1/' | awk '{print $1}'`
	mtime=`find /var/lib/tazpkg/packages.list -mtime +10`
	echo -n "$stat "
	if [ "$mtime" ]; then
		echo "(Older than 10 days)"
	else
		echo "(Not older than 10 days)"
	fi
	gettext "Installed packages   : "
	ls $INSTALLED | wc -l
	gettext "Mirrored packages    : "
	cat $LOCALSTATE/packages.list | wc -l
	gettext "Upgradeable packages : "
	cat $LOCALSTATE/upgradeable-packages.list | wc -l
	#gettext "Installed files      : "
	#cat $INSTALLED/*/files.list | wc -l
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

sidebar() {
	cat << EOT
<div id="sidebar">
	<h4>Categories</h4>
	<a class="active_base-system" href="$SCRIPT_NAME?cat=base-system">Base-system</a>
	<a class="active_x-window" href="$SCRIPT_NAME?cat=x-window">X window</a>
	<a class="active_utilities" href="$SCRIPT_NAME?cat=utilities">Utilities</a>
	<a class="active_network" href="$SCRIPT_NAME?cat=network">Network</a>
	<a class="active_games" href="$SCRIPT_NAME?cat=games">Games</a>
	<a class="active_graphics" href="$SCRIPT_NAME?cat=graphics">Graphics</a>
	<a class="active_office" href="$SCRIPT_NAME?cat=office">Office</a>
	<a class="active_multimedia" href="$SCRIPT_NAME?cat=multimedia">Multimedia</a>
	<a class="active_developement" href="$SCRIPT_NAME?cat=development">Development</a>
	<a class="active_system-tools" href="$SCRIPT_NAME?cat=system-tools">System tools</a>
	<a class="active_security" href="$SCRIPT_NAME?cat=security">Security</a>
	<a class="active_misc" href="$SCRIPT_NAME?cat=misc">Misc</a>
	<a class="active_meta" href="$SCRIPT_NAME?cat=meta">Meta</a>
	<a class="active_non-free" href="$SCRIPT_NAME?cat=non-free">Non free</a>
</div>
EOT
}

# For my packages list
list_actions() {
	cat << EOT
<div class="float-left">
	`gettext "Selection:"`
	<input type="submit" name="do" value="Remove" />
</div>
<div class="float-right">
	`gettext "List:"`
	<input type="submit" name="recharge" value="Recharge" />
	<input type="submit" name="upgradeable" value="Upgrade" />
</div>
EOT
}

# For list-cat
list_cat_action() {
	cat << EOT
<div class="float-left">
	`gettext "Selection:"`
	<input type="submit" name="do" value="Install" />
	<input type="submit" name="do" value="Remove" />
</div>
<div class="float-right">
	`gettext "List:"`
	<input type="submit" name="recharge" value="Recharge" />
	<input type="submit" name="upgradeable" value="Upgrade" />
	<a class="button" href='$SCRIPT_NAME?list'>
		<img src="$IMAGES/tazpkg.png" />`gettext "My packages"`</a>
</div>
EOT
}

# For search with JS function to toogle all pkgs
list_full_actions() {
	cat << EOT
<div class="float-left">
	`gettext "Selection:"`
	<input type="submit" name="do" value="Install" />
	<input type="submit" name="do" value="Remove" />
	<a href="`cat $PANEL/lib/checkbox.js`">`gettext "Toogle all"`</a>
</div>
<div class="float-right">
	`gettext "List:"`
	<input type="submit" name="recharge" value="Recharge" />
	<input type="submit" name="upgradeable" value="Upgrade" />
	<a class="button" href='$SCRIPT_NAME?list'>
		<img src="$IMAGES/tazpkg.png" />`gettext "My packages"`</a>
</div>
EOT
}

# For upgrade with JS function to toogle all pkgs and no 'Upgrade' button
list_up_actions() {
	cat << EOT
<div class="float-left">
	`gettext "Selection:"`
	<input type="submit" name="do" value="Install" />
	<input type="submit" name="do" value="Remove" />
	<a href="`cat $PANEL/lib/checkbox.js`">`gettext "Toogle all"`</a>
</div>
<div class="float-right">
	`gettext "List:"`
	<input type="submit" name="recharge" value="Recharge" />
	<a class="button" href='$SCRIPT_NAME?list'>
		<img src="$IMAGES/tazpkg.png" />`gettext "My packages"`</a>
</div>
EOT
}

#
# Commands
#

case "$QUERY_STRING" in
	list*)
		# List installed packages. This is the default because parsing
		# the full packages.desc can be long and take some resources
		cd $INSTALLED
		search_form
		sidebar
		LOADING_MSG="Listing... please wait"
		loading_msg
		cat << EOT
<h2>`gettext "My packages"`</h2>
<form method='get' action='$SCRIPT_NAME'>
<div id="actions">
EOT
		list_actions
		echo '</div>'
		table_start
		table_head
		for pkg in *
		do
			. $pkg/receipt
			echo '<tr>'
			# Use default tazpkg icon since all packages displayed are
			# installed
			echo "<td class='pkg'>
				<input type='checkbox' name='pkg' value=\"$pkg\" />
				<a href='$SCRIPT_NAME?info=$pkg'><img
					src='$IMAGES/tazpkg-installed.png'/>$pkg</a></td>"
			echo "<td>$VERSION</td>"
			echo "<td class='desc'>$SHORT_DESC</td>"
			echo "<td><a href='$WEB_SITE'>web</a></td>"
			echo '</tr>'
		done
		table_end
		list_actions
		echo '</form>' ;;
	cat*)
		# List all available packages by category on mirror. Listing all
		# packages is to resource intensive and not usefull.
		cd  $LOCALSTATE
		category=${QUERY_STRING#cat=}
		[ "${QUERY_STRING}" == "cat" ] && category="base-system"
		search_form
		sidebar | sed s/"active_${category}"/"active"/
		cat << EOT
<h2>`gettext "Category:"` $category</h2>
<form method='get' action='$SCRIPT_NAME'>
<div id="actions">
EOT
		list_cat_action
		echo '</div>'
		table_start
		table_head
		grep "| $category |" packages.desc | parse_packages_desc
		table_end
		list_cat_action
		echo '</form>' ;;
	search=*)
		# Search for packages
		pkg=${QUERY_STRING#*=}
		cd  $LOCALSTATE
		search_form
		sidebar
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
	recharge*)
		# Let recharge the packages list
		search_form
		sidebar
		cat << EOT
<h2>`gettext "Recharge"`</h2>
<form method='get' action='$SCRIPT_NAME'>
<div id="actions">
	<div class="float-left">
		<p>
			`gettext "Recharge will check for new or updated packages...
please wait"`
		</p>
	</div>
	<div class="float-right">
		<p>
			<a class="button" href='$SCRIPT_NAME?list'>
				<img src="$IMAGES/tazpkg.png" />`gettext "My packages"`</a>
		</p>
	</div>
</div>
<pre>
EOT
		tazpkg recharge | filter_tazpkg_msgs
		echo '</pre>'
		echo '<p>'
		gettext "Packages lists are up-to-date"
		echo '</p>' ;;
	upgradeable*)
		cd $LOCALSTATE
		search_form
		sidebar
		cat << EOT
<h2>`gettext "Upgradeable packages"`</h2>
<form method="get" action="$SCRIPT_NAME">
<div id="actions">
EOT
		list_up_actions
		tazpkg upgradeable
		echo '</div>'
		table_start
		table_head
		for pkg in `cat upgradeable-packages.list`
		do
			grep "^$pkg |" $LOCALSTATE/packages.desc | parse_packages_desc
		done
		table_end
		list_up_actions
		echo '</form>' ;;
	do=*)
		# Do an action on one or some packages
		cmdline=`echo ${QUERY_STRING#do=} | sed s'/&/ /g'`		
		cmd=`echo ${cmdline} | awk '{print $1}'`		
		pkgs=`echo $cmdline | sed -e s'/+/ /g' -e s'/pkg=//g' -e s/$cmd//`
		case $cmd in
			install|Install)
				cmd=get-install opt=--forced ;;
			remove|Remove)
				cmd=remove ;;
		esac
		search_form
		sidebar
		cat << EOT
<h2>Tazpkg: $cmd</h2>
<form method="get" action="$SCRIPT_NAME">
<div id="actions">
	<div class="float-left">
		<p>
			`gettext "Performing task on packages... please wait"`
		</p>
	</div>
	<div class="float-right">
		<p>
			<a class="button" href='$SCRIPT_NAME?list'>
				<img src="$IMAGES/tazpkg.png" />`gettext "My packages"`</a>
		</p>
	</div>
</div>
EOT
		echo '<pre class="pre-main">'
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
		sidebar
		. $INSTALLED/$pkg/receipt
		files=`cat $INSTALLED/$pkg/files.list | wc -l`
		cat << EOT
<h2>`gettext "Package"` $PACKAGE</h2>
<div id="actions">
	<div class="float-left">
		<p>
			<a class="button" href='$SCRIPT_NAME?do=remove&$pkg'>`gettext "Remove"`</a>
		</p>
	</div>
	<div class="float-right">
		<p>
			<a class="button" href='$SCRIPT_NAME?list'>
				<img src="$IMAGES/tazpkg.png" />`gettext "My packages"`</a>
		</p>
	</div>
</div>
<pre>
Name        : $PACKAGE
Version     : $VERSION
Description : $SHORT_DESC
Category    : $CATEGORY
Maintainer  : $MAINTAINER
Depends     : `for i in $DEPENDS; do echo -n \
	"<a href="$SCRIPT_NAME?info=$i">$i</a> "; done`
Website     : <a href="$WEB_SITE">$WEB_SITE</a>
Sizes       : $PACKED_SIZE/$UNPACKED_SIZE
</pre>

<p>`gettext "Installed files:"` `cat $INSTALLED/$pkg/files.list | wc -l`</p>
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
		sidebar
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
		sidebar
		cat << EOT
<h2>`gettext "Summary"`</h2>
<div id="actions">
	`gettext "Overview of all installed and mirrored packages"`
</div>
<pre class="pre-main">
`packages_summary`
</pre>
<a class="button" href='$SCRIPT_NAME?list'>
	<img src="$IMAGES/tazpkg.png" />`gettext "My packages"`</a>
<a class="button" href='$SCRIPT_NAME?recharge'>
	<img src="$IMAGES/recharge.png" />`gettext "Recharge list"`</a>
<a class="button" href='$SCRIPT_NAME?upgradeable'>
	<img src="$IMAGES/update.png" />`gettext "Check upgrade"`</a>
<a class="button" href='$SCRIPT_NAME?config'>
	<img src="$IMAGES/edit.png" />`gettext "Configuration"`</a>

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
