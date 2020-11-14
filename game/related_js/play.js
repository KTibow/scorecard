function closeOverlay() {
    document.getElementById("overlay").style.opacity = "0";
    document.getElementById("overlay").style.visibility = "hidden";
}
function openOverlay(message) {
    document.getElementById("overlay").style.opacity = "1";
    document.getElementById("overlay").style.visibility = "";
    document.getElementById("overlay-text").innerHTML = message;
}
function getPosition(el) {
    var xPos = 0;
    var yPos = 0;
    while (el) {
        xPos += el.offsetLeft - el.scrollLeft + el.clientLeft;
        yPos += el.offsetTop - el.scrollTop + el.clientTop;
        el = el.offsetParent;
    }
    return {
        x: xPos,
        y: yPos,
    };
}
function registerGroup() {
    var xmlhttp = new XMLHttpRequest();
    var idInput = document.getElementById("username");
    var url = "/addid/{{uid}}/" + idInput.value;
    var pos = getPosition(idInput);
    xmlhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            var attry = document.createAttribute("data-icon");
            if (this.responseText == "notreal") {
                attry.value = "error";
            } else {
                attry.value = "done";
                confetti({
                    particleCount: 100,
                    startVelocity: 30,
                    spread: 100,
                    origin: {
                        x:
                            (pos["x"] + idInput.offsetWidth / 2) /
                            window.innerWidth,
                        y: pos["y"] / window.innerHeight,
                    },
                });
            }
            document.getElementById("adgr").setAttributeNode(attry);
            if (this.responseText == "notreal") {
                document.getElementById("adgr").innerHTML = "Invalid ID.";
            } else {
                document.getElementById("adgr").innerHTML = "Added to group";
            }
            setTimeout(function () {
                var attry = document.createAttribute("data-icon");
                attry.value = "group_add";
                document.getElementById("adgr").setAttributeNode(attry);
                document.getElementById("adgr").innerHTML = "Add to group";
            }, 1000);
        }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}
function goHome() {
    window.location.href = "/";
}
function getGroup() {
    if (document.hasFocus()) {
        var xmlhttp = new XMLHttpRequest();
        var url = "/gids/{{uid}}";
        xmlhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                document.getElementById("gstat").innerHTML = this.responseText;
            }
        };
        xmlhttp.open("GET", url, true);
        xmlhttp.send();
    }
}
setInterval(getGroup, 400);
var xmlhttpy = new XMLHttpRequest();
var urly = "/rightnum/{{uid}}";
var nopes = [];
for (var i = 1; i <= 1000; i++) {
    nopes.push(i);
}
xmlhttpy.onreadystatechange = function () {
    if (this.readyState == 4 && this.status == 200) {
        nopes.pop(Number(this.responseText));
    }
};
xmlhttpy.open("GET", urly, true);
xmlhttpy.send();
function choose(choices) {
    var index = Math.floor(Math.random() * choices.length);
    return choices[index];
}
function getCard() {
    document.getElementById("attmpts").innerHTML = String(
        Number(document.getElementById("attmpts").innerHTML) + 1
    );
    var render_popup_timeout = 0;
    if (Number(document.getElementById("attmpts").innerHTML) == 16) {
        openOverlay(
            "It looks like you've done all of the cards. Make sure you aren't repeating any."
        );
        render_popup_timeout = 2000;
    }
    function renderPopup() {
        var xmlhttp = new XMLHttpRequest();
        var url =
            "/cardstatus/{{uid}}/" + document.getElementById("cardname").value;
        xmlhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                if (this.responseText == "0") {
                    var xmlhttp2 = new XMLHttpRequest();
                    var url2 = "/rightnum/{{uid}}";
                    xmlhttp2.onreadystatechange = function () {
                        if (this.readyState == 4 && this.status == 200) {
                            openOverlay(
                                "That's the right clue! The number is " +
                                    this.responseText +
                                    ". Share it with your friends, and they can verify it!"
                            );
                            setTimeout(confetti, 10, {
                                particleCount: 100,
                                startVelocity: 30,
                                spread: 360,
                                origin: {
                                    x: Math.random(),
                                    y: Math.random() - 0.2,
                                },
                            });
                            setTimeout(confetti, 510, {
                                particleCount: 100,
                                startVelocity: 30,
                                spread: 360,
                                origin: {
                                    x: Math.random(),
                                    y: Math.random() - 0.2,
                                },
                            });
                            setTimeout(confetti, 1010, {
                                particleCount: 100,
                                startVelocity: 30,
                                spread: 360,
                                origin: {
                                    x: Math.random(),
                                    y: Math.random() - 0.2,
                                },
                            });
                            var xmlhttp3 = new XMLHttpRequest();
                            var url3 = "/finished/{{uid}}";
                            xmlhttp3.open("GET", url3, true);
                            xmlhttp3.send();
                        }
                    };
                    xmlhttp2.open("GET", url2, true);
                    xmlhttp2.send();
                } else if (this.responseText == "1") {
                    if (nopes.length < 1) {
                        openOverlay(
                            "Ooops! You missed out on the right one from 1-1000."
                        );
                    } else {
                        var choice = choose(nopes);
                        openOverlay(
                            "This is a normal clue, and it tells you that it's not " +
                                String(choice)
                        );
                        nopes.pop(choice);
                    }
                } else if (this.responseText == "2") {
                    openOverlay("This clue doesn't help you.");
                } else if (this.responseText == "invalid") {
                    openOverlay(
                        "That's an invalid clue. Make sure you're in a group."
                    );
                }
            }
        };
        xmlhttp.open("GET", url, true);
        xmlhttp.send();
    }
    setTimeout(renderPopup, render_popup_timeout);
}
function checkNumber() {
    var xmlhttp = new XMLHttpRequest();
    var url = "/rightnum/{{uid}}";
    xmlhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            if (
                this.responseText == document.getElementById("numbername").value
            ) {
                openOverlay("Yup, this person actually got it!");
            } else {
                openOverlay("That's an invalid number. Double-check it.");
            }
        }
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}
