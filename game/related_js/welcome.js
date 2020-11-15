function registerUser() {
    var username = document.getElementById("username").value;
    if (username == "") {
        document.getElementById("username").style.animation = "1s jiggle";
        return;
    }
    localStorage.setItem("username", username);
    fetch(`/makeid/${username}`)
        .then((result) => {
            return result.text();
        })
        .then((result) => {
            window.location = result;
        });
}
var sheet = document.createStyleSheet();
if (localStorage.getItem("card") != null) {
    sheet.addRule("#content", "display: none;");
    sheet.addRule("body", "background: var(--primary-color);");
}
