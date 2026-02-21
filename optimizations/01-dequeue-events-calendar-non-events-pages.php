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
 * ESTIMATED SAVINGS: ~349 KiB unused JavaScript removed from non-events pages
 */

add_action( 'wp_print_scripts', 'hfxnow_dequeue_tribe_on_non_events_pages', 100 );
add_action( 'wp_print_styles',  'hfxnow_dequeue_tribe_on_non_events_pages', 100 );

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

	// Match any script/style whose src URL contains one of these strings.
	// Events Calendar scripts live in plugin directories named 'tribe',
	// 'the-events-calendar', or 'events-calendar-pro'.
	$patterns = [
		'tribe',
		'the-events-calendar',
		'events-calendar-pro',
	];

	global $wp_scripts, $wp_styles;

	foreach ( $wp_scripts->queue as $handle ) {
		$src = isset( $wp_scripts->registered[ $handle ] )
			? $wp_scripts->registered[ $handle ]->src
			: '';
		if ( ! $src ) {
			continue;
		}
		foreach ( $patterns as $pattern ) {
			if ( strpos( $src, $pattern ) !== false ) {
				wp_dequeue_script( $handle );
				break;
			}
		}
	}

	foreach ( $wp_styles->queue as $handle ) {
		$src = isset( $wp_styles->registered[ $handle ] )
			? $wp_styles->registered[ $handle ]->src
			: '';
		if ( ! $src ) {
			continue;
		}
		foreach ( $patterns as $pattern ) {
			if ( strpos( $src, $pattern ) !== false ) {
				wp_dequeue_style( $handle );
				break;
			}
		}
	}
}
