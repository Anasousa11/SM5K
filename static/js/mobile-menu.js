/**
 * Mobile Navigation Component
 * Handles hamburger menu toggle and mobile menu interactions.
 * Automatically closes menu when a link is clicked.
 */

document.addEventListener('DOMContentLoaded', function() {
  const hamburger = document.getElementById('navHamburger');
  const mobileMenu = document.getElementById('navMobileMenu');

  if (hamburger) {
    /**
     * Toggle hamburger menu active state and mobile menu visibility
     */
    hamburger.addEventListener('click', function() {
      hamburger.classList.toggle('active');
      mobileMenu.classList.toggle('active');
    });

    /**
     * Close menu when a navigation link is clicked
     * Improves UX by automatically hiding menu after selection
     */
    const mobileMenuLinks = mobileMenu.querySelectorAll('a');
    mobileMenuLinks.forEach(link => {
      link.addEventListener('click', function() {
        hamburger.classList.remove('active');
        mobileMenu.classList.remove('active');
      });
    });
  }
});
