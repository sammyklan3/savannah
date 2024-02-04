// Function to toggle the dropdown menu and rotate the cog wheel icon
function toggleDropdown() {
  var dropdownMenu = document.getElementById("cog-wheel-dropdown-menu");
  dropdownMenu.classList.toggle("show");

  var cogWheelIcon = document.getElementById("cog-wheel-icon");
  cogWheelIcon.classList.toggle("rotate");
}

// Event listener for the cog wheel click
var cogWheelDropdown = document.getElementById("cog-wheel-dropdown");
cogWheelDropdown.addEventListener("click", toggleDropdown);

function toggleCogAnimation(event) {
  event.preventDefault();
  var cogWheel = event.currentTarget;
  cogWheel.classList.toggle('active');

  if (cogWheel.classList.contains('active')) {
    cogWheel.style.animationDirection = 'normal';
  } else {
    cogWheel.style.animationDirection = 'reverse';
  }
}
