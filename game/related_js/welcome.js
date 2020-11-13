function registerUser() {
    var url = "/makeid/" + document.getElementById("username").value;
    fetch(url).then((result) => {result.text().then((result) => {window.location = result})});
}
