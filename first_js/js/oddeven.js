function oddEven() {
    const inputValue = document.getElementById('oddeven').value;
    const number =parseInt(inputValue);

    if(isNaN(number)) {
        document.getElementById('message').textContent ="please enter a valid number!";
        return;
    }

    if (number % 2 ===0) {
        document.getElementById("messsage").textContent ="even";
    } else {
        document.getElementById("message").textContent ="odd";
    }
}