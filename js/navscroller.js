// script to freeze the navigation at its bottom if on a very long
// page of content

function navscroll() {

    const HEADER = document.getElementById("header");
    const FOOTER = document.getElementById("footer");
    const MAIN_CONTENT = document.getElementById("cmain");
    const NAV_WRAPPER = document.getElementById("navwrapper")

    var windowHeight = window.innerHeight;
    var isDesktop = window.innerWidth > 1000; // see nosher2.css for definition of mobile width
    var headerHeight = HEADER.offsetHeight;
    var footerHeight = FOOTER.offsetHeight + 40;
    var navHeight = NAV_WRAPPER.offsetHeight;
    var navWidth = NAV_WRAPPER.offsetWidth;
    var lastY = 0;
    var constrainedY = 0;

    // don't bother unless the content area is reasonably longer than the navigation
    if (isDesktop && (MAIN_CONTENT.offsetHeight > navHeight * 1.2)) {
        window.addEventListener("scroll", (event) => {
            var scrollY = window.scrollY;
            var dY = scrollY - lastY;
            constrainedY += dY;
            var max = 0;
            if (navHeight > windowHeight) {
                max = (navHeight - windowHeight + (footerHeight * 2));
            } else {
                max = headerHeight;
            }
            constrainedY = Math.min(Math.max(constrainedY, 0), max)
            NAV_WRAPPER.style.position = "fixed";
            NAV_WRAPPER.style.width = navWidth + "px";
            NAV_WRAPPER.style.top = (headerHeight - constrainedY) + "px";
            lastY = scrollY;
        });
    }
}