cat << EOT
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="$(echo $LANG | cut -f1 -d_)">
<head>
	<title>$TITLE</title>
	<meta charset="utf-8" />
	<link rel="shortcut icon" href="/styles/default/favicon.ico" />
	<link rel="stylesheet" type="text/css" href="/styles/default/style.css" />
	<!-- Function to hide the loading message when page is generated. -->
	<script type="text/javascript">
		function showLoading(){
			document.getElementById("loading").style.display='none';
		}
	</script>
</head>
<body onload="showLoading()">

<div id="toolbar">
	<div id="icons">
		<a href="/help.cgi">
			<img src="/styles/default/images/help.png" alt="Help" /></a>
	</div>
	<ul id="menu">
		<li><a href="/">$(gettext 'Panel')</a>
			<ul>
				<li><a href="/index.cgi?terminal"><img
					src="/styles/default/images/terminal.png" />$(gettext 'Terminal')</a></li>
				<li><a href="/index.cgi?top"><img
					src="/styles/default/images/monitor.png" />$(gettext 'Processes')</a></li>
				<li><a href="/index.cgi?report"><img
					src="/styles/default/images/text.png" />$(gettext 'Create Report')</a></li>
			</ul>
		</li>
		<li><a href="/pkgs.cgi">$(gettext 'Packages')</a>
			<ul>
				<li><a href="/pkgs.cgi?list"><img
					src="/styles/default/images/tazpkg.png" />$(gettext 'My packages')</a></li>
				<li><a href="/pkgs.cgi?recharge"><img
					src="/styles/default/images/update.png" />$(gettext 'Recharge list')</a></li>
				<li><a href="/pkgs.cgi?up"><img
					src="/styles/default/images/update.png" />$(gettext 'Check updates')</a></li>
				<li><a href="/pkgs.cgi?admin"><img
					src="/styles/default/images/edit.png" />$(gettext 'Administration')</a></li>
			</ul>
		</li>
		<li><a href="/network.cgi">$(gettext 'Network')</a>
			<ul>
				<li><a href="/network.cgi?eth"><img
					src="/styles/default/images/ethernet.png" />$(gettext 'Ethernet')</a></li>
				<li><a href="/network.cgi?wifi"><img
					src="/styles/default/images/wireless.png" />$(gettext 'Wireless')</a></li>
				<li><a href="/index.cgi?file=/etc/network.conf"><img
					src="/styles/default/images/edit.png" />$(gettext 'Config file')</a></li>
			</ul>
		</li>
		<li><a href="/settings.cgi">$(gettext 'Settings')</a>
			<ul>
				<li><a href="/settings.cgi?users"><img
					src="/styles/default/images/users.png" />$(gettext 'Users')</a></li>
			</ul>
		</li>
		<li><a href="/boot.cgi">$(gettext 'Boot')</a>
			<ul>
				<li><a href="/boot.cgi?log"><img
					src="/styles/default/images/text.png" />$(gettext 'Boot logs')</a></li>
				<li><a href="/boot.cgi?daemons"><img
					src="/styles/default/images/recharge.png" />$(gettext 'Manage daemons')</a></li>
				<li><a href="/boot.cgi?grub"><img
					src="/styles/default/images/tux.png" />$(gettext 'Boot loader')</a></li>
			</ul>
		</li>
		<li><a href="/hardware.cgi">$(gettext 'Hardware')</a>
			<ul>
				<li><a href="/hardware.cgi?modules"><img
					src="/styles/default/images/tux.png" />$(gettext 'Kernel modules')</a></li>
				<li><a href="/hardware.cgi?detect"><img
					src="/styles/default/images/monitor.png" />$(gettext 'Detect PCI/USB')</a></li>
			</ul>
		</li>
		<li><a href="/live.cgi">$(gettext 'Live')</a>
			<ul>
				<li><a href="/live.cgi?liveusb">$(gettext 'Create a live USB key')</a></li>
				<li><a href="/live.cgi#liveiso">$(gettext 'Create a live CD-ROM')</a></li>
				<li><a href="/live.cgi#loram">$(gettext 'Convert ISO to loram')</a></li>
				<li><a href="/live.cgi#meta">$(gettext 'Build a meta ISO')</a></li>
			</ul>
		</li>
		<li><a href="/installer.cgi">$(gettext 'Install')</a>
			<ul>
				<li><a href="/installer.cgi?page=menu_install">$(gettext 'Install SliTaz')</a></li>
				<li><a href="/installer.cgi?page=menu_upgrade">$(gettext 'Upgrade system')</a></li>
			</ul>
		</li>
	</ul>
</div>

<div id="header">
	<h1>$TITLE</h1>
</div>

<!-- Page content -->
<div id="content">
EOT
