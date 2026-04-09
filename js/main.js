// AI Ally — main.js
// Minimal, no dependencies. Mobile nav, smooth scroll for in-page anchors.

document.addEventListener('DOMContentLoaded', () => {
  // Close mobile nav when a link is clicked
  document.querySelectorAll('.nav-links a').forEach(link => {
    link.addEventListener('click', () => {
      document.body.classList.remove('nav-open');
    });
  });

  // Console signature
  console.log('%cAI Ally', 'color:#0A2540;font:700 24px sans-serif;');
  console.log('%cYour AI Ally. On-site. On day one.', 'color:#FF6B35;font:500 13px sans-serif;');
  console.log('%cWe ship AI specialists into Australian schools and SMEs. Want to join? hello@aially.com.au', 'color:#6B7280;font:13px sans-serif;');
});
