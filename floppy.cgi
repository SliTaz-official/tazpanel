#!/bin/sh
#
# Floppy set CGI interface
#
# Copyright (C) 2015 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
TITLE=$(_ 'Boot')


case "$1" in
	menu)
		TEXTDOMAIN_original=$TEXTDOMAIN
		export TEXTDOMAIN='floppy'

		#which bootloader > /dev/null &&
		cat <<EOT
<li><a data-icon="@floppy@" href="floppy.cgi">$(_ 'Boot floppy')</a></li>
EOT
		export TEXTDOMAIN=$TEXTDOMAIN_original
		exit
esac


#
# Commands
#

error=
case " $(POST) " in
*\ doformat\ *)
	fdformat $(POST fd)
	which mkfs.$(POST fstype) > /dev/null 2>&1 &&
	mkfs.$(POST fstype) $(POST fd)
	;;
*\ write\ *)
	if [ "$(FILE fromimage tmpname)" ]; then
		dd if=$(FILE fromimage tmpname) of=$(POST tofd)
		rm -f $(FILE fromimage tmpname)
	else
		error="$(msg err 'Broken FILE support')"
	fi ;;
*\ read\ *)
	dd if=$(POST fromfd) of=$(POST toimage)
	;;
*\ build\ *)
	cmd=""
	toremove=""
	while read key file ; do
		[ "$(FILE $file size)" ] || continue
		for i in $(seq 1 $(FILE $file count)); do
			cmd="$cmd $key $(FILE $file tmpname $i)"
			toremove="$toremove $(FILE $file tmpname $i)"
		done
	done <<EOT
bootloader	kernel
--initrd	initrd
--initrd	initrd2
--info		info
EOT
	error="$(msg err 'Broken FILE support !')
		<pre>$(httpinfo)</pre>"
	if [ "$cmd" ]; then
		for key in cmdline rdev video format mem ; do
			[ "$(POST $key)" ] || continue
			cmd="$cmd --$key '$(POST $key)'"
		done 
		[ "$(POST edit)" ] || cmd="$cmd --dont-edit-cmdline"
		TITLE="$(_ 'TazPanel - floppy')"
		header
		xhtml_header
		cd $(POST workdir)
		echo "<pre>"
		eval $cmd 2>&1
		echo "</pre>"
		[ "$toremove" ] && rm -f $toremove && rmdir $(dirname $toremove)
		xhtml_footer
		exit 0
	fi
	;;
esac

listfd()
{
	echo "<select name=\"$1\">"
	ls /dev/fd[0-9]* | sed 's|.*|<option>&</option>|'
	echo "</select>"
}

header
xhtml_header "$(_ 'Floppy disk utilities')"
echo "$error"

cat <<EOT
<form method="post" enctype="multipart/form-data" class="wide">
EOT

[ -w /dev/fd0 ] && cat <<EOT
<section>
	<header>
		$(_ 'Floppy disk format')
	</header>
	<div>
		<button type="submit" name="doformat" data-icon="@start@" >$(_ 'Format disk')</button>
		$(listfd fd) filesystem:
		<select name "fstype">
			<option>$(_ 'none')</option>
			$(ls /sbin/mkfs.* | sed '/dev/d;s|.*/mkfs.\(.*\)|<option>\1</option>|')
		</select>
	</div>
</section>

<section>
	<header>
		$(_ 'Floppy disk transfer')
	</header>
	<table>
		<tr>
			<td>
				<button type="submit" name="write" data-icon="@start@" >$(_ 'Write image')</button>
				$(listfd tofd) &lt;&lt;&lt; <input name="fromimage" type="file">
			</td>
		</tr>
		<tr>
			<td>
				<button type="submit" name="read" data-icon="@start@" >$(_ 'Read image'  )</button>
				$(listfd fromfd) &gt;&gt;&gt; <input name="toimage" type="text" value="/tmp/floppy.img">
			<td>
		</tr>
	</table>
</section>
EOT


case "$HOME" in
	/home/*) OUTPUTDIR=$HOME ;;
	*)       OUTPUTDIR=/tmp ;;
esac

cat <<EOT
<section>
	<header>
		$(_ 'Boot floppy set builder')
	</header>

	<table>
		<tr>
			<td>$(_ 'Linux kernel:')</td>
			<td><input name="kernel" size="37" type="file"> <i>$(_ 'required')</i></td>
		</tr>
		<tr>
			<td>$(_ 'Initramfs / Initrd:')</td>
			<td><input name="initrd[]" size="37" type="file" multiple> <i>$(_ 'optional')</i></td>
		</tr>
		<tr>
			<td>$(_ 'Extra initramfs:')</td>
			<td><input name="initrd2[]" size="37" type="file" multiple> <i>$(_ 'optional')</i></td>
		</tr>
		<tr>
			<td>$(_ 'Boot message:')</td>
			<td><input name="info" size="37" type="file"> <i>$(_ 'optional')</i></td>
		</tr>
		<tr>
			<td>$(_ 'Default cmdline:')</td>
			<td id="cmdline"><input name="cmdline" size="36" type="text" value="$(sed 's/^BOOT_IMAGE[^ ]* //;s/initrd=[^ ]* //' /proc/cmdline)" > <input name="edit" checked="checked" type="checkbox">$(_ 'edit')
				<i>$(_ 'optional')</i></td>
		</tr>
		<tr>
			<td>$(_ 'Root device:')</td>
			<td><input name="rdev" size="8" value="/dev/ram0" type="text">
				&nbsp;&nbsp;$(_ 'Flags:')
				<select name="flags">
					<option selected="selected" value="1">R/O</option>
					<option value="0">R/W</option>
				</select>
				&nbsp;&nbsp;VESA:
				<select name="video">
					<option value="-3">Ask</option>
					<option value="-2">Extended</option>
					<option value="-1" selected="selected">Standard</option>
EOT

echo "0:0 1:1 2:2 3:3 4:4 5:5 6:6 7:7 8:8 9:9 10:10 11:11 12:12 13:13 14:14 15:15 \
3840:80x25 3843:80x28 3845:80x30 3846:80x34 3842:80x43 3841:80x50 3847:80x60 777:132x25 778:132x43 \
824:320x200x8    781:320x200x15   782:320x200x16   783:320x200x24   800:320x200x32   \
                 915:320x240x15   821:320x240x16   917:320x240x24   918:320x240x32   \
                 931:400x300x15   822:400x300x16   933:400x300x24   934:400x300x32   \
820:512x384x8    947:512x384x15   823:512x384x16   949:512x384x24   950:512x384x32   \
962:640x350x8    963:640x350x15   964:640x350x16   965:640x350x24   966:640x350x32   \
768:640x400x8    899:640x400x15   825:640x400x16   901:640x400x24   902:640x400x32   \
769:640x480x8    784:640x480x15   785:640x480x16   786:640x480x24   826:640x480x32   \
879:800x500x8    880:800x500x15   881:800x500x16   882:800x500x24   883:800x500x32   \
771:800x600x8    787:800x600x15   788:800x600x16   789:800x600x24   827:800x600x32   \
815:896x672x8                                      818:896x672x24   819:896x672x32   \
874:1024x640x8   875:1024x640x15  876:1024x640x16  877:1024x640x24  878:1024x640x32  \
773:1024x768x8   790:1024x768x15  791:1024x768x16  792:1024x768x24  828:1024x768x32  \
869:1152x720x8   870:1152x720x15  871:1152x720x16  872:1152x720x24  873:1152x720x32  \
775:1280x1024x8  793:1280x1024x15 794:1280x1024x16 795:1280x1024x24 829:1280x1024x32 \
835:1400x1050x8                   837:1400x1050x16 838:1400x1040x24                  \
                 864:1440x900x15  866:1440x900x16  867:1440x900x24  868:1440x900x32  \
816:1600x1200x8                   817:1600x1200x16                                   \
893:1920x1200x8" | sed 's|  *| |g' |\
awk 'BEGIN{RS=" "; FS=":"} {
	printf "<option value=\"%s\">%s</option>\n", $1, $2;
}'
cat <<EOT
				</select>
			</td>
		</tr>
		<tr>
			<td>$(_ 'Output directory:')</td>
			<td id="workdir"><input name="workdir" size="36" type="text" value="$OUTPUTDIR"></td>
		</tr>
		<tr>
			<td>$(_ 'Floppy size:')</td>
			<td><select name="format">
					<optgroup label="5&frac14; SD">
						<option value="360">360 KB</option>
					</optgroup>
					<optgroup label="3&frac12; SD">
						<option value="720">720 KB</option>
					</optgroup>
					<optgroup label="5&frac14; HD">
						<option value="1200">1.20 MB</option>
					</optgroup>
					<optgroup label="3&frac12; HD">
						<option value="1440" selected="selected">1.44 MB</option>
						<option value="1600">1.60 MB</option>
						<option value="1680">1.68 MB</option>
						<option value="1722">1.72 MB</option>
						<option value="1743">1.74 MB</option>
						<option value="1760">1.76 MB</option>
						<option value="1840">1.84 MB</option>
						<option value="1920">1.92 MB</option>
						<option value="1968">1.96 MB</option>
					</optgroup>
					<optgroup label="3&frac12; ED">
						<option value="2880">2.88 MB</option>
						<option value="3360">3.36 MB</option>
						<option value="3444">3.44 MB</option>
						<option value="3840">3.84 MB</option>
						<option value="3936">3.92 MB</option>
					</optgroup>
					<option value="0">$(_ 'no limit')</option>
				</select>&nbsp;
				$(_ 'RAM used')&nbsp;<select name="mem">
					<option selected="selected" value="16">16 MB</option>
					<option value="15">15 MB</option>
					<option value="14">14 MB</option>
					<option value="13">13 MB</option>
					<option value="12">12 MB</option>
					<option value="11">11 MB</option>
					<option value="10">10 MB</option>
					<option value="9">9 MB</option>
					<option value="8">8 MB</option>
					<option value="7">7 MB</option>
					<option value="6">6 MB</option>
					<option value="5">5 MB</option>
					<option value="4">4 MB</option>
				</select>&nbsp;
				<button type="submit" name="build" data-icon="@start@" >$(_ 'Build floppy set'  )</button>
			</td>
		</tr>
	</table>
	<footer>
		<p>
			$(_ 'Note') 1: $(_ 'the extra initramfs may be useful to add your own configuration files.')
		</p>
		<p>
			$(_ 'Note') 2: $(_ 'the keyboard is read for ESC or ENTER on every form feed (ASCII 12) in the boot message.')
		</p>
	</footer>
</section>
</form>
EOT

xhtml_footer
exit 0
