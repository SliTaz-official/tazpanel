#!/bin/sh
#
# CGI/Shell script example for TazPanel
#
echo "Content-Type: text/html"
echo ""

. tazpanel.conf

# xHTML 5 header
cat $HEADER | sed s'/- %TITLE%//'

[ $DEBUG == "1" ] && echo "<p class='debug'>DEBUG on</p>"

#
# Commands
#

case "$QUERY_STRING" in
	sysinfo)
		echo "TODO" ;;
	users)
		echo '<ul>'
		fgrep /home /etc/passwd | while read line
		do
			echo '<li>'
			echo "	<img src='$IMAGES/user.png' />$line"
			echo '</li>'
		done
		echo '</ul>' ;;
	network)
		echo '<pre>'
		ifconfig
		echo '</pre>' ;;
	hardware)
		echo '<pre>'
		lspci
		echo '</pre>' ;;
	*)
		# Default xHTML content
		cat << EOT
<p>
	Uptime: `uptime`
</p>
EOT
		;;
esac

# xHTML 5 footer
cat $FOOTER
