<?php
/**
 * Snippet: Add font-display: swap to all enqueued Google Fonts URLs
 *
 * HOW TO USE:
 * 1. In "Code Snippets" plugin, create a new snippet
 * 2. Paste this entire file's contents
 * 3. Activate
 *
 * WHY: Without font-display: swap, browsers block text rendering while
 * waiting for fonts to download. This causes a flash of invisible text (FOIT).
 * Adding &display=swap tells the browser to show fallback text immediately.
 *
 * ESTIMATED SAVINGS: ~80 ms reduction in render-blocking time
 */

add_filter( 'style_loader_src', 'hfxnow_add_font_display_swap', 10, 2 );

function hfxnow_add_font_display_swap( $src, $handle ) {
	// Only modify Google Fonts URLs
	if ( strpos( $src, 'fonts.googleapis.com' ) === false ) {
		return $src;
	}

	// Add display=swap if not already present
	if ( strpos( $src, 'display=' ) === false ) {
		$src = add_query_arg( 'display', 'swap', $src );
	}

	return $src;
}


/**
 * Also preconnect to Google Fonts domains to speed up the initial connection.
 * This reduces DNS lookup + TLS handshake time.
 */
add_action( 'wp_head', 'hfxnow_preconnect_google_fonts', 1 );

function hfxnow_preconnect_google_fonts() {
	echo '<link rel="preconnect" href="https://fonts.googleapis.com">' . "\n";
	echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
}
