<?php
/**
 * Snippet: Dequeue The Events Calendar Pro scripts/styles on non-events pages
 *
 * HOW TO USE:
 * 1. Install the free "Code Snippets" plugin from wordpress.org/plugins/code-snippets/
 * 2. Go to Snippets > Add New
 * 3. Paste this entire file's contents (without the opening <?php tag)
 * 4. Set "Run snippet everywhere" > save and activate
 * 5. Go to WP Fastest Cache > Delete Cache after activating
 *
 * WHY: The Events Calendar Pro loads ~350 KiB of JS/CSS on every page of your
 * site, even pages that have nothing to do with events. This restricts those
 * assets to URLs that start with /events (or contain tribe/calendar routes).
 *
 * HOW IT WORKS: Events Calendar registers all its own scripts with handles
 * starting with 'tribe-' or 'tribe_'. Matching by handle prefix is safe
 * because it avoids vendor scripts (swiper, selectWoo, tooltipster, etc.)
 * that Events Calendar bundles but other plugins may also depend on.
 *
 * ESTIMATED SAVINGS: ~349 KiB unused JavaScript removed from non-events pages
 */

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
