#!/bin/sh
#
# Locale settings CGI interface.
#
# Copyright (C) 2015 SliTaz GNU/Linux - BSD License
#


# Common functions from libtazpanel

. ./lib/libtazpanel
get_config
header

TITLE=$(_ 'Locale')



#############################
# Get info from locale file #
#############################

get_locale_info()
{
	# Commands like `LC_ALL=fr_FR locale -k LC_MEASUREMENT` will do the job
	# only when your locale is generated and exists in the /usr/lib/locale.
	# Here we manually parse locale definition files from /usr/share/i18n/locales/.
	# Strange, bloated and not script-friendly format :(

	[ ! -e /usr/share/i18n/locales/$1 ] && return

	# Prepare file
	if [ ! -e /tmp/tazpanel-$1 ]; then
		sed 's|^[ \t]*||;/^%/d;/^comment_char/d;/^escape_char/d' /usr/share/i18n/locales/$1 | tr '\n' '&' | sed 's|/&||g' | tr '&' '\n' | sed 's|<U\([0-9a-fA-F]*\)>|\&#x\1;|g' | sed 's|&#x00|\&#x|g' > /tmp/tazpanel-$1
	fi

	local ANS=$(grep -e "^$2[ 	]" /tmp/tazpanel-$1 | sed 's|^[^ \t][^ \t]* *||')
	if [ -z "$ANS" ]; then
		# Not found, then section is copied from other locale definition file...
		case $2 in
			measurement)
				section='LC_MEASUREMENT';;
			width|height)
				section='LC_PAPER';;
			currency_symbol|int_curr_symbol)
				section='LC_MONETARY';;
			day|abday|mon|abmon|d_t_fmt|d_fmt|t_fmt|am_pm|t_fmt_ampm|date_fmt)
				section='LC_TIME';;
		esac
		# Recursive call
		get_locale_info $(sed -n '/^'$section'/,/^END '$section'/p' /tmp/tazpanel-$1 | grep 'copy' | cut -d'"' -f2) $2
	else
		case $2 in
			day|abday|mon|abmon|am_pm)		# semicolon-separated list in double quotes
				echo "$ANS";;
			*)		# single value in double qoutes
				echo "$ANS" | cut -d'"' -f2;;
		esac
	fi
}


# Get info from locale file about measurement system

get_locale_info_measurement()
{
	# faster to use pre-processed values
	case $1 in
		en_AG|en_US|es_PR|es_US|nl_AW|yi_US) _ 'US' ;;
		POSIX) ;;
		*) _ 'metric' ;;
	esac
}


# Get info from locale file about paper size

get_locale_info_paper()
{
	# faster to use pre-processed values
	case $1 in
		en_AG|en_US|es_PR|es_US|nl_AW|yi_US) echo '8½×11 (US Letter)';;
		en_CA|en_PH|es_CL|es_CO|es_CR|es_GT|es_MX|es_NI|es_PA|es_SV|es_VE|fil_PH|fr_CA|ik_CA|iu_CA|shs_CA|tl_PH) echo '216×279 (US Letter)';;
		POSIX) ;;
		*) echo '210×297 (A4)';;
	esac
}


# Get info from locale file about date and time format

get_locale_info_date_time()
{
	case $2 in
		c) get_locale_info $1 d_t_fmt ;;
		x) get_locale_info $1 d_fmt ;;
		X) get_locale_info $1 t_fmt ;;
		r) get_locale_info $1 t_fmt_ampm ;;
		*) get_locale_info $1 date_fmt ;;
	esac | sed 's|&#x20;| |g; s|&#x25;|%|g; s|&#x2C;|,|g; s|&#x2D;|-|g; s|&#x2E;|.|g; s|&#x2F;|/|g; s|&#x3A;|:|g; s|&#x41;|A|g; s|&#x42;|B|g; s|&#x43;|C|g; s|&#x46;|F|g; s|&#x48;|H|g; s|&#x49;|I|g; s|&#x4D;|M|g; s|&#x4F;|O|g; s|&#x52;|R|g; s|&#x53;|S|g; s|&#x54;|T|g; s|&#x58;|X|g; s|&#x59;|Y|g; s|&#x5A;|Z|g; s|&#x61;|a|g; s|&#x62;|b|g; s|&#x65;|e|g; s|&#x64;|d|g; s|&#x6B;|k|g; s|&#x6D;|m|g; s|&#x6E;|n|g; s|&#x6F;|o|g; s|&#x70;|p|g; s|&#x72;|r|g; s|&#x74;|t|g; s|&#x78;|x|g; s|&#x79;|y|g; s|&#x7A;|z|g;'

}


parse_date()
{
	local weekday month day abday mon abmon rtime d_fmt t_fmt am_pm
	weekday=$(( $(date +%w) + 1 ))											# 1=Sunday ...
	  month=$(date +%-m)													# 1=January ...
	  day=$(get_locale_info $1   day | cut -d'"' -f$(( 2 * $weekday )) | sed 's|&|\\\&|g')	# translated day of week
	abday=$(get_locale_info $1 abday | cut -d'"' -f$(( 2 * $weekday )) | sed 's|&|\\\&|g')	#   same, abbreviated
	  mon=$(get_locale_info $1   mon | cut -d'"' -f$(( 2 * $month   )) | sed 's|&|\\\&|g')	# translated month
	abmon=$(get_locale_info $1 abmon | cut -d'"' -f$(( 2 * $month   )) | sed 's|&|\\\&|g')	#   same, abbreviated
	# next %-codes expanded into other %-codes
	rtime=$(get_locale_info_date_time $1 r | sed 's|&|\\\&|g')									# %r: 12-hour time
	d_fmt=$(get_locale_info_date_time $1 x | sed 's|&|\\\&|g')									# %x: date
	t_fmt=$(get_locale_info_date_time $1 X | sed 's|&|\\\&|g')									# %X: time

	case $(LC_ALL=POSIX date +%P) in										# translated am/pm
		am) am_pm=$(get_locale_info $1 am_pm | cut -d'"' -f2 | sed 's|&|\\\&|g');;
		pm) am_pm=$(get_locale_info $1 am_pm | cut -d'"' -f4 | sed 's|&|\\\&|g');;
	esac

	# r x X | OC | Y y Oy Ey | m -m Om | d -d Od | e -e Oe | F | H OH k | I OI l | M OM | S OS | R T | Z z | t | P p Op A a B b
	# Note: %P=am/pm; %p=AM/PM. But here they the same because it is not a simple job to convert letters.
	echo "$2" | sed "s|%r|$rtime|; s|%x|$d_fmt|; s|%X|$t_fmt|; \
		s|%OC|S(date +%OC)|; \
		s|%Y|$(date +%Y)|; s|%y|$(date  +%y )|; s|%Oy|$(date +%Oy)|; s|%Ey|$(date +%Ey)|; \
		s|%m|$(date +%m)|; s|%-m|$(date +%-m)|; s|%Om|$(date +%Om)|; \
		s|%d|$(date +%d)|; s|%-d|$(date +%-d)|; s|%Od|$(date +%Od)|; \
		s|%e|$(date +%e)|; s|%-e|$(date +%-e)|; s|%Oe|$(date +%Oe)|; \
		s|%F|$(date +%F)|; \
		s|%H|$(date +%H)|; s|%OH|$(date +%OH)|; s|%k|$(date +%k)|; \
		s|%I|$(date +%I)|; s|%OI|$(date +%OI)|; s|%l|$(date +%l)|; \
		s|%M|$(date +%M)|; s|%OM|$(date +%OM)|; \
		s|%S|$(date +%S)|; s|%OS|$(date +%OS)|; \
		s|%R|$(date +%R)|; s|%T|$(date  +%T )|; \
		s|%Z|$(date +%Z)|; s|%z|$(date  +%z )|; \
		s|%t|\t|; \
		s|%P|$am_pm|; s|%p|$am_pm|; s|%Op|$am_pm|; s|%A|$day|; s|%a|$abday|; s|%B|$mon|; s|%b|$abmon|;"

}

list_of()
{
	cd /usr/share/i18n/locales
	#mon=$(date +%-m); monn=$(( $mon * 2 ))
	#echo "mon=\"$mon\" monn=\"$monn\""

	cat <<EOT
<table class="wide zebra filelist">
	<thead>
		<tr><td>Locale</td>
			<td>Date format</td>
			<td>Native date</td>
			<td>Measurement</td>
			<td>Paper size</td>
		</tr>
	</thead>
EOT

for LOC in en_US fr_CA be_BY ca_IT el_CY fr_CH ru_RU ru_UA; do
	case $LOC in
		iso*|translit*) ;;
		*)
			#echo -e "$LOC:\t$(parse_date $LOC $(get_locale_info_date_time $LOC c | sed 's|&|\\\&|g'))";;
			FMT="$(get_locale_info_date_time $LOC x)"
			echo "<tr><td>$LOC</td><td>$FMT</td><td>"
			parse_date $LOC "$FMT"
			echo "</td><td>"
			get_locale_info_measurement $LOC
			echo "</td><td>"
			get_locale_info_paper $LOC
			echo "</td></tr>"
			;;
	esac
done
	echo '</table>'
}





#
# Default xHTML content
#

xhtml_header
check_root_tazpanel

cat <<EOT
<h2>Under construction!</h2>

<section>
	<header>Current date and some i18n values in the different locales:</header>
	$(list_of)
</section>
EOT

xhtml_footer
exit 0
