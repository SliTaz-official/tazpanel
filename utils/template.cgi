#!/bin/sh
#
# CGI template interface for TazPanel.
#

# Common functions from libtazpanel
. lib/libtazpanel
header
get_config

#
# Commands
#

case " $(GET) " in
	*\ cmd\ *)
		echo "" ;;
	*)
		#
		# Default xHTML content
		#
		xhtml_header
		cat << EOT
<div id="wrapper">
	<h2>$(gettext "Page title - Template")</h2>
	<p>$(gettext "Page information")<p>
</div>

<h3>$(gettext "h3 title")</h3>

<pre>
Preformated output
</pre>
EOT
		;;
esac

xhtml_footer
exit 0
