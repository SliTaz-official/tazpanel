
// Hide Loading panel
function hideLoading() {
	var loading = document.getElementById("loading");
	// If element presents on page
	if (loading) loading.style.display='none';
}
// Attach event handler
window.onload = hideLoading;



// Confirm page loading break
function confirmExit() {
	return "$(_ 'Confirm break')";
}
// Attach event handler
window.onbeforeunload = confirmExit;



// Set light or dark color theme
function setColorTheme() {
	// Goal: to produce pages that fit the user's defined look and feel, and
	//   may be more accessible as the current user settings (contrast color
	//   schemes, big font sizes, etc.)
	// Realization in the CSS2:
	//   http://www.w3.org/TR/REC-CSS2/ui.html#system-colors
	// We can use colors from user's color theme to mimic plain desktop application.
	//
	// Alas, nowadays it not works. Webkit-based browser returns hard-coded values,
	//   with exception of these two:
	//   * ButtonText  - text on push buttons.
	//   * CaptionText - text in caption, size box, and scrollbar arrow box.
	//
	// When user changes color theme, browser re-draws page, so all input elements
	//   (buttons, checkboxes, radiobuttons, drop-down lists, scrollbars, text inputs)
	//   automagically fits user-defined theme. We need to change web document's
	//   colors manually. We can't ask for exact user defined colors for document's
	//   background in any way, we can only imagine if it dark or light.
	//   So, plan is follows:
	// We use 'ButtonText' color for base document's color,  and calculate if it
	//   dark or light. If color of button's text is dark, then color of button's body
	//   is light, and we define entire web document as light; and vice versa.

	// Get 'ButtonText' color value (as current text's color of body)
	var body = document.getElementsByTagName('body')[0];
	var bodyColor = window.getComputedStyle(body, null).color;
	console.info("Set bodyColor: %s", bodyColor);

	// Returned value must be in format like "rgb(212, 212, 212)" or "rgba(192, 68, 1, 0)"
	if (bodyColor.indexOf("rgb") != -1) {
		// Make array with color components
		var results = bodyColor.match(/^rgba?\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})/);

		// Calculate luminance (brightness) in range 0..1
		if (results && results.length >= 3) {
			r = parseInt(results[1], 10);
			g = parseInt(results[2], 10);
			b = parseInt(results[3], 10);
			min = Math.min(r, g, b); max = Math.max(r, g, b);
		}
		var luminance = (min + max) / 2 / 255;

		// Set class for body
		body.className = (luminance > 0.5) ? 'dark' : 'light';
	}
	// Now we can use cascade styles for any elements lying on light or dark body:
	//   .light h2 { color: #222; }
	//   .dark  h2 { color: #CCC; }
	// Also we can use semi-transparent colors in some cases:
	//   body footer { color: rgba(128, 128, 128, 0.5); }
}



// Set base font size
function setBaseFont() {
	// Goal: to have on page the same font sizes as in user's system.
	// User input elements changed its font size automatically, so we can read
	//   font size from (hidden) button and apply this size to document's body.
	//   All other sizes will be relative, and will grow or shrink automatically.

	// Get document's body
	var body = document.getElementsByTagName('body')[0];

	// Make button in the hidden DOM
	var hiddenButton = document.createElement('BUTTON');

	// Move button away from look
	hiddenButton.style.setProperty('position', 'absolute', 1);
	hiddenButton.style.setProperty('left', '0', 1);

	// Add some text to button
	hiddenButton.appendChild(document.createTextNode("SliTaz"));

	// Add button to DOM
	body.appendChild(hiddenButton);

	// Focus to button (it will get colored outline!)
	hiddenButton.focus();

	// Get button's style
	var buttonStyle = getComputedStyle(hiddenButton, null);

	// Copy styles from button to body
	with (body.style) {
		fontFamily = buttonStyle.fontFamily;
		fontSize   = buttonStyle.fontSize;
		fontWeight = 'normal';
	}

	//body.style.color      = buttonStyle.outlineColor;

	console.info('Set fontFamily: %s, fontSize: %s', body.style.fontFamily, body.style.fontSize);
	console.info('Theme color: %s', buttonStyle.outlineColor);
	// Remove button from hidden DOM
	body.removeChild(hiddenButton);
}



//
function dupTableHead() {
	if (! document.getElementById('head2')) return
	var tableHead = document.createElement("TABLE");
	with (tableHead) {
		innerHTML = '<thead>' + document.getElementById('head2').innerHTML + '</thead>'
		setAttribute("id", "head1h");
		setAttribute("class", "zebra pkglist");
	}

	document.body.appendChild(tableHead);
}



//
function scrollHandler(){
	toolbar = document.getElementById('toolbar');
	paddingTop = toolbar.offsetTop + toolbar.offsetHeight;
	paddingTopPx = paddingTop + 'px';

	headerOffset = document.getElementById('head1').offsetTop;
	windowScrolled = document.body.scrollTop;
	if ((headerOffset - windowScrolled) < paddingTop)
		{
//		document.getElementById('miscinfo1').innerText = '<';
		var head1h = document.getElementById('head1h');
		var head1  = document.getElementById('head1');

		with (head1h.style) {
			setProperty('top', paddingTopPx, 1);
			setProperty('display', 'table', 1);
			setProperty('left',   head1.offsetLeft + 'px', 1);
			setProperty('width',  head1.offsetWidth + 'px', 1);
		}

//		document.getElementById('miscinfo1').innerText = '(' + toopop +')P^' + paddingTop + 'L' + head1h.offsetLeft + ':W' + head1h.offsetWidth + ':H' + head1h.offsetHeight + ':T' + head1h.clientTop +',' + head1h.offsetTop;

		}
	else
		{
		//document.getElementById('miscinfo1').innerText = '>';
		document.getElementById('head1h').style.display = 'none';
		}

	tHeadTr  = document.getElementById('head1h').children[0].children[0];
	tHeadTrO = document.getElementById('head1').children[0].children[0];
	tHeadTr.children[0].style.setProperty('width', tHeadTrO.children[0].offsetWidth -1 + 'px', 1);
	tHeadTr.children[1].style.setProperty('width', tHeadTrO.children[1].offsetWidth -1 + 'px', 1);
	tHeadTr.children[2].style.setProperty('width', tHeadTrO.children[2].offsetWidth -1 + 'px', 1);
	//tHeadTr.children[3].style.setProperty('width', tHeadTrO.children[3].offsetWidth -1 + 'px', 1);

}



// Handler for History scroller for Terminal
function keydownHandler(e) {
	// Get code for pressed key
	var evt = e ? e:event;
	var keyCode = evt.keyCode;

	// If pressed "up" or "down"
	if (keyCode==38 || keyCode==40) {
		// Local storage used as global variables storage
		// Get current position in the History, and History size
		//var cur_hist = window.localStorage.getItem("cur_hist");
		//var max_hist = window.localStorage.getItem("max_hist");
		switch(keyCode) {
			case 38:
				// "up" key pressed; decrement and normalize position
				cur_hist--; if (cur_hist < 0) cur_hist = 0;
				break;
			case 40:
				// "down" key pressed; increment and normalize position
				cur_hist++; if (cur_hist > max_hist) cur_hist = max_hist;
				break;
		}
		// Element "cmd" is a text input, put History element there
		var cmd = document.getElementById('typeField');
		cmd.focus();
		cmd.innerText = ash_history[cur_hist];

		var hint = ''
		if (cur_hist < max_hist) hint = '[' + cur_hist + '/' + (max_hist - 1) + '] ';
		document.getElementById('num_hist').innerText = hint;

		//window.localStorage.setItem('cur_hist', cur_hist);
		return false
	}
	if (keyCode==13) {
		document.getElementById('cmd').value=document.getElementById('typeField').innerText;
		document.getElementById('term').submit();
		return false
	}
	return true
}



// Add hover effect for menu
function menuAddHover() {
	var toolbarMenu = document.getElementById('toolbarMenu');
	toolbarMenu.className = 'hover';

	menus = toolbarMenu.getElementsByTagName('li');
	for (i = 0; i < menus.length; i++)
		menus[i].blur();

	toolbarMenu.focus();
	toolbarMenu.onblur = menuRmHover;
	console.log('Add finished');
}

// Remove hover effect for menu
function menuRmHover() {
	var toolbarMenu = document.getElementById('toolbarMenu');
	toolbarMenu.className = 'nohover';

	menus = toolbarMenu.getElementsByTagName('li');
	for (i = 0; i < menus.length; i++)
		menus[i].onclick = menuAddHover;

	console.log('Rm finished');
}


// Close main menu
function closeMenu() {
	document.getElementById('noMenu').style.display = 'none';
	closeItem(itemOpened);
	menuIsClosed = true;
	//console.log('Menu closed');
}
// Open main menu
function openMenu() {
	//console.log('openMenu')
	document.getElementById('noMenu').style.display = 'block';
	menuIsClosed = false;
}
// Open main menu item
function openItem(el) {
	if (itemOpened != el) {
		if (itemOpened)
			closeItem(itemOpened);
		el.children[1].className = 'opened';
		el.focus();
		itemOpened = el;
		menuIsClosed = false; openMenu();
		//console.log('Opened %s', el.tabIndex);
		//console.log('Menu opened (open)');
	}
}
// Close main menu item
function closeItem(el) {
	//console.log('<closeItem: "%s">', el)
	thisMenu = el.children[1];
	if (thisMenu.className == 'opened') {
		thisMenu.className = 'closed';
		el.blur();
		itemOpened = ''
		//console.log('Closed %s', el.tabIndex);
	}
}

itemOpened = '';
menuIsClosed = true;

// Add event handler
function addMenuHandlers() {
	menus = document.getElementById('toolbarMenu').children;
	for (i = 0; i < menus.length; i++) {
		menus[i].firstElementChild.onclick     = function() {menuItemClick(this)};
		menus[i].firstElementChild.onmouseover = function() {menuItemHover(this)};
		menus[i].onblur      = function() {menuItemBlur(this)};
	}

	// Close menu when click outside menu
	document.getElementById('noMenu').onclick = closeMenu;
}

function menuItemClick(el) {
	topItem = el.parentElement;
	thisMenu = topItem.children[1];
	//console.log('Clicked %s class %s', topItem.tabIndex, thisMenu.className);
	if (thisMenu.className == 'opened') {
		closeItem(topItem);
		menuIsClosed = true; closeMenu();
		//console.log('Menu closed (click)');
	}
	else {
		openItem(topItem);
		menuIsClosed = false; openMenu();
		//console.log('Menu opened (click)');
	}
}

function menuItemHover(el) {
	hoverElem = el.parentElement;
	//console.log('Hovered %s', hoverElem.tabIndex);
	if (! menuIsClosed) {
		closeItem(itemOpened);
		openItem(hoverElem);
	}
}
function menuItemBlur(el) {
	elem = el; //.parentElement;
	//console.log('Blurred %s', elem.tabIndex);
	//closeItem(elem);
	//menuIsClosed = true;
	//console.log('Menu closed (blur)');
}



//
// AJAX code for dynamic requests
//

function ajax(cgiUrl, command, ajaxOut) {
	// (1) create object for server request
	var req = new XMLHttpRequest();

	// (2) show request status
	var statusElem = document.getElementById('ajaxStatus');

	req.onreadystatechange = function() {
		// onreadystatechange activates on server answer receiving

		if (req.readyState == XMLHttpRequest.DONE) {
			// if request done
			statusElem.innerHTML = req.statusText // show status (Not Found, ОК..)

			// if status 200 (ОК) - show answer to user
			if (req.status == 200)
				document.getElementById(ajaxOut).innerHTML = req.responseText;
			// here we can add "else" with request errors processing
		}
	}

	// (3) set request address
	req.open('POST', cgiUrl, true);

	// (4) request object is ready
	req.send(command); // send request

	// (5)
	statusElem.innerHTML = '<img src="/styles/default/images/loader.gif" />'
}



//
// Load configuration for new and stored networks
//

function loadcfg(essid, bssid, keyType) {
	// looking for stored network
	for (i = 0; i < networks.length; i++) {
		if (networks[i].ssid == essid) break;
		if (typeof networks[i].bssid != 'undefined') {
			if (networks[i].bssid == bssid) {
				essid = networks[i].ssid;
				break;
			}
		}
	}
	document.getElementById('essid').value = essid;
	document.getElementById('keyType').value = keyType;

	password = document.getElementById('password')
	password.value = '';
	if (typeof networks[i] != 'undefined') {
		if (typeof networks[i].psk != 'undefined')
			password.value = networks[i].psk;
		else if (typeof networks[i].wep_key0 != 'undefined')
			password.value = networks[i].wep_key0;
		else if (typeof networks[i].password != 'undefined')
			password.value = networks[i].password;
	}

	// Not used yet
	document.getElementById('bssid').value = '';

	wifiSettingsChange();
}


//
// Toggle all checkboxes on a page
//

function checkBoxes() {
	var inputs = document.getElementsByTagName('input');
	for (var i = 0; i < inputs.length; i++) {
		if (inputs[i].type && inputs[i].type == 'checkbox') {
			inputs[i].checked = !inputs[i].checked;
			countSelPkgs(inputs[i]);
		}
	}
}


//
// Count selected packages on the packages list
//

function countSelPkgs(el) {
	countSelected = countSelectedSpan.innerText;
	if (countSelected == '') countSelected = 0;

	element = (el.type == 'change' ? this : el);

	if (element.checked)
		countSelected++;
	else
		countSelected--;

	countSelectedSpan.innerText = countSelected;
}

// Attach event handler
function setCountSelPkgs() {
	// The change event does not bubble to the form container
	pkglist = document.getElementById('pkglist');
	if (pkglist) {
		var checkboxes = pkglist.getElementsByTagName('input');
		for (i = 0; i < checkboxes.length; i++) {
			checkboxes[i].onchange = countSelPkgs;
		}
	}
	countSelectedSpan = document.getElementById('countSelected');
}
