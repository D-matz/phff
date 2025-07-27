//make element moveable eg dragElt(document.getElementById('allergy-form'))
//note it should have position right and position top
function dragElt(elt) {
    var startX, startY, startRight, startTop, isDown = false;
    elt.onmousedown = function(e) {
        isDown = true;
        startX = e.clientX;
        startY = e.clientY;
        startRight = parseInt(window.getComputedStyle(elt).right, 10);
        startTop = parseInt(window.getComputedStyle(elt).top, 10);
        document.body.style.userSelect = 'none';
    };
    document.onmousemove = function(e) {
        if (!isDown) return;
        var dx = e.clientX - startX;
        var dy = e.clientY - startY;
        elt.style.right = (startRight - dx) + 'px';
        elt.style.top = (startTop + dy) + 'px';
    };
    document.onmouseup = function() {
        isDown = false;
        document.body.style.userSelect = '';
    };
};