function checkAge() {
    const age = document.getElementById('age').value;
    let message ="";
   //12 and below ="Child"
   //13 to 19 ="Teen"
   //20 to 59 ="Adult"
   //60 and above ="Senior Citizen"
   if (age <=12) {
    message ="Child";
   } else if (age > 13 && age <= 19) {
    message = "Teen";
   } else if (age >= 20 && age <=59){
    message ="Adult";
   } else if (age >= 60){
    message ="Senior Citizen";
   } else{
    message ="Under age";
   }

   document.getElementById('message').innerHTML = message;
   console.log(age);

}