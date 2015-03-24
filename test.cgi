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

TITLE='TazPanel - Test'

xhtml_header

cat <<EOT

<section>
	<header data-icon="info">Buttons with font icons</header>
<!--
--><button data-icon="add"        >Add        </button><button data-icon="admin"   >Admin   </button><!--
--><button data-icon="back"       >Back       </button><button data-icon="battery" >Battery </button><!--
--><button data-icon="brightness" >Brightness </button><button data-icon="cancel"  >Cancel  </button><!--
--><button data-icon="cd"         >CD         </button><button data-icon="check"   >Check   </button><!--
--><button data-icon="clock"      >Clock      </button><button data-icon="conf"    >Conf    </button><!--
--><button data-icon="daemons"    >Daemons    </button><button data-icon="delete"  >Delete  </button><!--
--><button data-icon="detect"     >Detect     </button><button data-icon="diff"    >Diff    </button><!--
--><button data-icon="download"   >Download   </button><button data-icon="edit"    >Edit    </button><!--
--><button data-icon="eth"        >Eth        </button><button data-icon="group"   >Group   </button><!--
--><button data-icon="grub"       >GRUB       </button><button data-icon="hdd"     >HDD     </button><!--
--><button data-icon="help"       >Help       </button><button data-icon="history" >History </button><!--
--><button data-icon="info"       >Info       </button><button data-icon="install" >Install </button><!--
--><button data-icon="link"       >Link       </button><button data-icon="list"    >List    </button><!--
--><button data-icon="locale"     >Locale     </button><button data-icon="lock"    >Lock    </button><!--
--><button data-icon="logs"       >Logs       </button><button data-icon="loopback">Loopback</button><!--
--><button data-icon="man"        >Man        </button><button data-icon="modules" >Modules </button><!--
--><button data-icon="off"        >Off        </button><button data-icon="ok"      >OK      </button><!--
--><button data-icon="on"         >On         </button><button data-icon="opt"     >Opt     </button><!--
--><button data-icon="proc"       >Proc       </button><button data-icon="refresh" >Refresh </button><!--
--><button data-icon="removable"  >Removable  </button><button data-icon="remove"  >Remove  </button><!--
--><button data-icon="repack"     >Repack     </button><button data-icon="report"  >Report  </button><!--
--><button data-icon="restart"    >Restart    </button><button data-icon="run"     >Run     </button><!--
--><button data-icon="save"       >Save       </button><button data-icon="scan"    >Scan    </button><!--
--><button data-icon="settings"   >Settings   </button><button data-icon="slitaz"  >SliTaz  </button><!--
--><button data-icon="start"      >Start      </button><button data-icon="stop"    >Stop    </button><!--
--><button data-icon="sync"       >Sync       </button><button data-icon="tags"    >Tags    </button><!--
--><button data-icon="tag"        >Tag        </button><button data-icon="tazx"    >TazX    </button><!--
--><button data-icon="temperature">Temperature</button><button data-icon="terminal">Terminal</button><!--
--><button data-icon="text"       >Text       </button><button data-icon="unlink"  >Unlink  </button><!--
--><button data-icon="unlock"     >Unlock     </button><button data-icon="upgrade" >Upgrade </button><!--
--><button data-icon="user"       >User       </button><button data-icon="view"    >View    </button><!--
--><button data-icon="web"        >Web        </button><button data-icon="wifi"    >Wi-Fi   </button><!--
-->
</section>


<section>
	<header data-icon="link">Links with font icons</header>
	<div>
<p>
<a data-icon="add"        >Add        </a> <a data-icon="admin"     >Admin     </a> <a data-icon="back"     >Back     </a>
<a data-icon="battery"    >Battery    </a> <a data-icon="brightness">Brightness</a> <a data-icon="cancel"   >Cancel   </a>
<a data-icon="cd"         >CD         </a> <a data-icon="check"     >Check     </a> <a data-icon="clock"    >Clock    </a>
<a data-icon="conf"       >Conf       </a> <a data-icon="daemons"   >Daemons   </a> <a data-icon="delete"   >Delete   </a>
<a data-icon="detect"     >Detect     </a> <a data-icon="diff"      >Diff      </a> <a data-icon="download" >Download </a>
<a data-icon="edit"       >Edit       </a> <a data-icon="eth"       >Eth       </a> <a data-icon="group"    >Group    </a>
<a data-icon="grub"       >GRUB       </a> <a data-icon="hdd"       >HDD       </a> <a data-icon="help"     >Help     </a>
<a data-icon="history"    >History    </a> <a data-icon="info"      >Info      </a> <a data-icon="install"  >Install  </a>
<a data-icon="link"       >Link       </a> <a data-icon="list"      >List      </a> <a data-icon="locale"   >Locale   </a>
<a data-icon="lock"       >Lock       </a> <a data-icon="logs"      >Logs      </a> <a data-icon="loopback" >Loopback </a>
<a data-icon="man"        >Man        </a> <a data-icon="modules"   >Modules   </a> <a data-icon="off"      >Off      </a>
<a data-icon="ok"         >OK         </a> <a data-icon="on"        >On        </a> <a data-icon="opt"      >Opt      </a>
<a data-icon="proc"       >Proc       </a> <a data-icon="refresh"   >Refresh   </a> <a data-icon="removable">Removable</a>
<a data-icon="remove"     >Remove     </a> <a data-icon="repack"    >Repack    </a> <a data-icon="report"   >Report   </a>
<a data-icon="restart"    >Restart    </a> <a data-icon="run"       >Run       </a> <a data-icon="save"     >Save     </a>
<a data-icon="scan"       >Scan       </a> <a data-icon="settings"  >Settings  </a> <a data-icon="slitaz"   >SliTaz   </a>
<a data-icon="start"      >Start      </a> <a data-icon="stop"      >Stop      </a> <a data-icon="sync"     >Sync     </a>
<a data-icon="tags"       >Tags       </a> <a data-icon="tag"       >Tag       </a> <a data-icon="tazx"     >TazX     </a>
<a data-icon="temperature">Temperature</a> <a data-icon="terminal"  >Terminal  </a> <a data-icon="text"     >Text     </a>
<a data-icon="unlink"     >Unlink     </a> <a data-icon="unlock"    >Unlock    </a> <a data-icon="upgrade"  >Upgrade  </a>
<a data-icon="user"       >User       </a> <a data-icon="view"      >View      </a> <a data-icon="web"      >Web      </a>
<a data-icon="wifi"       >Wi-Fi      </a>
</p>
	</div>
</section>


<section>
	<header data-icon="view">Links with font icons only (small buttons)</header>
	<p>
<a data-img="conf"   href="#"></a>Conf   <a data-img="help" href="#"></a>Help <a data-img="man"  href="#"></a>Man
<a data-img="off"    href="#"></a>Off    <a data-img="on"   href="#"></a>On   <a data-img="opt"  href="#"></a>Opt
<a data-img="remove" href="#"></a>Remove <a data-img="run"  href="#"></a>Run  <a data-img="stop" href="#"></a>Stop
<a data-img="web"    href="#"></a>Web
</p>
</section>

<section>
	<header data-icon="check">User input elements</header>
	<div><form>
	<table>
		<tr><td>Text:</td>
			<td><input type="text" placeholder="Text"/></td>
		</tr>
		<tr><td>Password:</td>
			<td><input type="password" placeholder="Password"/></td>
		</tr>
		<tr><td>Button:</td>
			<td><input type="button" value="Button" data-icon="ok"/></td>
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
			<td><select><option data-icon="user">Option 1<option>Option 2<option>Option 3</select></td>
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
