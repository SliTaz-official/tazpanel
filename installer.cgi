#!/bin/sh
#
# Main CGI interface for Tazinst, the SliTaz installer.
#
# Copyright (C) 2012 SliTaz GNU/Linux - BSD License
#
# Authors : Dominique Corbex <domcox@slitaz.org>
#

VERSION=0.29

# Common functions from libtazpanel
. lib/libtazpanel
header
get_config

# Include gettext helper script.
. /usr/bin/gettext.sh

# Export package name for gettext.
TEXTDOMAIN='installer'
export TEXTDOMAIN

TITLE="- Installer"

# Tazinst required version
TAZINST_REQUIRED_VERSION="3.3"

# Tazinst setup file
INSTFILE=/var/lib/tazinst.conf


write_setup()
{
	if [ -e "$INSTFILE" ]; then
		# Install type
		INST_TYPE=$(GET INST_TYPE)
		# Source File
		case "$INST_TYPE" in
			usb)
				SRC_FILE=$(GET SRC_USB) ;;
			iso)
				SRC_FILE=$(GET SRC_ISO) ;;
			web)
				SRC_FILE=$(GET SRC_WEB) ;;
		esac
		SRC_FILE=$(echo "$SRC_FILE" | sed 's/\//\\\//'g)
		[ -n $(GET URL) ] && SRC_WEB=$(GET URL)
		# Main Partition
		TGT_PARTITION=$(echo "$(GET TGT_PARTITION)" | sed 's/\//\\\//'g)
		[ -n "$(GET MAIN_FMT)" ] && TGT_FS=$(GET MAIN_FS) || TGT_FS=""
		# Home Partition
		if [ -n "$(GET HOME_SELECT)" ] ; then
			TGT_HOME=$(echo "$(GET TGT_HOME)" | sed 's/\//\\\//'g)
			[ -n "$(GET HOME_FS)" ] && TGT_HOME_FS=$(GET HOME_FS)
		else
			TGT_HOME=""
			TGT_HOME_FS=""
		fi
		# Hostname
		TGT_HOSTNAME=$(GET TGT_HOSTNAME)
		# Root pwd
		TGT_ROOT_PWD=$(GET TGT_ROOT_PWD)
		# User Login
		TGT_USER=$(GET TGT_USER)
		# User Pwd
		TGT_USER_PWD=$(GET TGT_USER_PWD)
		# Grub
		TGT_GRUB=$(GET TGT_GRUB)
		[ "$TGT_GRUB" == "yes" ] || TGT_GRUB=no
		# Win Dual-Boot
		TGT_WINBOOT=$(GET TGT_WINBOOT)

		# Save changes to INSTFILE
		sed -i s/"^INST_TYPE=.*"/"INST_TYPE=\"$INST_TYPE\"/" $INSTFILE
		sed -i s/"^SRC_FILE=.*"/"SRC_FILE=\"$SRC_FILE\"/" $INSTFILE
		sed -i s/"^TGT_PARTITION=.*"/"TGT_PARTITION=\"$TGT_PARTITION\"/" $INSTFILE
		sed -i s/"^TGT_FS=.*"/"TGT_FS=\"$TGT_FS\"/" $INSTFILE
		sed -i s/"^TGT_HOME=.*"/"TGT_HOME=\"$TGT_HOME\"/" $INSTFILE
		sed -i s/"^TGT_HOME_FS=.*"/"TGT_HOME_FS=\"$TGT_HOME_FS\"/" $INSTFILE
		sed -i s/"^TGT_HOSTNAME=.*"/"TGT_HOSTNAME=\"$TGT_HOSTNAME\"/" $INSTFILE
		sed -i s/"^TGT_ROOT_PWD=.*"/"TGT_ROOT_PWD=\"$TGT_ROOT_PWD\"/" $INSTFILE
		sed -i s/"^TGT_USER=.*"/"TGT_USER=\"$TGT_USER\"/" $INSTFILE
		sed -i s/"^TGT_USER_PWD=.*"/"TGT_USER_PWD=\"$TGT_USER_PWD\"/" $INSTFILE
		sed -i s/"^TGT_GRUB=.*"/"TGT_GRUB=\"$TGT_GRUB\"/" $INSTFILE
		sed -i s/"^TGT_WINBOOT=.*"/"TGT_WINBOOT=\"$TGT_WINBOOT\"/" $INSTFILE
	fi
}

read_setup()
{
	# various checks on setup file
	if [ -e "$INSTFILE" ]; then
		# validity check + reformat output
		tazinst check $INSTFILE | awk '
BEGIN{
	fmt1="<span class=\"msg-nok\">"
	fmt2="<br /></span>"
	OFS=""
	}
{
	# make html compliant
	str=$0
	gsub(/\[1m/,"",str)
	gsub(/\[0m/,"",str)
	gsub(/\s/,"\\&nbsp;",str)
	gsub(/</,"\\&lt",str)
	gsub(/>/,"\\&gt",str)
	a[i++]=str
} END {
	{print fmt1,a[i-1],fmt2}
	{for (j=0; j<i-1;) print fmt1,substr(a[j++],3),fmt2}
}'
	else
		# no setup file found: creating
		gettext "Creating setup file $INSTFILE."
		tazinst new $INSTFILE
		if [ ! -e "$INSTFILE" ]; then
			cat <<EOT
<span class="msg-nok">$(gettext "Setup File Error")<br />
$(gettext "The setup file <strong>$INSTFILE</strong> doesn't exist.")</span><br />
EOT
		else
			if [ ! -r $INSTFILE ]; then
				cat <<EOT
<span class="msg-nok">$(gettext "Setup File Error")<br />
$(gettext "The setup file <strong>$INSTFILE</strong> is not readable. 
Check permissions and ownership.")</span><br />
EOT
			fi	
		fi
	fi
	# read setup file
	. $INSTFILE
}

select_action()
{
	cat <<EOT
<div id="wrapper">
	<h2>$(gettext "SliTaz Installer")</h2>
<p>
	$(gettext "The SliTaz Installer installs or upgrades SliTaz to a hard disk
	drive from a device like a Live-CD or LiveUSB key, from a SliTaz ISO file,
	or from the web by downloading an ISO file.")
<p>
</div>
EOT
}

select_install()
{
	cat <<EOT
<div class="box">
	<h4>$(gettext "Install")</h4>
<p>
	$(gettext "Install SliTaz on a partition of your hard disk drive. If
	you decide to format your partition, all data will be lost. If you do not
	format, all data except for any existing /home directory will be removed, 
	the home directory will be kept as is.")
</p>
<p>
	$(gettext "Before installation, you may need to create or resize partitions
	on your hard disk drive in order to make space for SliTaz GNU/Linux.
	You can graphically manage your partitions with Gparted")
</p>
</div>
<p>
<a class="button" href="$SCRIPT_NAME?page=partitioning">$(gettext "Install SliTaz")</a>
EOT
}

select_upgrade()
{
	cat <<EOT
<div class="box">
	<h4>$(gettext "Upgrade")</h4>
<p>
	$(gettext "Upgrade an already installed SliTaz system on your hard disk
	drive. Your /home /etc /var/www directories will be kept, all other directories
	will be removed. Any additional packages added to your old Slitaz system
	will be updated as long you have an active internet connection.")
</p>
</div>
<p>
	<a class="button" href="$SCRIPT_NAME?page=upgrade">$(gettext "Upgrade SliTaz")</a>
</p>
EOT
}

select_gparted()
{
	cat <<EOT
<h4>$(gettext "Partitioning")</h4>
<div class="box">
<p>
	$(gettext "On most used systems, the hard drive is already dedicated to 
	partitions for Windows<sup>&copy;</sup>, or Linux, or another operating 
	system. You'll need to resize these partitions in order to make space for
	SliTaz GNU/Linux. SliTaz will co-exist with other operating systems already
	installed on your hard drive.") 
</p>
<p>
	$(gettext "The amount of space needed depends on how much software you 
	plan to install	and how much space you require for users. It's conceivable
	that you could run a minimal SliTaz system in 300 megs or less, but 2 gigs
	is indeed more comfy.")
<p>
	$(gettext "A separate home partition, and a partition that will be used 
	as Linux swap space may be created if needed. Slitaz detects and uses swap
	partitions automatically.")
</p>
</p>
</div>
<div class="box">
<p>
	$(gettext "You can graphically manage your partitions with Gparted. GParted
	is a partition editor for graphically managing your disk partitions. Gparted
	allows you to create, destroy, resize and copy partitions without data
	loss.")
</p>
<p>
	$(gettext "Gparted supports ext2, ext3, ext4, linux swap, ntfs and fat32
	filesystems right out of the box. Support for xjs, jfs, hfs and other
	filesystems is available as well but you first need to add drivers for 
	these filesystems by installing the related packages xfsprogs, jfsutils,
	linux-hfs and so on.")
</p>
</div>
<a class="button" href="$SCRIPT_NAME?page=gparted">$(gettext "Execute Gparted")</a>
<h5>$(gettext "Continue installation")</h5>
	$(gettext "Once you've made room for SliTaz on your drive,	you
	should be able to continue installation.")

<hr />
<a class="button" value="$1" href="$SCRIPT_NAME?page=home" >
	$(gettext "Back to Installer Start Page")</a>
<a class="button" value="$2" href="$SCRIPT_NAME?page=install">
	$(gettext "Continue Installation")</a>
EOT
}

display_action()
{
	case $1 in
		install)
			cat << EOT
<div id="wrapper">
<h3>$(gettext "Install SliTaz")</h3>
<p>$(gettext "You're going to install SliTaz on a partition of your hard disk drive. If
	you decide to format your HDD, all data will be lost. If you do not 
	format, all data except for any existing /home directory will be removed, 
	the home directory will be kept as is.")<p>
</div>
<input type="hidden" name="INST_ACTION" value="$1">
EOT
			;;
		upgrade)
			cat << EOT
<div id="wrapper">
<h2>$(gettext "Upgrade SliTaz")</h2>
<p>$(gettext "You're going to upgrade an already installed SliTaz system on your hard disk
	drive. Your /home /etc /var/www directories will be kept, all other directories
	will be removed. Any additional packages added to your old Slitaz system
	will be updated as long you have an active internet connection.")<p>
</div>
<input type="hidden" name="INST_ACTION" value="$1">
EOT
			;;
	esac
}

select_source()
{
	cat <<EOT
<a name="source"></a>
<h4>$(gettext "Slitaz source media")</h4>
<div class="box">
<input type="radio" name="INST_TYPE" value="cdrom" $([ "$INST_TYPE" == "cdrom" ] && echo "checked") id="cdrom" />
<label for="cdrom">$(gettext "LiveCD")</td></label>
<br />
<input type="radio" name="INST_TYPE" value="usb" $([ "$INST_TYPE" == "usb" ] && echo "checked") id="usb" />
<label for="usb">$(gettext "LiveUSB"):
<select name="SRC_USB">
EOT
	# List disks if plugged USB device
	usb=0
	if [ -d /proc/scsi/usb-storage ]; then
		for DEV in /sys/block/sd* ; do
			if readlink $DEV | grep -q usb; then
				DEV=$(basename $DEV)
				if [ -d /sys/block/${DEV}/${DEV}1 ]; then
					for i in $(fdisk -l /dev/$DEV | awk '/^\/dev/ {printf "%s ", $1}') ; do
						echo "<option value='$i' $([ "$i" == "$SRC_FILE" ] && echo "selected") >$i</option>"
						usb=$usb+1
					done
				fi
			fi
		done
	fi
	if [ $usb -lt 1 ]; then
		echo "<option value="">$(gettext "Not found")</option>"
	fi
	cat << EOT
</select>
</label>
<br />
<input type="radio" name="INST_TYPE" value="iso" $([ "$INST_TYPE" == "iso" ] && echo "checked") id="iso" />
<label for="iso">$(gettext "ISO file"):</label>
<input type="url" size="50" name="SRC_ISO" $([ "$INST_TYPE" == "iso" ] && echo -e "value=\"$SRC_FILE\"") placeholder="$(gettext "Full path to the ISO image file")" />
<br />
<input type="radio" name="INST_TYPE" value="web" $([ "$INST_TYPE" == "web" ] && echo "checked") id="web" />
<label for="web">$(gettext "Web"):
<a class="button" onclick="document.forms['ConfigForm'].url.value = '$(tazinst showurl stable)'; return true;">$(gettext "Stable")</a>
<a class="button" onclick="document.forms['ConfigForm'].url.value = '$(tazinst showurl cooking)'; return true;">$(gettext "Cooking")</a>
$(gettext "URL:")
<input id="url" type="url" size="55" name="SRC_WEB" value="$get_SRC_WEB" placeholder="$(gettext "Full url to an ISO image file")" />
</label>
</div>
EOT
}

select_hdd()
{
cat <<EOT
	<a name="hdd"></a>
	<h4></span>$(gettext "Hard Disk Drive")</h4>
EOT
}

select_partition()
{
	cat <<EOT
<div class="box">
<a name="partition"></a>
$(gettext "Install Slitaz to partition:")
<select name="TGT_PARTITION">
EOT
	# List partitions
	if fdisk -l | grep -q ^/dev/ ; then
		echo "<option value="">$(gettext "None")</option>"
		for i in $(fdisk -l | awk '/^\/dev/ {printf "%s " $1}'); do
			echo "<option value='$i' $([ "$i" == "$TGT_PARTITION" ] && echo "selected")>$i</option>"
		done
	else
		echo "<option value="">$(gettext "Not found")</option>"
	fi
	cat << EOT
</select>
<br />
<input type="checkbox" name="MAIN_FMT" value="yes" $([ -n "$TGT_FS" ] && echo "checked") id="mainfs" />
<label for="mainfs">$(gettext "Format partition as"):</label>
<select name="MAIN_FS">
EOT
	scan_mkfs
	for i in $FS
	do
		echo  "<option value='$i' $([ "$i" == "$TGT_FS" ] && echo "selected")>$i</option>"
	done
	cat <<EOT
</select>
</div>
EOT
}

select_old_slitaz()
{
	cat <<EOT
<div class="box">
<a name="partition"></a>
$(gettext "Existing SliTaz partition to upgrade:")
<select name="TGT_PARTITION">
EOT
	# List partitions
	if fdisk -l | grep -q ^/dev/ ; then
		echo "<option value="">$(gettext "None")</option>"
		for i in `blkid | cut -d ":" -f 1`; do
			echo "<option value='$i' $([ "$i" == "$TGT_PARTITION" ] && echo "selected")>$i</option>"
		done
	else
		echo "<option value="">$(gettext "Not found")</option>"
	fi
	cat <<EOT
</select>
</div>
EOT
}

select_options()
{
	cat <<EOT
<a name="options"></a>
<h4></span>$(gettext "Options")</h4>
EOT
}

select_home()
{
	cat <<EOT
<div>
<a name="home"></a>
<h5>$(gettext "home partition")</h5>
<input type="checkbox" name="HOME_SELECT" value="yes" $([ -n "$TGT_HOME" ] && echo "checked") id="homepart" />
<label for="homepart">$(gettext "Use a separate partition for /home:")</label>
<select name="TGT_HOME">
EOT
	# List disk if plugged USB device
	if fdisk -l | grep -q ^/dev/ ; then
		echo "<option value="">$(gettext "None")</option>"
		for i in $(fdisk -l | awk '/^\/dev/ {printf "%s " $1}'); do
			echo "<option value='$i' $([ "$i" == "$TGT_HOME" ] && echo "selected")>$i</option>"
		done
	else
		echo "<option value="">$(gettext "Not found")</option>"
	fi
cat <<EOT
</select>
	
<input type="checkbox" name="HOME_FMT" value="yes" $([ -n "$TGT_HOME_FS" ] && echo "checked") id="homefs" />
<label for="homefs">$(gettext "Format partition as:")</label>
<select name="HOME_FS">"
EOT
	for i in $FS
	do
		echo  "<option value='$i' $([ "$i" == "$TGT_HOME_FS" ] && echo "selected")>$i</option>"
	done
	cat <<EOT
</select>
</div>
EOT
}

select_hostname()
{
cat << EOT
<div>
<a name="hostname"></a>
<h5>$(gettext "Hostname")</h5>
$(gettext "Set Hostname to:")
<input type="text" id="hostname" name="TGT_HOSTNAME" value="$TGT_HOSTNAME" placeholder="$(gettext "Name of your system")" onkeyup="checkLogin('hostname','msgHostname'); return false;" />
<span id="msgHostname"></span>
</div>
EOT
}

select_root()
{
cat << EOT
<div class="box2">
<a name="root"></a>
<h5>$(gettext "Root")</h5>
$(gettext "Root passwd:")
<input type="password" id="rootPwd1" name="TGT_ROOT_PWD" value="$TGT_ROOT_PWD" placeholder="$(gettext "Password of root")" onkeyup="checkPwd('rootPwd1','rootPwd2','msgRootPwd'); return false;" />
$(gettext "Confirm password:")
<input type="password" id="rootPwd2" value="$TGT_ROOT_PWD" placeholder="$(gettext "Password of root")" onkeyup="checkPwd('rootPwd1','rootPwd2','msgRootPwd'); return false;" />
<span id="msgRootPwd"></span>
</div>
EOT
}

select_user()
{
cat << EOT
<div class="box2">
<a name="user"></a>
<h5>$(gettext "User")</h5>
$(gettext "User login:")
<input type="text" id="user" name="TGT_USER" value="$TGT_USER" placeholder="$(gettext "Name of the first user")" onkeyup="checkLogin('user','msgUser'); return false;" />
<span id="msgUser"></span>
<br /><br />
$(gettext "User passwd:")
<input type="password" id="userPwd1" name="TGT_USER_PWD" value="$TGT_USER_PWD" placeholder="$(gettext "Password of the first user")" onkeyup="checkPwd('userPwd1','userPwd2','msgUserPwd'); return false;" />
$(gettext "Confirm password:")
<input class="confirm" type="password" id="userPwd2" value="$TGT_USER_PWD" placeholder="$(gettext "Password of the first user")" onkeyup="checkPwd('userPwd1','userPwd2','msgUserPwd'); return false;" />
<span id="msgUserPwd"></span>
</div>
EOT
}

select_grub()
{
cat << EOT
<div>
<a name="grub"></a>
<h5>$(gettext "Grub")</h5>
<input type="checkbox" name="TGT_GRUB" value="yes" $([ "$TGT_GRUB" == "yes" ] && echo "checked") id="grub" />
<label for="grub">$(gettext "Install Grub bootloader. Usually you should answer yes, unless you want to install grub by hand yourself.")<br /></label>
<input type="checkbox" name="TGT_WINBOOT" value="auto" $([ -n "$TGT_WINBOOT" ] && echo "checked") id="dualboot" />
<label for="dualboot">$(gettext "Enable Windows Dual-Boot.")</label>
</div>
EOT
}

moveto_page()
{
	case $1 in
		partitioning)
			title1=$(gettext "Back to partitioning") ;;
		*)
			page=home
			title1=$(gettext "Back to Installer Start Page") ;;
	esac
	case $2 in
		write|run)
			title2=$(gettext "Proceed to SliTaz installation") ;;
		reboot)
			title2=$(gettext "Installation complete. You can now restart (reboot)") ;;
		failed)
			title2=$(gettext "Installation failed. See log") ;;
		*)
			page=home
			title2=$(gettext "Back to Installer Start Page") ;;
	esac
	cat <<EOT
<hr />
<input type="hidden" name="page" value="$2" />
<a class="button" value="$1"  href="$SCRIPT_NAME?page=$1" >$title1</a>
<input type="submit" value="$title2">
EOT
}

page_redirection()
{
	cat <<EOT
<html>
<head>
<title>$(gettext "A web page that points a browser to a different page after 2 seconds")</title>
<meta http-equiv="refresh" content="0; URL=$SCRIPT_NAME?page=$1">
<meta name="keywords" content="automatic redirection">
</head>
<body>
$(gettext "If your browser doesn't automatically redirect within a few seconds, 
you may want to go there manually")
<a href="$SCRIPT_NAME?page=$1">$1</a> 
</body>
</html>
EOT
}

check_ressources()
{
	local code 
	code=0
	# Check tazinst
	if ! tazinst usage | grep -q Usage: ; then
		cat <<EOT
<h3>$(gettext "Tazinst Error")</h3>
<p><strong>tazinst</strong>, $(gettext "the lightweight SliTaz HDD installer
is missing. Any installation can not be done without tazinst.")</p>
<p>$(gettext "Check tazinst' permissions, or reinstall the slitaz-tools package:")</p>
<code># tazpkg get-install slitaz-tools --forced</code>
EOT
		code=1
	else
		# Check tazinst required version
		v=$(tazinst version | tr -d '[:alpha:]')
		r=$TAZINST_REQUIRED_VERSION
		if ! (echo "$v" | awk -v r=$r '{v=$v+0}{ if (v < r) exit 1}') ; then
			cat <<EOT
<h3>$(gettext "Tazinst Error")</h3>
<p><strong>tazinst</strong> ($v) $(gettext "is not at the required version ($r),
use tazinst in a xterm or reinstall the slitaz-tools package:")</p>
<code># tazpkg get-install slitaz-tools --forced</code>
EOT
			code=1
		fi
	fi
	return $code
}

run_tazinst()
{
	echo "<h4>$(gettext "Proceeding: ()")</h4>"
	gettext "Please wait until processing is complete"
	table_start
	tazinst $(GET INST_ACTION) $INSTFILE | \
		awk '{print "<tr><td><tt>" $0 "</tt></td></tr>"}'
	table_end
	gettext "Completed."
	return $(grep -c "cancelled on error" $INSTFILE)
}

tazinst_log()
{
	echo "<pre>"
	tazinst log
	echo "</pre>"
}

scan_mkfs()
{
	for path in /bin /sbin /usr/bin /usr/sbin
	do
		[ -e $path/mkfs.btrfs ] && FS=btrfs
		[ -e $path/mkfs.cramfs ] && FS="$FS cramfs"
		[ -e $path/mkfs.ext2 ] && FS="$FS ext2"
		[ -e $path/mkfs.ext3 ] && FS="$FS ext3"
		[ -e $path/mkfs.ext4 ] && FS="$FS ext4"
		[ -e $path/mkfs.jfs ] && FS="$FS jfs"
		[ -e $path/mkfs.minix ] && FS="$FS minix"
		[ -e $path/mkfs.reiserfs ] && FS="$FS reiserfs"
		[ -e $path/mkfs.xfs ] && FS="$FS xfs"
	done
}

form_start()
{
	cat <<EOT
<script src="lib/user.js"></script>
<script type="text/javascript">
	function Validate(page) {
		if (page == "install") {
			// hostname
			if (false == checkLogin('hostname','msgHostname')) {
				alert("Hostname error");
				return false;
			// root pwd
			} else if (false == checkPwd('rootPwd1','rootPwd2','msgRootPwd')) {
				alert("Root password error");
				return false;
			// user
			} else if (false == checkLogin('user','msgUser')) {
				alert("User login error");
				return false;
			// user pwd
			} else if (false == checkPwd('userPwd1','userPwd2','msgUserPwd')) {
				alert("User password error");
				return false;
			} else {
				var r=confirm("$(gettext "Do you really want to continue?")");
				if (r==true)
				{
					document.ConfigForm.submit();
				} else {
					return false;
				}
			}
		} else if (page == "write") {
			return true;
		} else {
			var r=confirm("$(gettext "Do you really want to continue?")");
			if (r==true)
			{
				document.ConfigForm.submit();
			} else {
				return false;
			}
		}
	}
</script>
<form name="ConfigForm" method="get" onsubmit="return Validate('$1')" action="$SCRIPT_NAME">
EOT
}

form_end()
{
	echo "</form>"
}

#
# Main
#

case "$(GET page)" in
	home)
		xhtml_header
		select_action
		select_install
		select_upgrade
		;;
	partitioning)
		xhtml_header
		display_action install
		select_gparted
		;;
	gparted)
		su - -c "exec env DISPLAY=':0.0' XAUTHORITY='/var/run/slim.auth' /usr/sbin/gparted"
 		xhtml_header
		page_redirection partitioning
		;;
	install)
		xhtml_header
		form_start install
		display_action install
		read_setup
		select_source
		select_hdd
		select_partition
		select_options
		select_home
		select_hostname
		select_root
		select_user
		select_grub
		moveto_page partitioning write
		form_end
		;;
	upgrade)
		xhtml_header
		form_start upgrade
		display_action upgrade
		read_setup
		select_source
		select_hdd
		select_old_slitaz
		select_options
		select_grub
		moveto_page home write
		form_end
		;;
	write)
		write_setup
		xhtml_header
		if ! (tazinst check $INSTFILE); then
			page_redirection $(GET INST_ACTION)
		else
			read_setup
			form_start write
			display_action $(GET INST_ACTION)
			if run_tazinst; then
				moveto_page home reboot
			else
				moveto_page home failed
			fi
			form_end
		fi
		;;
	reboot)
		reboot ;;
	failed)
		xhtml_header
		display_log
		;;
	menu_install)
		xhtml_header
		if check_ressources; then
			page_redirection partitioning
		fi
		;;
	menu_upgrade)
		xhtml_header
		if check_ressources; then
			page_redirection upgrade
		fi
		;;
	*)
		xhtml_header
		if check_ressources; then
			page_redirection home
		fi
		;;
esac

xhtml_footer

exit 0
