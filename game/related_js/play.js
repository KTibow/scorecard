function closeOverlay() {
    document.getElementById("overlay").style.opacity = "0";
    document.getElementById("overlay").style.visibility = "hidden";
}
function openOverlay(message) {
    document.getElementById("overlay").style.opacity = "1";
    document.getElementById("overlay").style.visibility = "";
    document.getElementById("overlay-text").innerHTML = message;
    setTimeout(() => {
        document.getElementById("closeOverlay").focus();
    }, 50);
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
    fetch(`/addid/${userIdString}/${idInput.value}`)
        .then((result) => {
            return result.text();
        })
        .then((idValid) => {
            var addToGroup = document.getElementById("adgr");
            if (idValid != "notreal") {
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
                addToGroup.setAttribute("data-icon", "done");
                addToGroup.innerHTML = "Added to group";
            } else {
                addToGroup.setAttribute("data-icon", "error");
                addToGroup.innerHTML = "Invalid ID.";
            }
            setTimeout(() => {
                addToGroup.setAttribute("data-icon", "group_add");
                addToGroup.innerHTML = "Add to group";
            }, 1000);
        });
}
function goHome() {
    window.location = "/";
}
function getGroup() {
    if (document.hasFocus()) {
        fetch(`/gids/${userIdString}`)
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
    if (attemptsSoFar == 16) {
        openOverlay(
            "It looks like you've done all of the cards. Make sure you aren't repeating any."
        );
    }
    var cardId = document.getElementById("cardname").value.toUpperCase();
    setTimeout(
        () => {
            fetch(`/cardstatus/${userIdString}/${cardId}`)
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
                            for (var confettiDelay of [10, 510, 1010]) {
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
                            fetch(`/finished/${userIdString}`);
                            break;
                        case "regular":
                            fetch(`/nopecard/${userIdString}/${cardId}`)
                                .then((result) => {
                                    return result.text();
                                })
                                .then((cardId) => {
                                    var cardsNotToVisit = document.getElementById(
                                        "cardsNotToVisit"
                                    );
                                    if (
                                        cardsNotToVisit.innerHTML ==
                                        "[no cards yet]"
                                    ) {
                                        cardsNotToVisit.innerHTML = cardId;
                                    } else {
                                        cardsNotToVisit.innerHTML += ", ";
                                        cardsNotToVisit.innerHTML += cardId;
                                    }
                                    openOverlay(
                                        `This is a normal card. Don't go looking for card ${cardId}.`
                                    );
                                });
                            break;
                        case "invalid_id":
                            openOverlay(
                                "That's an invalid user ID. Try going home to make a new one."
                            );
                            break;
                        case "invalid_card":
                            openOverlay(
                                "That's an invalid card. Cards are A-D and 1-4, so some examples are A1, D4, and B3."
                            );
                            break;
                        default:
                            openOverlay("WTH?" + outcome);
                            break;
                    }
                });
        },
        attemptsSoFar == 16 ? 2000 : 0
    );
}
