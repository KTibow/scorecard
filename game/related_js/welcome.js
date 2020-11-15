function registerUser() {
    var username = document.getElementById("username").value;
    if (username == "") {
        document.getElementById("username").style.animation = "1s jiggle";
        return;
    }
    fetch(`/makeid/${username}`)
        .then((result) => {
            return result.text();
        })
        .then((result) => {
            window.location = result;
        });
}
