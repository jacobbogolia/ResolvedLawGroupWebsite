document.addEventListener('DOMContentLoaded', function() {
  // Define which sections exist on the index page
  const indexSections = ['practice-areas', 'about', 'team', 'contact'];

  // Check if we're on the index page
  function isIndexPage() {
    const path = window.location.pathname;
    return path.endsWith('index.html') || path.endsWith('/') || path === '';
  }

  // Get the base path to index.html based on current page depth
  function getIndexPath() {
    const path = window.location.pathname;
    // If we're in a subfolder like /blog/, we need ../index.html
    if (path.includes('/blog/')) {
      return '../index.html';
    }
    return 'index.html';
  }

  // Smooth scroll to an element
  function scrollToElement(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  }

  // Handle anchor link clicks
  document.addEventListener('click', function(e) {
    const link = e.target.closest('a');
    if (!link) return;

    const href = link.getAttribute('href');
    if (!href) return;

    // Check if it's a hash-only link (e.g., #contact)
    if (href.startsWith('#')) {
      const targetId = href.substring(1);

      // If we're on the index page and the section exists, smooth scroll
      if (isIndexPage() && indexSections.includes(targetId)) {
        e.preventDefault();
        scrollToElement(targetId);
        history.pushState(null, null, href);
      }
      // If we're NOT on index page but clicking a hash link for an index section
      else if (!isIndexPage() && indexSections.includes(targetId)) {
        e.preventDefault();
        window.location.href = getIndexPath() + href;
      }
    }
    // Check if it's a link to index.html with a hash (e.g., index.html#contact or ../index.html#contact)
    else if (href.includes('index.html#')) {
      const targetId = href.split('#')[1];

      // If we're already on index page, just smooth scroll
      if (isIndexPage()) {
        e.preventDefault();
        scrollToElement(targetId);
        history.pushState(null, null, '#' + targetId);
      }
      // Otherwise let the browser navigate normally (it will scroll on load)
    }
  });

  // On page load, check for hash and scroll to it
  if (window.location.hash) {
    const targetId = window.location.hash.substring(1);
    // Small delay to ensure page is fully rendered
    setTimeout(function() {
      scrollToElement(targetId);
    }, 100);
  }
});
