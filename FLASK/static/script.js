// Get all text boxes
const textBoxes = document.querySelectorAll('.text-box');

// Add event listeners to text boxes
textBoxes.forEach(textBox => {
  textBox.addEventListener('mouseenter', () => {
    // Pause all animations
    pauseAnimations();

    // Add hover-stop-animation class to text box
    textBox.classList.add('hover-stop-animation');
  });

  textBox.addEventListener('mouseleave', () => {
    // Resume all animations
    resumeAnimations();

    // Remove hover-stop-animation class from text box
    textBox.classList.remove('hover-stop-animation');
  });
});

// Pause all animations
function pauseAnimations() {
  const elements = document.getElementsByTagName('*');
  for (let i = 0; i < elements.length; i++) {
    const computedStyles = getComputedStyle(elements[i]);
    if (computedStyles.animationPlayState === 'running') {
      elements[i].style.animationPlayState = 'paused';
    }
  }
}

// Resume all animations
function resumeAnimations() {
  const elements = document.getElementsByTagName('*');
  for (let i = 0; i < elements.length; i++) {
    const computedStyles = getComputedStyle(elements[i]);
    if (computedStyles.animationPlayState === 'paused') {
      elements[i].style.animationPlayState = 'running';
    }
  }
}
