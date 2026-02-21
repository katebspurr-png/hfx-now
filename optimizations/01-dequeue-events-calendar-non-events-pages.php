<?php
/**
 * Snippet: Dequeue The Events Calendar Pro scripts/styles on non-events pages
 *
 * HOW TO USE:
 * 1. Install the free "Code Snippets" plugin from wordpress.org/plugins/code-snippets/
 * 2. Go to Snippets > Add New
 * 3. Paste this entire file's contents
 * 4. Set "Run snippet everywhere" > save and activate
 *
 * WHY: The Events Calendar Pro loads ~350 KiB of JS/CSS on every page of your
 * site, even pages that have nothing to do with events. This restricts those
 * assets to URLs that start with /events (or contain tribe/calendar routes).
 *
 * ESTIMATED SAVINGS: ~349 KiB unused JavaScript removed from non-events pages
 */

add_action( 'wp_enqueue_scripts', 'hfxnow_dequeue_tribe_on_non_events_pages', 99 );

function hfxnow_dequeue_tribe_on_non_events_pages() {

	// Only run on the front-end, not in admin
	if ( is_admin() ) {
		return;
	}

	// Allow scripts on any events-related page
	if (
		is_singular( 'tribe_events' )       // Single event page
		|| is_post_type_archive( 'tribe_events' ) // Events archive (/events/)
		|| is_tax( 'tribe_events_cat' )     // Event category pages
		|| is_tax( 'tribe_events_tag' )     // Event tag pages
		|| tribe_is_event()                 // Any other Tribe event view
		|| tribe_is_events_home()
		|| tribe_is_month()
		|| tribe_is_day()
		|| tribe_is_week()
	) {
		return; // Leave scripts alone on events pages
	}

	// Dequeue The Events Calendar core scripts
	wp_dequeue_script( 'tribe-events-calendar-script' );
	wp_dequeue_script( 'tribe-events-pro' );
	wp_dequeue_script( 'tribe-events-bar' );
	wp_dequeue_script( 'tribe-events-ajax-handler' );
	wp_dequeue_script( 'tribe-events-ajax-tribe-calendar' );
	wp_dequeue_script( 'tribe-events-ajax-day' );
	wp_dequeue_script( 'tribe-events-ajax-list' );
	wp_dequeue_script( 'tribe-events-ajax-month' );
	wp_dequeue_script( 'tribe-events-views-v2' );
	wp_dequeue_script( 'tribe-common' );
	wp_dequeue_script( 'tribe-events-pro-v2' );

	// Dequeue The Events Calendar core styles
	wp_dequeue_style( 'tribe-events-calendar-style' );
	wp_dequeue_style( 'tribe-events-calendar-pro-style' );
	wp_dequeue_style( 'tribe-events-full' );
	wp_dequeue_style( 'tribe-common-skeleton-style' );
	wp_dequeue_style( 'tribe-common-full-style' );
	wp_dequeue_style( 'tribe-events-v2-full' );
	wp_dequeue_style( 'tribe-events-pro-v2-full' );
}
