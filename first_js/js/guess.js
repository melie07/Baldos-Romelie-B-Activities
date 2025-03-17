function checkNumber() {
    const guessInput = document.getElementById('guess');
    const message = document.getElementById('message');
    const triesDisplay = document.getElementById('tries');
    const guess = Number(guessInput.value);

    if(tries > 0) {
        if(guess === randomNumber) {
            message.textContent = "Congatsiee! That's Trueee!";
        } else {
            tries--;
            if(guess < randomNumber) {
                message.textContent = "Higher bruhh!";
            }
            triesDisplay.textContent = "Tries: " + tries;

            if(tries === 0) {
                message.textContent = "Game done! The number was" + randomNumber + ".";
            }
        }
    }
    guessInput.value = "";
}