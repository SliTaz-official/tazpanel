/*
	Login and password validation
	Copyright (C) 2012 SliTaz GNU/linux - GNU gpl v3
*/

////
// i18n for this javascript

function i18n(text){
	var lang = document.getElementsByTagName("html")[0].getAttribute("lang");
	var orig = ["Too short!", "Too long!", "Invalid chars!", "(No Password!)", "(Strong)", "(Medium!)", "(Weak!)", "Do Not Match!"];
	var translate = ["es", "fr", "pt", "ru"];
	translate['ru'] = ["Слишком короткий!", "Слишком длинный!", "Недопустимые символы!", "(Нет пароля!)", "(Сильный)", "(Средний!)", "(Слабый!)", "Не совпадает!"];
	translate['fr'] = [ ];

	var output = text;
	for (var i=0; i<orig.length; i++) {
		if (translate[lang] !== undefined && orig[i] == text) {
			var transTry = translate[lang][i];
			if (transTry !== undefined && transTry !== '') {
				var output = transTry;
			}
		break
		}
	}
	return(output);
}

////
// Login validation - typical use:
// <input id="login1" onkeyup="checkLogin('login1','msg1'); return false;" />
// <span id="msg1"></span>

function checkLogin(user,message){
	var login = document.getElementById(user);
	var msg   = document.getElementById(message);
	var enoughRegex = new RegExp("(?=.{3,}).*", "g");
	var incharRegex = new RegExp("^[A-Za-z0-9_-]{3,32}$");
	// html fragments
	var nok='<span class="msg-nok">&#x2716; ';
	var s='</span>';

	if (login.value == '') {
		msg.innerHTML = '';
	} else if (false == enoughRegex.test(login.value)) {
		msg.innerHTML = nok + i18n('Too short!') + s;
		return false;
	} else if (login.value.length > 32) {
		msg.innerHTML = nok + i18n('Too long!') + s;
		return false;
	} else if (false == incharRegex.test(login.value)) {
		msg.innerHTML = nok + i18n('Invalid chars!') + s;
		return false;
	} else {
		msg.innerHTML = '<span class="msg-ok">&#x2714;'+s;
	}
}

////
// Password validation - typical use:
// <input type="password" id="pass1" onkeyup="checkPwd('pass1','pass2','msg2'); return false;" />
// <input type="password" id="pass2" onkeyup="checkPwd('pass1','pass2','msg2'); return false;" />
// <span id="msg2"></span>

function checkPwd(password,confirm,message){
	var pwd1 = document.getElementById(password);
	var pwd2 = document.getElementById(confirm);
	var msg  = document.getElementById(message);
	// html fragments
	var nok = '<span class="msg-nok">&#x2716; ';
	var okw = '<span class="msg-ok">&#x2714; </span><span class="msg-warn">';
	var s = '</span>';

	if(pwd1.value == pwd2.value){
		// passwords match.
		pwd2.classList.remove('alert');
		// various checks
		var enoughRegex = new RegExp("(?=.{3,}).*", "g");
		var incharRegex = new RegExp("^[A-Za-z0-9!@#$%^&*()_]{3,40}$");
		var strongRegex = new RegExp("^(?=.{8,})(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*\\W).*$", "g");
		var mediumRegex = new RegExp("^(?=.{7,})(((?=.*[A-Z])(?=.*[a-z]))|((?=.*[A-Z])(?=.*[0-9]))|((?=.*[a-z])(?=.*[0-9]))).*$", "g");
		if (pwd1.value.length==0) {
			msg.innerHTML = okw + i18n('(No Password!)') + s;
		} else if (pwd1.value.length > 40) {
			msg.innerHTML = nok + i18n('Too long!') + s;
			return false;
		} else if (false == enoughRegex.test(pwd1.value)) {
			msg.innerHTML = nok + i18n('Too short!') + s;
			return false;
		} else if (false == incharRegex.test(pwd1.value)) {
			msg.innerHTML = nok + i18n('Invalid chars!') + s;
			return false;
		} else if (strongRegex.test(pwd1.value)) {
			msg.innerHTML = '<span class="msg-ok">&#x2714; ' + i18n('(Strong)') + s;
		} else if (mediumRegex.test(pwd1.value)) {
			msg.innerHTML = okw + i18n('(Medium!)') + s;
		} else {
			msg.innerHTML = okw + i18n('(Weak!)') + s;
		}
	} else {
		// passwords do not match.
		pwd2.classList.add('alert');
		msg.innerHTML = nok + i18n('Do Not Match!') + s;
		return false;
	}
}
