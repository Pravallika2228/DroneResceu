const loginForm = document.getElementById("loginForm");

const loginMessage = document.getElementById("loginMessage");


loginForm.addEventListener("submit", function (event) {

    event.preventDefault();


    const username =
        document.getElementById("username").value.trim();

    const password =
        document.getElementById("password").value;


    if (!username || !password) {

        loginMessage.textContent =
            "Please enter your login details.";

        return;
    }


    /*
        Temporary navigation.

        Real authentication will be implemented
        later using Flask + secure password hashing.
    */

    window.location.href = "/home";

});