function checkAge() {
    const age = parseInt(document.getElementById('age').value, 10); 
    let message = "";

    if (age <= 12) {
        message = "Child";
    } else if (age >= 13 && age <= 19) {
        message = "Teen";
    } else if (age >= 20 && age <= 59) {
        message = "Adult";
    } else if (age >= 60) {
        message = "Senior Citizen";
    } else {
        message = "Under age"; 
    }

    document.getElementById('message').innerHTML = message;
    console.log(age);
}
