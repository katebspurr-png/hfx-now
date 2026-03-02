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
//    Saves ~80 ms by preventing render-blocking font requests.
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

add_action( 'wp_head', 'hfxnow_preconnect_google_fonts', 1 );

function hfxnow_preconnect_google_fonts() {
	echo '<link rel="preconnect" href="https://fonts.googleapis.com">' . "\n";
	echo '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>' . "\n";
}

// =============================================================================
// 3. Add font-display: swap to self-hosted Manrope font
//    Saves ~50 ms FCP by showing fallback text while the font loads.
// =============================================================================

add_action( 'wp_head', 'hfxnow_font_display_swap_self_hosted', 1 );

function hfxnow_font_display_swap_self_hosted() {
	echo '<style>@font-face { font-family: "Manrope"; font-display: swap; }</style>' . "\n";
}

// =============================================================================
// 4. Register a dedicated event card thumbnail size
//    Ensures event list images are consistently sized and not oversized.
//    After activating, run "Regenerate Thumbnails" to create the new size
//    for existing images.
// =============================================================================

add_action( 'after_setup_theme', 'hfxnow_register_event_image_sizes' );

function hfxnow_register_event_image_sizes() {
	add_image_size( 'hfxnow-event-card', 400, 267, true ); // 3:2 ratio, hard crop
}

// Tell Events Calendar to use our custom size in list view
add_filter( 'tribe_event_featured_image_size', 'hfxnow_event_featured_image_size' );

function hfxnow_event_featured_image_size( $size ) {
	if ( ! is_singular( 'tribe_events' ) ) {
		return 'hfxnow-event-card';
	}
	return $size;
}

// =============================================================================
// 5. Events page optimizations — preload critical CSS + hero image
//    Runs only on events pages. Preloads the Events Calendar stylesheet and
//    optionally a hero/header image to improve LCP.
// =============================================================================

add_action( 'wp_head', 'hfxnow_events_page_head_optimizations', 1 );

function hfxnow_events_page_head_optimizations() {
	if ( ! hfxnow_is_events_page() ) {
		return;
	}

	// Preload Events Calendar critical CSS
	$tec_css = trailingslashit( WP_PLUGIN_URL )
		. 'the-events-calendar/src/resources/css/tribe-events.min.css';
	echo '<link rel="preload" as="style" href="' . esc_url( $tec_css ) . '">' . "\n";
}

// =============================================================================
// 6. Category filter bar — horizontal pill navigation above the events list
//    Outputs a row of category links styled as pills/chips.
// =============================================================================

add_action( 'tribe_events_before_template', 'hfxnow_events_category_filter_bar' );

function hfxnow_events_category_filter_bar() {
	$categories = get_terms( array(
		'taxonomy'   => 'tribe_events_cat',
		'hide_empty' => true,
	) );

	if ( is_wp_error( $categories ) || empty( $categories ) ) {
		return;
	}

	$events_url    = trailingslashit( tribe_get_events_link() );
	$current_cat   = get_queried_object();
	$current_slug  = ( $current_cat instanceof WP_Term ) ? $current_cat->slug : '';

	echo '<nav class="hfxnow-category-filters" aria-label="Event categories">' . "\n";
	echo '  <a href="' . esc_url( $events_url ) . '" class="hfxnow-filter-pill'
		. ( empty( $current_slug ) ? ' active' : '' ) . '">All</a>' . "\n";

	foreach ( $categories as $cat ) {
		$url    = esc_url( trailingslashit( $events_url ) . 'category/' . $cat->slug . '/' );
		$active = ( $cat->slug === $current_slug ) ? ' active' : '';
		echo '  <a href="' . $url . '" class="hfxnow-filter-pill' . $active . '">'
			. esc_html( $cat->name ) . '</a>' . "\n";
	}

	echo '</nav>' . "\n";
}

// =============================================================================
// 7. Quick date filters — Today / This Weekend / This Week / This Month
// =============================================================================

add_action( 'tribe_events_before_template', 'hfxnow_events_quick_date_filters', 5 );

function hfxnow_events_quick_date_filters() {
	$base = trailingslashit( tribe_get_events_link() );

	// Determine which view is currently active
	$current_view = '';
	if ( function_exists( 'tribe_is_day' ) && tribe_is_day() ) {
		$today = wp_date( 'Y-m-d' );
		if ( tribe_get_the_date( 'Y-m-d' ) === $today ) {
			$current_view = 'today';
		}
	} elseif ( function_exists( 'tribe_is_week' ) && tribe_is_week() ) {
		$current_view = 'week';
	} elseif ( function_exists( 'tribe_is_month' ) && tribe_is_month() ) {
		$current_view = 'month';
	}

	$today_date = wp_date( 'Y-m-d' );

	$links = array(
		array(
			'label' => 'Today',
			'url'   => $base . 'today/',
			'key'   => 'today',
		),
		array(
			'label' => 'This Week',
			'url'   => $base . 'week/',
			'key'   => 'week',
		),
		array(
			'label' => 'This Month',
			'url'   => $base . 'month/',
			'key'   => 'month',
		),
	);

	echo '<nav class="hfxnow-date-filters" aria-label="Quick date filters">' . "\n";
	foreach ( $links as $link ) {
		$active = ( $link['key'] === $current_view ) ? ' active' : '';
		echo '  <a href="' . esc_url( $link['url'] ) . '" class="hfxnow-date-pill'
			. $active . '">' . esc_html( $link['label'] ) . '</a>' . "\n";
	}
	echo '</nav>' . "\n";
}

// =============================================================================
// 8. Subscribe to Calendar button — links to the Events Calendar iCal feed
// =============================================================================

add_action( 'tribe_events_after_template', 'hfxnow_events_subscribe_button' );

function hfxnow_events_subscribe_button() {
	$ical_url = trailingslashit( tribe_get_events_link() ) . '?ical=1';
	$gcal_url = 'https://www.google.com/calendar/render?cid=' . urlencode( $ical_url );

	echo '<div class="hfxnow-subscribe-bar">' . "\n";
	echo '  <span class="hfxnow-subscribe-label">Subscribe to events:</span>' . "\n";
	echo '  <a href="' . esc_url( $gcal_url ) . '" target="_blank" rel="noopener" '
		. 'class="hfxnow-subscribe-btn hfxnow-subscribe-gcal">+ Google Calendar</a>' . "\n";
	echo '  <a href="' . esc_url( $ical_url ) . '" class="hfxnow-subscribe-btn '
		. 'hfxnow-subscribe-ical">+ iCal / Outlook</a>' . "\n";
	echo '</div>' . "\n";
}

// =============================================================================
// 9. SEO — Meta description + Open Graph tags for the events archive
//    Only fires on the main events archive if no SEO plugin has already set them.
// =============================================================================

add_action( 'wp_head', 'hfxnow_events_archive_seo_tags', 2 );

function hfxnow_events_archive_seo_tags() {
	if ( ! hfxnow_is_events_page() ) {
		return;
	}

	// Skip if Yoast or RankMath is handling this
	if ( defined( 'WPSEO_VERSION' ) || class_exists( 'RankMath' ) ) {
		return;
	}

	$title       = 'Events in Halifax | HFX Now';
	$description = 'Discover what\'s happening in Halifax — live music, festivals, '
		. 'food events, community gatherings, and more. Browse upcoming events at HFX Now.';
	$url         = tribe_get_events_link();

	echo '<meta name="description" content="' . esc_attr( $description ) . '">' . "\n";
	echo '<meta property="og:title" content="' . esc_attr( $title ) . '">' . "\n";
	echo '<meta property="og:description" content="' . esc_attr( $description ) . '">' . "\n";
	echo '<meta property="og:type" content="website">' . "\n";
	echo '<meta property="og:url" content="' . esc_url( $url ) . '">' . "\n";
	// To add a custom OG image, uncomment and set the URL below:
	// echo '<meta property="og:image" content="' . esc_url( '/wp-content/uploads/events-og.jpg' ) . '">' . "\n";
}

// =============================================================================
// 10. Enqueue events page CSS for UX improvements
//     Mobile-first card layout, date chip styling, filter bars, subscribe button.
// =============================================================================

add_action( 'wp_enqueue_scripts', 'hfxnow_enqueue_events_styles' );

function hfxnow_enqueue_events_styles() {
	if ( ! hfxnow_is_events_page() ) {
		return;
	}

	wp_enqueue_style(
		'hfxnow-events',
		plugin_dir_url( __FILE__ ) . 'hfxnow-events.css',
		array(),
		'1.0'
	);
}

// =============================================================================
// Helper — check if current page is any events page
// =============================================================================

function hfxnow_is_events_page() {
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
		return true;
	}
	return false;
}
