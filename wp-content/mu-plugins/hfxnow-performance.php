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

// =============================================================================
// 2. Add font-display: swap to Google Fonts URLs
//    Only applies when fonts are loaded directly from fonts.googleapis.com
//    (i.e. not self-hosted by a caching plugin like W3 Total Cache).
//    NOTE: Do NOT add preconnect hints here — if a caching plugin self-hosts
//    Google Fonts, preconnecting to fonts.googleapis.com wastes connection
//    slots and hurts mobile performance.
// =============================================================================

add_filter( 'style_loader_src', 'hfxnow_add_font_display_swap', 10, 2 );

function hfxnow_add_font_display_swap( $src, $handle ) {
	if ( strpos( $src, 'fonts.googleapis.com' ) === false ) {
		return $src;
	}
	if ( strpos( $src, 'display=' ) === false ) {
		$src = add_query_arg( 'display', 'swap', $src );
	}
	return $src;
}
