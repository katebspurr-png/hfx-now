<?php
/**
 * Plugin Name: HFX Now — Performance Optimizations
 * Description: Must-use plugin for mobile page speed improvements. Deployed via git.
 * Version: 1.2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// =============================================================================
// 1. Defer Events Calendar JS (and its dependencies) to remove them from the
//    render-blocking critical path.
//
// Priority 11 (not 10):
//   Tribe's Tribe__Assets_Pipeline class also hooks script_loader_tag at
//   priority 10. It injects extra <script> tags inline:
//     - underscore-before.js and underscore-after.js around the 'underscore' tag
//     - select2-after.js appended after the 'tribe-select2' tag
//   Running at priority 11 means our str_replace runs AFTER those injections,
//   so defer is added to all the extra tags automatically.
//
// Handles covered:
//   tribe-* / tribe_* / tec-*  — tribe's own scripts (V2 views, filter bar, etc.)
//   underscore                  — only used by tribe on the frontend; backbone.min.js
//                                 is absent from the page so Backbone is not loaded
//   jquery-ui-core/mouse/slider/draggable — only tribe uses these on the frontend;
//                                 Elementor uses its own drag system, not jQuery UI
//   jquery-touch-punch           — tribe filter-bar touch events (frontend only)
//   smush-lazy-load              — Smush image lazy-loading, safe to defer anywhere
//
// jQuery itself is intentionally left synchronous. The WPFC combined file
// (dg8ik.js, ~34 KB) likely contains jQuery, and deferring jQuery breaks
// inline $() / jQuery() calls throughout the page.
// =============================================================================

add_filter( 'script_loader_tag', 'hfxnow_defer_noncritical_scripts', 11, 2 );

function hfxnow_defer_noncritical_scripts( $tag, $handle ) {
	if ( is_admin() ) {
		return $tag;
	}

	// Skip scripts with no src (inline).
	if ( strpos( $tag, ' src=' ) === false ) {
		return $tag;
	}

	// Skip if any script in the tag string is already deferred or async
	// (str_replace would otherwise produce duplicate attributes).
	if ( strpos( $tag, ' defer' ) !== false || strpos( $tag, ' async' ) !== false ) {
		return $tag;
	}

	$should_defer =
		strpos( $handle, 'tribe-' ) === 0 ||
		strpos( $handle, 'tribe_' ) === 0 ||
		strpos( $handle, 'tec-' )   === 0 ||
		in_array( $handle, [
			// WordPress-registered underscore — only tribe uses it on the frontend.
			'underscore',
			// jQuery UI components used exclusively by The Events Calendar on the
			// frontend (drag-to-scroll, range slider, touch events).
			'jquery-ui-core',
			'jquery-ui-mouse',
			'jquery-ui-slider',
			'jquery-ui-draggable',
			'jquery-touch-punch',
			// Smush lazy-load — deferred is actually the correct behaviour for
			// a lazy-loader (it should run after the DOM is ready anyway).
			'smush-lazy-load',
		], true );

	if ( ! $should_defer ) {
		return $tag;
	}

	// Replace every <script  opening tag with <script defer — this covers both
	// the handle's own tag and any extra <script> tags injected by tribe's
	// Assets_Pipeline (underscore-before/after, select2-after).
	return str_replace( '<script ', '<script defer ', $tag );
}

// NOTE: font-display: swap via style_loader_src filter is intentionally
// omitted. WP Fastest Cache self-hosts Google Fonts. Changing the URL via
// filter causes WPFC to treat it as an uncached resource and make a live
// blocking HTTP request on every page load. Fix font-display directly in
// the WPFC-generated font CSS file instead.
