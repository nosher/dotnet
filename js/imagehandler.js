const MAIN = $('#fullsize');
const DT_IMG_SIZE = 800; // the apparent width/height of desktop images

var image_position = 0;
var initialAspect = screen.orientation.type;
var isLandscape = false;
if (initialAspect.includes("landscape")) {
    isLandscape = true;
}

//window.addEventListener("load", imageSetter);
screen.orientation.addEventListener("change", orient);
addSwipe();
addKeyListeners();

/*
 *  Entry-point function called from photo album HTML
 */
function showViewer(pos) {
    // update image_position with requested image as 
    // this is accessed by the key listeners
    imageSetter();
    image_position = pos; 
    var props = getProps();
    if (props.isMobile) {
        var mv = $("#mobile_viewer");
        if (mv && isLandscape) {
            mv.get(0).requestFullscreen("hide")
                .then(() => {
                    console.log("PROMISE: with image setter");
                    imageSetter();
                    mv.show(0);
                })
                .catch((err) => {
                    console.log("PROMISE: failed, show without setter");
                    mv.show(0);
                });

        } else {
            mv.show(0);
        }
        
    } else {
        $("#viewer").show(300);
    }
    showImage(image_position, isLandscape);
}

function hideViewer() {
    if (getProps().isMobile) {
        $("#mobile_viewer").hide(300, function() {})
    } else {
        $("#viewer").hide(300, function() {
            MAIN.attr('src', '');
        });
    }
}

function orient() {
    isLandscape = !isLandscape;
    console.log("LANDSCAPE:", isLandscape);
    hideViewer();
    document.exitFullscreen()
        .then(() => {
            console.log("Exit fullscreen");
        })
        .catch((err) => console.log("not in fullscreen"));
}

function showImage(position, landscape) {
    var props = getProps();
    console.log("IMG: showing " + position);
    if (props.isMobile) {
        showMobileImages(position, landscape);
    } else {
        showDesktopImage(position);
    }
}

function getProps() {
    var winwidth = window.innerWidth;
    var winheight = window.innerHeight;
    return {
        "winwidth": winwidth,
        "winheight": winheight,
        // see nosher2.css for media rules defining a mobile view
        "isMobile": ((winwidth > winheight) ? winwidth : winheight) < 1000
    }
}

function imageSetter() {
    var props = getProps();
    /*
    *  Set the currently-empty image height and widths, if dimensions[] is available
    */
    if (Object.keys(dimensions).length > 0) {
        for (i = 0; i < imgCount; i++) {
            var iwidth = iheight = 0;
            var ratio = dimensions[ids[i]];
            if (props.isMobile) {
                if (isLandscape) {
                    iheight = Math.floor(props.winheight * 0.9);
                    iwidth = Math.floor(iheight / ratio);
                } else {
                    iwidth = props.winwidth;
                    iheight = Math.floor(iwidth * ratio);
                }
            } else {
                iwidth = DT_IMG_SIZE;
                iheight = Math.floor(iwidth * ratio);
            }
            var container = document.getElementById("mphoto_" + i);
            var img = document.getElementById(ids[i]);

            // set style width and height
            container.style.width = iwidth + "px";
            if (isLandscape) {
                container.style.height = iheight + "px";
            } else {
                container.style.height = "auto";
            }
            img.style.width = iwidth + "px";
            img.style.height = iheight + "px";
            console.log("SET: ", iwidth, "x", iheight);
        }
    };
    if (index > -1) {
        setTimeout(showViewer(index), 1500);
    };
}

function addSwipe() {
    MAIN.swipe( {
            threshold: 75,
            swipe: function(event, direction, distance, duration, fingerCount, fingerData) {
            if (direction == "right" 
                    && $("#viewer").is(":visible") 
                    && image_position > 0) {
                showImage(--image_position);
            } else if (direction == "left" 
                        && $("#viewer").is(":visible") 
                        && image_position < imgCount - 1) {
                showImage(++image_position);
            } 
            }
    });
}

function addKeyListeners() {
    $(window).keydown(function(event) {
        if (event.which == 37) {
            // cursor left
            if ($("#viewer").is(":visible") && image_position > 0) {
                goto(--image_position, event);
            } else if (prevAlbum !== undefined) {
                window.location.href = getUrl() + prevAlbum; 
            }
        } else if (event.which == 39 || event.which == 32) {
            // cursor right or spacebar
            if ($("#viewer").is(":visible") && image_position < imgCount - 1) {
                goto(++image_position, event);
            } else if (nextAlbum !== undefined) {
                window.location.href = getUrl() + nextAlbum; 
            }
        } else if (event.which == 35) {
            // end
            goto(imgCount - 1, event);
        } else if (event.which == 38) {
            // cursor up
            MAIN.animate({scrollTop: 0});
        } else if (event.which == 40) {
            // cursor down 
            MAIN.animate({scrollTop: 9999});
        } else if (event.which == 88) {
            // X keypress
            hideViewer();
        } else {
            console.log(event.which);
        }
    });
}

function getUrl() {
    return window.location.protocol 
                + "//" + window.location.hostname 
                + (window.location.hostname != "nosher.net" ? ":8010" : "") 
                + "/images/"
}

function goto(pos, event) {
    event.preventDefault();
    showImage(pos);
}

function scrollImgToView(position, landscape) {
    var el = document.getElementById(ids[position]);
    el.scrollIntoView();
    if (position < (imgCount - 1)) {
        // show a bit of the previous image
        if (!landscape) {
            window.scrollBy(0, -80);
        }
    }
}

function showDesktopImage(pos) {
    MAIN.prop("title", images[pos] + ", {{year}}, " + captions[pos]);
    $("#caption").html(captions[pos] + "<span class=\"closetext\" onclick='hideViewer();'> (X) </span>");
    for (var i = 0; i < imgCount; i++) {
        elem = document.getElementById((i + 1) + "-marker");
        elem.className = "lolite";
    }
    elem = document.getElementById((pos + 1) + "-marker");
    elem.className = "hilite";
    var thumb = 74;
    var half = $(window).width() / 2 - thumb;
    var newpos = pos * thumb;
    if (newpos > half) {
        $("#wrapper").scrollLeft(pos * thumb - half - thumb / 4);
    } else if (newpos < half) {
        $("#wrapper").scrollLeft(0);
    }
    MAIN.hide();
    var imgUrl = base + "/" + images[pos] + "-m.webp";
    MAIN.attr("alt", "{{title}}, " + captions[pos]);
    MAIN.attr("src", imgUrl).on("load", function() {
        
        var inMemory = new Image();
        inMemory.onload = function() {
            width = this.width;
            height = this.height;
            if (height > 1200 || width > 1200) {
                // for extra-large images, scale down by half as these are intended as
                // hi-res images for high-density displays
                width = width / 2;
                height = height / 2;
            }
            if (width > $(window).width()) {
                // we're probably in a width-constrained situation
                dWidth = $(window).width() * 0.8;
                dHeight = dWidth * height / width; 
                MAIN.css('max-width', dWidth + 'px')
                MAIN.css('max-height', dHeight + 'px')
                console.log("dwidth ", dWidth)
            } else {
                MAIN.css('max-width', width + 'px')
                MAIN.css('max-height', height + 'px')
                console.log("width ", width)
            }
            MAIN.fadeIn(100);
        };
        inMemory.src = MAIN.attr("src");
    });
}

/*
*
* Asynchronous functions
*
*/

async function showMobileImages(position, landscape) {
    console.log("IMG show mobile images");
    const pos = await asyncImageLoader(position, landscape);
    scrollImgToView(position, landscape)
    var others = [];
    var next = position + 1;
    var prev = position - 1;
    // interleave remaining images, e.g. 4 5 3 6 2 7 1
    while (next < imgCount || prev > -1) {
        if (next < imgCount) {
            others.push(next);
        }
        if (prev > -1) {
            others.push(prev);
        }
        prev--;
        next++;
    }
    for (i = 0; i < others.length; i++) {
        await asyncImageLoader(others[i], landscape)
    }
}

async function asyncImageLoader(position) {
    var frame = $("#mphoto_" + position);
    var url = base + "/" + images[position] + "-m.webp";
    var img = frame.find("img");
    var props = getProps();
    const imageLoadPromise = new Promise(resolve => {
        console.log("IMG ", url, " loading");
        img.attr("src", url).on("load", function() {
            if (Object.keys(dimensions).length == 0) {
                // no dimensions defined, so set width and height from the natural dimensions
                var lwidth = this.naturalWidth;
                var lheight = this.naturalHeight;
                var ratio = lheight / lwidth;
                if (props.isMobile) {
                    // here, landscape relates to the display, not the image
                    if (isLandscape) {
                        iheight = Math.floor(props.winheight * 0.9);
                        iwidth = Math.floor(iheight / ratio);
                    } else {
                        iwidth = props.winwidth;
                        iheight = Math.floor(iwidth * ratio);
                    }
                } else {
                    // here, landscape relates to the image, not the display
                    if (lwidth > lheight) {
                        iwidth = DT_IMG_SIZE;
                        iheight = Math.floor(iwidth * ratio);
                    } else {
                        iheight = DT_IMG_SIZE;
                        iwidth = Math.floor(iheight / ratio);   
                    }
                }
                console.log("SET NATURAL W/H: ", iwidth, iheight);
                this.height = iheight;
                this.width = iwidth;
            }
            console.log("IMG ", "loaded");
            resolve();
        })
    }).catch((err) => {console.log("IMG ERR ", err)});;
    await imageLoadPromise;
    return position;
};