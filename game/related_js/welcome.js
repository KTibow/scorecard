function registerUser() {
    var usernameElement = document.getElementById("username");
    var username = usernameElement.value;
    if (username.replace(" ", "") == "") {
        usernameElement.classList.remove("jiggle-once");
        usernameElement.classList.add("jiggle-once");
        return;
    }
    localStorage.setItem("username", username);
    fetch(`/api/make_id_for/${username}`)
        .then((result) => {
            return result.text();
        })
        .then((result) => {
            window.location = `/cluecard/${username}`;
        });
}
if (localStorage.getItem("username") != null) {
    var sheet = document.createElement("style");
    sheet.innerHTML = `
#content {
    display: none;
}
#loading {
    display: block;
    background: var(--primary-color);
    width: 50vw;
    height: 50vh;
    margin: 25vh 25vw;
    animation: infinite 1s jiggle;
}
p {
    font-size: 2em;
    transform: translateY(calc(50% - 1em));
    height: 100%;
    color: white;
    text-align: center;
}
html, body {
    margin: 0;
    height: 100%;
}`;
    document.body.appendChild(sheet);
    document.getElementById("username").value = localStorage.getItem(
        "username"
    );
    setTimeout(() => {
        var errorSheet = document.createElement("style");
        errorSheet.innerHTML = `
 #loading {
     filter: hue-rotate(60deg);
 }`;
        document.body.appendChild(errorSheet);
        alert("I'm having trouble logging you in.");
    }, 5000);
    registerUser();
}
