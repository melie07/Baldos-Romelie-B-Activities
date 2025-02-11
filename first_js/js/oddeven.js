function checkOddEven() {
    let numberInput = document.getElementById("numberInput");
    let number = parseInt(numberInput.value);
  
    if (isNaN(number)) {
      alert("Please enter a valid number.");
      return;
    }
  
    let result = "";
    if (number % 2 === 0) {
      result = number + " is even.";
    } else {
      result = number + " is odd.";
    }
  
    let resultDiv = document.getElementById("result");
    resultDiv.textContent = result;
  }