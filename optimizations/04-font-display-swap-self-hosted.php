<?php
/**
 * Snippet: Add font-display: swap to self-hosted fonts (e.g. Manrope)
 *
 * HOW TO USE:
 * 1. In "Code Snippets" plugin, create a new snippet
 * 2. Paste this entire file's contents
 * 3. Activate
 *
 * WHY: The Manrope font is self-hosted (served from halifax-now.ca as a .woff2
 * file). Unlike Google Fonts, self-hosted @font-face declarations don't
 * automatically include font-display: swap. Without it, the browser blocks
 * text rendering until the font loads, causing a flash and delaying FCP.
 *
 * This snippet injects a <style> block into <head> that overrides the
 * @font-face rule with font-display: swap, telling the browser to render
 * text immediately using a fallback font while Manrope loads in the background.
 *
 * ESTIMATED SAVINGS: ~50 ms FCP improvement
 */

add_action( 'wp_head', 'hfxnow_font_display_swap_self_hosted', 1 );

function hfxnow_font_display_swap_self_hosted() {
	?>
<style>
/* Force font-display: swap for self-hosted Manrope font */
@font-face {
  font-family: 'Manrope';
  font-display: swap;
}
</style>
	<?php
}
