function registerUser() {
    var url = "/makeid/" + document.getElementById("username").value;
    fetch(url)
        .then((result) => {
            return result.text();
        })
        .then((result) => {
            window.location = result;
        });
}
