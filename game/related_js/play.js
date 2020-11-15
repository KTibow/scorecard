function closeOverlay() {
    document.getElementById("overlay").style.opacity = "0";
    document.getElementById("overlay").style.visibility = "hidden";
}
function openOverlay(message) {
    document.getElementById("overlay").style.opacity = "1";
    document.getElementById("overlay").style.visibility = "";
    document.getElementById("overlay-text").innerHTML = message;
}
function getPosition(element) {
    var xPos = 0;
    var yPos = 0;
    while (element) {
        xPos += element.offsetLeft - element.scrollLeft + element.clientLeft;
        yPos += element.offsetTop - element.scrollTop + element.clientTop;
        element = element.offsetParent;
    }
    return {
        x: xPos,
        y: yPos,
    };
}
function registerGroup() {
    var idInput = document.getElementById("username");
    var url = "/addid/" + userId + "/" + idInput.value;
    fetch(url)
        .then((result) => {
            return result.text() != "notreal";
        })
        .then((idValid) => {
            var buttonIcon = document.createAttribute("data-icon");
            if (idValid) {
                // Confetti
                var pos = getPosition(idInput);
                pos["x"] = pos["x"] + idInput.offsetWidth / 2;
                pos["x"] = pos["x"] / window.innerWidth;
                pos["y"] = pos["y"] / window.innerHeight;
                confetti({
                    particleCount: 100,
                    startVelocity: 30,
                    spread: 100,
                    origin: pos,
                });
                // Other stuff
                buttonIcon.value = "done";
                document.getElementById("adgr").innerHTML = "Added to group";
            } else {
                buttonIcon.value = "error";
                document.getElementById("adgr").innerHTML = "Invalid ID.";
            }
            document.getElementById("adgr").setAttributeNode(buttonIcon);
            setTimeout(() => {
                buttonIcon.value = "group_add";
                document.getElementById("adgr").setAttributeNode(buttonIcon);
                document.getElementById("adgr").innerHTML = "Add to group";
            }, 1000);
        });
}
function goHome() {
    window.location = "/";
}
function getGroup() {
    if (document.hasFocus()) {
        fetch("/gids/" + userId)
            .then((response) => {
                return response.text();
            })
            .then((response) => {
                document.getElementById("gstat").innerHTML = response;
            });
    }
}
setInterval(getGroup, 400);
function getCard() {
    var attemptsElement = document.getElementById("attmpts");
    var attemptsSoFar = Number(attemptsElement.innerHTML) + 1;
    attemptsElement.innerHTML = String(attemptsSoFar);
    var renderPopupTimeout = 0;
    if (attemptsSoFar == 16) {
        openOverlay(
            "It looks like you've done all of the cards. Make sure you aren't repeating any."
        );
        renderPopupTimeout = 2000;
    }
    setTimeout(() => {
        fetch(
            `/cardstatus/${userId}/${document.getElementById("cardname").value}`
        )
            .then((result) => {
                return result.text();
            })
            .then((outcome) => {
                switch (outcome) {
                    case "correct":
                        openOverlay(
                            "That's the right clue! Your group can see you're finished now."
                        );
                        var confettiConfig = {
                            particleCount: 100,
                            startVelocity: 30,
                            spread: 360,
                        };
                        for (confettiDelay of [10, 510, 1010]) {
                            setTimeout(
                                confetti,
                                confettiDelay,
                                Object.assign(
                                    {
                                        origin: {
                                            x: Math.random(),
                                            y: Math.random() - 0.2,
                                        },
                                    },
                                    confettiConfig
                                )
                            );
                        }
                        fetch(`/finished/${userId}`);
                        break;
                    case "regular":
                        fetch(
                            `/nopecard/${
                                document.getElementById("cardname").value
                            }/${userId}`
                        )
                            .then((result) => {
                                return result.text();
                            })
                            .then((cardNum) => {
                                openOverlay(
                                    `This is a normal card. Don't go looking for card ${cardNum}`
                                );
                            });
                        break;
                    case "invalid":
                        openOverlay(
                            "That's an invalid clue. Make sure you're in a group."
                        );
                        break;
                    default:
                        openOverlay("WTH?" + outcome)
                        break;
                }
            });
    }, renderPopupTimeout);
}
