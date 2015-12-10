#!/bin/sh
#
# test.cgi - Test TazPanel styles.
#
# Copyright (C) 2015 SliTaz GNU/Linux - BSD License
#

# Common functions from libtazpanel
. lib/libtazpanel
get_config
header

TITLE='Test'

xhtml_header 'Show icons and styles'

cat <<EOT

<section>
	<header><span data-img="@info@"></span>Buttons with font icons</header>
EOT

icons="@add@:add @admin@:admin @back@:back @battery@:battery @brightness@:brightness \
@cancel@:cancel @cd@:cd @check@:check @clock@:clock @conf@:conf @daemons@:daemons @delete@:delete \
@detect@:detect @diff@:diff @download@:download @edit@:edit @eth@:eth @group@:group @grub@:grub \
@hdd@:hdd @help@:help @history@:history @info@:info @install@:install @link@:link @list@:list \
@locale@:locale @lock@:lock @logs@:logs @loopback@:loopback @man@:man @modules@:modules @off@:off \
@ok@:ok @on@:on @opt@:opt @proc@:proc @refresh@:refresh @removable@:removable @remove@:remove \
@repack@:repack @report@:report @restart@:restart @run@:run @save@:save @scan@:scan \
@settings@:settings @slitaz@:slitaz @start@:start @stop@:stop @sync@:sync @tags@:tags @tag@:tag \
@tazx@:tazx @temperature@:temperature @terminal@:terminal @text@:text @unlink@:unlink \
@unlock@:unlock @upgrade@:upgrade @user@:user @view@:view @web@:web @wifi@:wifi @toggle@:toggle \
@chlock@:chlock @calendar@:calendar @modem@:modem @vpn@:vpn @display@:display @cpu@:cpu \
@floppy@:floppy @folder@:folder"

echo "$icons" | \
awk 'BEGIN{RS=" "; FS=":"} {
	printf "<button data-icon=\"%s\">%s</button>", $1, $2;
}'

cat <<EOT
</section>


<section>
	<header><span data-img="@link@"></span>Links with font icons</header>
	<div>
<p>
EOT

echo "$icons" | \
awk 'BEGIN{RS=" "; FS=":"} {
	printf "<a data-icon=\"%s\" href=\"#\">%s</a> ", $1, $2;
}'

cat <<EOT
</p>
	</div>
</section>


<section>
	<header><span data-img="@view@"></span>Links with font icons only (small buttons)</header>
	<p>
EOT

echo "$icons" | \
awk 'BEGIN{RS=" "; FS=":"} {
	printf "<a data-img=\"%s\" href=\"#\"></a>%s ", $1, $2;
}'

cat <<EOT
	</p>
</section>


<section>
	<header><span data-img="@sechi@"></span>Status icons</header>
	<div>
<span data-icon="@lvl0@">lvl0</span> <span data-icon="@lvl1@">lvl1</span> <span data-icon="@lvl2@">lvl2</span>
<span data-icon="@lvl3@">lvl3</span> <span data-icon="@lvl4@">lvl4, lvl5</span>
<span data-icon="@online@">online</span> <span data-icon="@offline@">offline</span>
<span data-icon="@sechi@">sechi</span> <span data-icon="@secmi@">secmi</span> <span data-icon="@seclo@">seclo</span>
<span data-icon="@pkg@">pkg</span> <span data-icon="@pkgi@">pkgi</span> <span data-icon="@pkgib@">pkgib</span>
	</div>
	<div>
<span data-icon="@msg@">msg</span> <span data-icon="@msgerr@">msgerr</span>
<span data-icon="@msgwarn@">msgwarn</span> <span data-icon="@msgup@">msgup</span>
<span data-icon="@msgtip@">msgtip</span>
	</div>
</section>


<section>
	<header><span data-img="&#xf20a;"></span>Font components</header>
	<div>
<span data-icon="&#xf200;">#f200</span> <span data-icon="&#xf201;">#f201</span>
<span data-icon="&#xf202;">#f202</span> <span data-icon="&#xf203;">#f203</span>
<span data-icon="&#xf204;">#f204</span> <span data-icon="&#xf205;">#f205</span>
<span data-icon="&#xf206;">#f206</span> <span data-icon="&#xf207;">#f207</span>
<span data-icon="&#xf208;">#f208</span> <span data-icon="&#xf209;">#f209</span>
<span data-icon="&#xf20a;">#f20a</span> <span data-icon="&#xf20b;">#f20b</span>
<span data-icon="&#xf20c;">#f20c</span> <span data-icon="&#xf20d;">#f20d</span>
	</div>
</section>


<section>
	<header>Message boxes</header>
	$(msg msg  "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
	$(msg tip  "Fusce volutpat est a euismod malesuada.")
	$(msg warn "Aenean elementum augue et nisl sollicitudin, ut pellentesque leo rutrum.")
	$(msg err  "Etiam nisi elit, fringilla sit amet consectetur quis, efficitur eu ligula.")
	$(msg up   "Sed pharetra ex ligula, nec commodo erat suscipit eu.")
</section>


<section>
	<header><span data-img="@check@"></span>User input elements</header>
	<div><form>
	<table>
		<tr><td>Text:</td>
			<td><input type="text" placeholder="Text"/></td>
		</tr>
		<tr><td>Password:</td>
			<td><input type="password" placeholder="Password"/></td>
		</tr>
		<tr><td>Button:</td>
			<td><input type="button" value="Button" data-icon="@ok@"/></td>
		</tr>
		<tr><td>Checkbox:</td>
			<td><input type="checkbox" id="chk"/><label for="chk">Check it</label></td>
		</tr>
		<tr><td>Radio:</td>
			<td>
				<label><input type="radio" name="rad" id="radio1"/>Option 1</label>
				<label><input type="radio" name="rad" id="radio2" checked/>Option 2</label>
				<label><input type="radio" name="rad" id="radio3"/>Option 3</label>
			</td>
		</tr>
		<tr><td>File:</td>
			<td><input type="file" accept=".txt,.png"/></td>
		</tr>
		<tr><td>Image:</td>
			<td><input type="image" src="/styles/default/images/msg-warn.png"/></td>
		</tr>
		<tr><td>Reset:</td><td><input type="reset"/></td></tr>
		<tr><td>Submit:</td><td><input type="submit"/></td></tr>
		<tr><td>Select:</td>
			<td><select><option data-icon="@user@">Option 1<option>Option 2<option>Option 3</select></td>
		</tr>
		<tr><td colspan="2"><b>HTML 5 inputs:</b></td></tr>
		<tr><td>Search:</td><td><input type="search" results="5" autosave="pkgsearch" autocomplete="on"/></td></tr>
		<tr><td>Number:</td><td><input type="number" name="n" value="3" min="0" max="10"/></td></tr>
		<tr><td>Range:</td><td><input type="range" name="r" value="3" min="0" max="10"/></td></tr>
		<tr><td>Color:</td><td><input type="color" name="c"/></td></tr>
		<tr><td>Tel:</td><td><input type="tel" name="t"/></td></tr>
		<tr><td>URL:</td><td><input type="url" name="u"/></td></tr>
		<tr><td>E-mail:</td><td><input type="email" name="e" data-x="A part number is a digit followed by three uppercase letters." required/></td></tr>
		<tr><td>Date:</td><td><input type="date" name="d" value="$(date +'%F')"/></td></tr>
		<tr><td>Month:</td><td><input type="month" name="m" value="$(date +'%Y-%m')"/></td></tr>
		<tr><td>Week:</td><td><input type="week" name="w" value="$(date +'%Y-W%V')"/></td></tr>
		<tr><td>Time:</td><td><input type="time" name="ti" value="$(date +'%R')"/></td></tr>
		<tr><td>Date &amp; Time:</td><td><input type="datetime" name="dt" value="$(date +'%FT%RZ')"/></td></tr>
		<tr><td>Date &amp; Time Local:</td><td><input type="datetime-local" name="dtl" value="$(date +'%FT%R')"/></td></tr>
	</table>
	</form></div>
</section>
EOT
xhtml_footer
exit 0
