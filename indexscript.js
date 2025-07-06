
document.addEventListener("DOMContentLoaded", function () {
    const video = document.getElementById("video");
    const borderElement = document.querySelector(".border");
    const borderTwoElement = document.querySelector(".bordertwo");
    const borderThreeElement = document.querySelector(".borderthree");
    const borderFourElement = document.querySelector(".borderfour");
    const h2Element = document.querySelector("h2");
    let lastScrollY = window.scrollY;

    video.addEventListener("ended", function () {
        this.currentTime = 0;
        this.play();
    });

    video.playbackRate = 1;

    function adjustBackgroundEffects() {
        let scrollY = window.scrollY;
        let documentHeight = document.documentElement.scrollHeight;
        let windowHeight = window.innerHeight;
        let scrollPercentage = scrollY / (documentHeight - windowHeight);

        let blurAmount = Math.max(10 - scrollPercentage * 20, 0);
        video.style.filter = `blur(${blurAmount}px)`;

        let zoomFactor = 1 + scrollPercentage * 0.2;
        video.style.transform = `translate(-50%, -50%) scale(${zoomFactor})`;
    }

    function handleElementFade() {
        let scrollY = window.scrollY;
        let documentHeight = document.documentElement.scrollHeight;
        let windowHeight = window.innerHeight;
        let scrollPercentage = (scrollY / (documentHeight - windowHeight)) * 100;

        let scrollingDown = scrollY > lastScrollY;
        lastScrollY = scrollY;

        function fadeInElement(element, percentage) {
            if (scrollPercentage >= percentage) {
                element.classList.add("faded");
                element.classList.remove("fade-out");
            }
        }

        function fadeOutElement(element, percentage) {
            if (scrollPercentage <= percentage) {
                element.classList.add("fade-out");
                element.classList.remove("faded");
            }
        }

        if (borderTwoElement) {
            fadeInElement(borderTwoElement, 35);
            fadeOutElement(borderTwoElement, 35);
        }

        if (borderThreeElement) {
            fadeInElement(borderThreeElement, 40);
            fadeOutElement(borderThreeElement, 40);
        }

        if (borderFourElement) {
            fadeInElement(borderFourElement, 65);
            fadeOutElement(borderFourElement, 70);
        }
    }

    function shrinkBorderOnScroll() {
        let scrollY = window.scrollY;
        let initialHeight = 700; 
        let newHeight = Math.max(initialHeight - scrollY * 1.2, 16);
        borderElement.style.height = newHeight + "px";
    }
    
    function fadeH2OnScroll() {
        let scrollTop = window.scrollY;
        let fadeStart = 0;
        let fadeEnd = 100;
        let opacity = 1 - (scrollTop - fadeStart) / (fadeEnd - fadeStart);

        if (opacity < 0) opacity = 0;
        if (opacity > 1) opacity = 1;

        h2Element.style.opacity = opacity;
    }

    window.addEventListener("scroll", function () {
        adjustBackgroundEffects();
        handleElementFade();
        shrinkBorderOnScroll();
        fadeH2OnScroll();
    });
});

window.addEventListener('scroll', function () {
    let h2Element = document.querySelector('h2');
    let scrollTop = window.scrollY;
    let fadeStart = 0;
    let fadeEnd = 100;
    let opacity = 1 - (scrollTop - fadeStart) / (fadeEnd - fadeStart);

    if (opacity < 0) opacity = 0;
    if (opacity > 1) opacity = 1;

    h2Element.style.opacity = opacity;
});

document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});
