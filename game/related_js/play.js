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
function showPopup(message) {
    var element =
        document.getElementById("notification") ||
        document.createElement("div");
    element.id = "notification";
    element.classList.add("notification");
    element.innerHTML = message;
    document.body.appendChild(element);
}
function registerGroup() {
    var idInput = document.getElementById("userId");
    fetch(`/api/add_ids/${userIdString}/${idInput.value}`)
        .then((result) => {
            return result.text();
        })
        .then((idValid) => {
            var addToGroup = document.getElementById("addToGroup");
            if (idValid != "invalid_id") {
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
function updateStatus() {
    if (document.hasFocus()) {
        fetch(`/api/user_status/${userIdString}`)
            .then((response) => {
                return response.text();
            })
            .then((status) => {
                status = JSON.parse(status);
                if (status["status"] == "bad_id") {
                    showPopup(
                        "Your ID is invalid. I'll try to update it in a bit."
                    );
                    setTimeout(() => {
                        window.location.reload();
                    }, 2500);
                } else if (status["status"] == "not_in_group") {
                    document.getElementById("groupStat").innerHTML =
                        "You're not in a group yet.";
                } else if (status["status"] == "success") {
                    var peopleInGroup = status["result"].sort();
                    peopleInGroup = [
                        peopleInGroup
                            .slice(0, peopleInGroup.length - 1)
                            .join(", "),
                        peopleInGroup[peopleInGroup.length - 1],
                    ];
                    peopleInGroup = peopleInGroup.join(" and ");
                    document.getElementById(
                        "groupStat"
                    ).innerHTML = `Right now you have ${peopleInGroup} in your group.`;
                }
            });
    }
}
setInterval(updateStatus, 400);
function handleClue(outcome, clueId) {
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
                var confettiTempConfig = Object.assign(
                    {
                        origin: {
                            x: Math.random(),
                            y: Math.random() - 0.2,
                        },
                    },
                    confettiConfig
                );
                setTimeout(confetti, confettiDelay, confettiTempConfig);
            }
            fetch(`/api/add_to_finished/${userIdString}`);
            break;
        case "regular":
            fetch(`/api/incorrect_clue_for/${userIdString}/without/${clueId}`)
                .then((result) => {
                    return result.text();
                })
                .then((clueId) => {
                    var cluesNotToVisit = document.getElementById(
                        "cluesNotToVisit"
                    );
                    if (cluesNotToVisit.innerHTML == "") {
                        cluesNotToVisit.innerHTML = `Don't bother visiting ${clueId}.`;
                    } else {
                        cluesNotToVisit.innerHTML = cluesNotToVisit.innerHTML.replace(
                            ".",
                            ""
                        );
                        cluesNotToVisit.innerHTML += `, ${clueId}.`;
                    }
                    openOverlay(
                        `This is a normal clue. Don't go looking for clue ${clueId}.`
                    );
                });
            break;
        case "not_in_group":
            openOverlay("You need to be in a group to check a clue status.");
            break;
        case "invalid_clue":
            openOverlay(
                "That's an invalid clue. Make sure you've selected both the letter and number of the clue."
            );
            break;
        default:
            openOverlay("WTH?" + outcome);
            break;
    }
}
function checkClue() {
    var attemptsElement = document.getElementById("attmpts");
    var attemptsSoFar = Number(attemptsElement.innerHTML) + 1;
    attemptsElement.innerHTML = String(attemptsSoFar);
    if (attemptsSoFar == 16) {
        openOverlay(
            "It looks like you've done all of the clues. Make sure you aren't repeating any."
        );
    }
    var clueId = "";
    var element;
    for (element of document.querySelectorAll("input[type='radio']")) {
        if (element.checked) {
            clueId += element.id.replace("toggle-", "").toUpperCase();
            element.checked = false;
        }
    }
    setTimeout(
        () => {
            fetch(`/api/clue_status_of/${clueId}/for/${userIdString}/`)
                .then((result) => {
                    return result.text();
                })
                .then((outcome) => {
                    handleClue(outcome, clueId);
                });
        },
        attemptsSoFar == 16 ? 2000 : 0
    );
}
