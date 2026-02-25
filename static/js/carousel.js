/**
 * Carousel Component
 * Handles automatic rotation of carousel slides with manual indicator controls.
 * Auto-rotates every 6 seconds unless user interacts.
 */

document.addEventListener('DOMContentLoaded', function() {
  const slides = document.querySelectorAll('.carousel-slide');
  const indicators = document.querySelectorAll('.carousel-indicators .indicator');
  let currentSlide = 0;

  /**
   * Display a specific slide by index
   * @param {number} n - The index of the slide to display
   */
  function showSlide(n) {
    slides.forEach(slide => slide.classList.remove('active'));
    indicators.forEach(ind => ind.classList.remove('active'));
    
    slides[n].classList.add('active');
    indicators[n].classList.add('active');
  }

  /**
   * Move to the next slide
   * Cycles back to start when reaching the end
   */
  function nextSlide() {
    currentSlide = (currentSlide + 1) % slides.length;
    showSlide(currentSlide);
  }

  // Auto-rotate carousel every 6 seconds
  setInterval(nextSlide, 6000);

  // Allow manual selection via indicator click
  indicators.forEach((indicator, index) => {
    indicator.addEventListener('click', () => {
      currentSlide = index;
      showSlide(currentSlide);
    });
  });
});
