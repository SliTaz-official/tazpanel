#!/bin/sh
#
# CGI/Shell script example for TazPanel
#
echo "Content-Type: text/html"
echo ""

. tazpanel.conf

xhtml_header() {
	# xHTML 5 header
	cat $HEADER | sed s/'- %TITLE%'/"$TITLE"/
}

[ $DEBUG == "1" ] && echo "<p class='debug'>DEBUG on</p>"

#
# Commands
#

case "$QUERY_STRING" in
	users)
		TITLE="- Users"
		xhtml_header
		echo '<ul>'
		fgrep /home /etc/passwd | while read line
		do
			echo '<li>'
			echo "	<img src='$IMAGES/user.png' />$line"
			echo '</li>'
		done
		echo '</ul>' ;;
	network)
		TITLE="- Network"
		xhtml_header
		echo '<pre>'
		ifconfig
		echo '</pre>' ;;
	hardware)
		TITLE="- Hardware"
		xhtml_header
		echo '<pre>'
		lspci
		echo '</pre>' ;;
	*)
		# Default xHTML content
		xhtml_header
		cat << EOT
<p>
	Uptime: `uptime`
</p>
EOT
		;;
esac

# xHTML 5 footer
cat $FOOTER
