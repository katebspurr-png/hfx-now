<?php
/**
 * Plugin Name: HFX Now — Performance Optimizations
 * Description: Must-use plugin for mobile page speed improvements. Deployed via git.
 * Version: 1.0
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// =============================================================================
// 1. Dequeue Events Calendar scripts/styles on non-events pages
//    Saves ~349 KiB of unused JS/CSS on every non-events page.
// =============================================================================

add_action( 'wp_enqueue_scripts', 'hfxnow_dequeue_tribe_on_non_events_pages', 9999 );

function hfxnow_dequeue_tribe_on_non_events_pages() {

	if ( is_admin() ) {
		return;
	}

	if (
		is_singular( 'tribe_events' )
		|| is_post_type_archive( 'tribe_events' )
		|| is_tax( 'tribe_events_cat' )
		|| is_tax( 'tribe_events_tag' )
		|| ( function_exists( 'tribe_is_event' )       && tribe_is_event() )
		|| ( function_exists( 'tribe_is_events_home' ) && tribe_is_events_home() )
		|| ( function_exists( 'tribe_is_month' )       && tribe_is_month() )
		|| ( function_exists( 'tribe_is_day' )         && tribe_is_day() )
		|| ( function_exists( 'tribe_is_week' )        && tribe_is_week() )
	) {
		return;
	}

	global $wp_scripts, $wp_styles;

	foreach ( $wp_scripts->queue as $handle ) {
		if ( strpos( $handle, 'tribe-' ) === 0 || strpos( $handle, 'tribe_' ) === 0 ) {
			wp_dequeue_script( $handle );
		}
	}

	foreach ( $wp_styles->queue as $handle ) {
		if ( strpos( $handle, 'tribe-' ) === 0 || strpos( $handle, 'tribe_' ) === 0 ) {
			wp_dequeue_style( $handle );
		}
	}
}

// NOTE: font-display: swap via style_loader_src filter is intentionally
// omitted. W3 Total Cache self-hosts Google Fonts under the original URL
// (display=auto). Changing the URL via filter causes W3TC to treat it as an
// uncached resource and make a live blocking HTTP request on every page load,
// which hurts performance. font-display must be fixed in the W3TC-generated
// font CSS file directly instead.
