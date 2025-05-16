function checkUser() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let message = document.getElementById("message");

    if (username === "melie" && password === "melie07") {
        message.style.color = "gray";
        message.textContent = "Login successful!";
        setTimeout(() => {
            window.location.href = "inventory.html"; 
        }, 1000);
    } else {
        message.style.color = "red";
        message.textContent = "Invalid username or password";
    }
}
