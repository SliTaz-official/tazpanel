/*
	Login and password validation
	Copyright (C) 2012 SliTaz GNU/linux - GNU gpl v3
*/

////
// Login validation - typical use:
// <input id="login1" onkeyup="checkLogin('login1','msg1'); return false;" />
// <span id="msg1"></span>

function checkLogin(user,message){
	var login = document.getElementById(user);
	var msg = document.getElementById(message);
	var enoughRegex = new RegExp("(?=.{3,}).*", "g");
	var incharRegex = new RegExp("^[A-Za-z0-9_-]{3,32}$");
	if (false == enoughRegex.test(login.value)) {
		msg.innerHTML ="<span class=\"msg-nok\">&#x2716; Too short</span>";
		return false;
	} else if (login.value > 32) {
		msg.innerHTML ="<span class=\"msg-nok\">&#x2716; Too long</span>";
		return false;
	} else if (false == incharRegex.test(login.value)) {
		msg.innerHTML ="<span class=\"msg-nok\">&#x2716; Invalid chars</span>";
		return false;		
	} else {
		msg.innerHTML = "<span class=\"msg-ok\">&#x2714;</span";
	}
}

////
// Password validation - typical use:
// <input type="password" id="pass1" onkeyup="checkLogin('pass1','pass2','msg2'); return false;" />
// <input type="password" id="pass2" onkeyup="checkLogin('pass1','pass2','msg2'); return false;" />
// <span id="msg2"></span>

function checkPwd(password,confirm,message){
	var pwd1 = document.getElementById(password);
	var pwd2 = document.getElementById(confirm);
	var msg = document.getElementById(message);
	if(pwd1.value == pwd2.value){
		// passwords match. 
		pwd2.classList.remove('alert');
		// various checks
		var enoughRegex = new RegExp("(?=.{3,}).*", "g");
		var incharRegex = new RegExp("^[A-Za-z0-9!@#$%^&*()_]{3,40}$");
		var strongRegex = new RegExp("^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g");
		var mediumRegex = new RegExp("^(?=.{7,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g");
		if (pwd1.value.length==0) {
			msg.innerHTML = "<span class=\"msg-ok\">&#x2714; </span><span class=\"msg-warn\">(No Password!)</span>";
		} else if (pwd1.value.length > 40) {
			msg.innerHTML ="<span class=\"msg-nok\">&#x2716; Too long!</span>";
			return false;
		} else if (false == enoughRegex.test(pwd1.value)) {
			msg.innerHTML ="<span class=\"msg-nok\">&#x2716; Too short!</span>";
			return false;
		} else if (false == incharRegex.test(pwd1.value)) {
			msg.innerHTML ="<span class=\"msg-nok\">&#x2716; Invalid chars!</span>";
			return false;
		} else if (strongRegex.test(pwd1.value)) {
			msg.innerHTML = "<span class=\"msg-ok\">&#x2714; (Strong)</span>";
		} else if (mediumRegex.test(pwd1.value)) {
			msg.innerHTML = "<span class=\"msg-ok\">&#x2714; </span><span class=\"msg-warn\">(Medium!)</span>";
		} else {
			msg.innerHTML = "<span class=\"msg-ok\">&#x2714; </span><span class=\"msg-warn\">(Weak!)</span>";
		}
	} else {
		// passwords do not match.
		pwd2.classList.add('alert');
		msg.innerHTML = "<span class=\"msg-nok\">&#x2716; Do Not Match!</span>"
		return false;
	}
}  