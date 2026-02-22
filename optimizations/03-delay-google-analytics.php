<?php
/**
 * Snippet: Delay Google Analytics / GTM until user interaction
 *
 * HOW TO USE:
 * 1. In "Code Snippets" plugin, create a new snippet
 * 2. Paste this entire file's contents
 * 3. Activate
 *
 * IMPORTANT: If WP Rocket is active, use its built-in "Delay JavaScript
 * execution" feature instead (see wprocket-settings-guide.md). Only use
 * this snippet if you are NOT using WP Rocket's delay feature.
 *
 * WHY: Google Analytics and GTM are 3rd-party scripts that block the main
 * thread on page load. Delaying them until the first user interaction
 * (scroll, click, keypress) means they don't affect initial page render.
 *
 * NOTE: This will slightly delay analytics data for users who immediately
 * bounce without interacting — an acceptable trade-off for speed.
 */

add_action( 'wp_head', 'hfxnow_delay_gtm_script', 1 );

function hfxnow_delay_gtm_script() {
	// Only run if GTM or GA is not already being handled by WP Rocket delay
	?>
<script>
(function() {
  var fired = false;
  function loadAnalytics() {
    if (fired) return;
    fired = true;

    // Replace GTM-XXXXXXX with your actual GTM container ID
    // OR replace with your GA4 measurement ID (G-XXXXXXXXXX)
    var GTM_ID = 'GTM-XXXXXXX';

    // Load Google Tag Manager
    (function(w,d,s,l,i){
      w[l]=w[l]||[];
      w[l].push({'gtm.start': new Date().getTime(), event:'gtm.js'});
      var f=d.getElementsByTagName(s)[0];
      var j=d.createElement(s);
      var dl=l!='dataLayer'?'&l='+l:'';
      j.async=true;
      j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;
      f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer', GTM_ID);
  }

  // Fire on first user interaction
  ['scroll','click','keydown','touchstart','mousemove'].forEach(function(evt) {
    window.addEventListener(evt, loadAnalytics, { once: true, passive: true });
  });

  // Fallback: load after 5 seconds even with no interaction
  setTimeout(loadAnalytics, 5000);
})();
</script>
	<?php
}
