var circle = document.querySelector('circle');
var radius = circle.r.baseVal.value;
var circumference = radius * 2 * Math.PI;
circle.style.strokeDasharray = `${circumference} ${circumference}`;
circle.style.strokeDashoffset = `${circumference}`;

function setRemainingBudget(remainder, budget) {
  percent = (remainder / budget) * 100;
  if (percent >= 101){
    percent = 100;
  }
  else if (percent <= -1){
    percent = 0;
  }
  const offset = circumference - percent / 100 * circumference;
  circle.style.strokeDashoffset = offset;
}

window.onload = function() {
  var remaining = document.getElementById("remainder").getAttribute("content");
  var budget = document.getElementById("budget").getAttribute("content");

  setRemainingBudget(remaining, budget);
}






