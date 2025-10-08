$(document).ready(function() {
    
    var media = window.matchMedia("(max-width: 840px)")
    disableForMobile(media);
    $('html, body').animate({
        scrollTop: ($('.hilite').first().top)
    },500);
});

$(window).on("load", function() {
    var doZoom = false;
    var zoomer = $(".zoomer");
    var magicon = $(".magicon");
    var height = zoomer.height();
    var zimg = zoomer.children("img");
    var offset = zimg.offset()
    var naturalWidth = zimg.get(0).naturalWidth;
    var naturalHeight = zimg.get(0).naturalHeight;
    addKeyListeners();
    if (naturalWidth > 1200) {
        magicon.show();
        magicon.on("click", function() {
            doZoom = !doZoom;
            if (doZoom) {
                $(this).children("button").html("Turn off zoom");
            } else {
                $(this).children("button").html("🔍 Click to zoom");

            }
        });
        zoomer.on("mouseover", function() {
            if (doZoom) {
                    console.log(zimg.get(0).naturalWidth);   
                    zimg.width(naturalWidth);
                    zimg.height(naturalHeight);
                    zoomer.height(height);
                    zoomer.css('cursor','zoom-in');
                    console.log(zimg.width());   
                    zoomer.on("mousemove", function(event) {
                    if (doZoom) {
                        var newx = event.pageX - offset.left;
                        var newy = event.pageY - offset.top;
                        zimg.offset({left: offset.left - newx, top: offset.top - newy});
                    } 
                    });

            }
        });
        zoomer.on("mouseout", function() {
            if (doZoom) {
                    zimg.width(700);
                    zimg.height(naturalHeight/2);
                    zimg.offset(offset);
            }
        });
    }
});

function getUrl() {
    return window.location.protocol 
                + "//" + window.location.hostname 
                + (window.location.hostname != "nosher.net" ? ":8010" : "") 
                + "/archives/computers/"
}

function disableForMobile(x) {
    if (x.matches) { 
        $("#zoom").hide();
    } 
}

function addKeyListeners() {
    $(window).keydown(function(event) {
        console.log(event.which);
        switch (event.which) {
              case 37:
                // cursor left
                if (prev != "") {
                    window.location.href = getUrl() + prev; 
                }
                break;
            case 32:
            case 39:
                // cursor right or spacebar
                if (next != "") {
                    window.location.href = getUrl() + next; 
                }
                event.stopPropagation();
                break;
            default:
                console.log(event.which);
        }
    });
}
