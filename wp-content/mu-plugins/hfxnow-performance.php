<?php
/**
 * Plugin Name: HFX Now — Performance Optimizations
 * Description: Must-use plugin for mobile page speed improvements. Deployed via git.
 * Version: 1.1
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// =============================================================================
// 1. Add defer to Events Calendar JS — removes them from the render-blocking
//    critical path while keeping the calendar fully functional.
//
//    WHY defer instead of dequeue:
//    The Events Calendar uses a custom asset system (StellarWP/tec_asset) that
//    force-enqueues scripts from its shortcode callback, bypassing standard
//    wp_dequeue_script. Dequeuing at wp_enqueue_scripts priority 9999 sets
//    the internal is_enqueued flag to true but removes the script from the WP
//    queue, so the shortcode's force-enqueue sees is_enqueued=true and skips
//    re-adding it — leaving the calendar with no JS at all (broken).
//
//    defer keeps scripts loading for interactivity but moves them off the
//    critical render path. Tribe's V2 views render HTML server-side so their
//    JS is pure progressive enhancement — safe to defer.
//
//    jQuery is intentionally left synchronous (many themes/plugins rely on
//    inline jQuery calls that would break if jQuery were deferred).
// =============================================================================

add_filter( 'script_loader_tag', 'hfxnow_defer_tribe_scripts', 10, 2 );

function hfxnow_defer_tribe_scripts( $tag, $handle ) {
	if ( is_admin() ) {
		return $tag;
	}

	// Only defer tribe scripts.
	if ( strpos( $handle, 'tribe-' ) !== 0 && strpos( $handle, 'tribe_' ) !== 0 ) {
		return $tag;
	}

	// Skip if already has defer or async.
	if ( strpos( $tag, ' defer' ) !== false || strpos( $tag, ' async' ) !== false ) {
		return $tag;
	}

	// Skip inline scripts (no src attribute).
	if ( strpos( $tag, ' src=' ) === false ) {
		return $tag;
	}

	return str_replace( '<script ', '<script defer ', $tag );
}

// NOTE: font-display: swap via style_loader_src filter is intentionally
// omitted. W3 Total Cache self-hosts Google Fonts under the original URL
// (display=auto). Changing the URL via filter causes W3TC to treat it as an
// uncached resource and make a live blocking HTTP request on every page load,
// which hurts performance. font-display must be fixed in the W3TC-generated
// font CSS file directly instead.
