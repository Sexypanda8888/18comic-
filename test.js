function scramble_image(e, t, a, n, d) {
    if (n || (n = !1),
        d || (d = !1),
        e.src.indexOf(".jpg") < 0 || parseInt(t) < parseInt(a) || "1" == d)
        return console.log(e.style.display),
            void("none" === e.style.display && (e.style.display = "block"));
    1 == n || 0 == e.complete ? document.getElementById(e.id).onload = function() {
            onImageLoaded(e)
        } :
        onImageLoaded(e)
}

function onImageLoaded(e) {
    var t;
    null == e.nextElementSibling ? (t = document.createElement("canvas"),
        e.after(t)) : t = document.getElementById(e.id).nextElementSibling;
    var a = t.getContext("2d"),
        n = e.width,
        d = e.naturalWidth,
        i = e.naturalHeight;
    t.width = d,
        t.height = i,
        (n > e.parentNode.offsetWidth || 0 == n) && (n = e.parentNode.offsetWidth),
        t.style.width = n + "px",
        t.style.display = "block";
    var l = document.getElementById(e.id).parentNode;
    l = (l = l.id.split("."))[0];
    for (var s = get_num(aid, l), r = parseInt(i % s), o = d, m = 0; m < s; m++) {
        var c = Math.floor(i / s),
            g = c * m,
            h = i - c * (m + 1) - r;
        0 == m ? c += r : g += r,
            a.drawImage(e, 0, h, o, c, 0, g, o, c)
    }
    $(e).addClass("hide")
}
//e是aid，l是000X的数字。
//l经过加以后变成n，变成Md5后获取最后一个字符的asc2码，最后余十
l = (l = l.id.split("."))[0];

function get_num(e, t) {
    var a = 10;
    if (e >= 268850) {
        var n = e + t;
        switch (n = (n = (n = md5(n)).substr(-1)).charCodeAt(),
            n %= 10) {
            case 0:
                a = 2;
                break;
            case 1:
                a = 4;
                break;
            case 2:
                a = 6;
                break;
            case 3:
                a = 8;
                break;
            case 4:
                a = 10;
                break;
            case 5:
                a = 12;
                break;
            case 6:
                a = 14;
                break;
            case 7:
                a = 16;
                break;
            case 8:
                a = 18;
                break;
            case 9:
                a = 20
        }
    }
    return a
}