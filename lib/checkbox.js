javascript:(function() {
function checkBoxes(w) {
	try {
		var inputs = w.document.getElementsByTagName('input');
		for (var i = 0; i < inputs.length; i++) {
			if (inputs[i].type && inputs[i].type == 'checkbox') {
				inputs[i].checked = !inputs[i].checked;
			}
		}
	} catch (e){}
	if (w.frames && w.frames.length>0) {
		for (var i = 0; i < w.frames.length;i++) {
			var fr = w.frames[i];
			checkFrames(fr);
		}
	}
}
checkBoxes(window);
})()
