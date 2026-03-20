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
// 0. Fix Permissions-Policy header & PHP resource limits for 502 prevention
//    - Removes unrecognized 'browsing-topics' feature from Permissions-Policy
//    - Increases PHP memory and execution time to prevent 502 on uploads/AJAX
// =============================================================================

// Send a clean Permissions-Policy header (without browsing-topics)
add_action( 'send_headers', 'hfxnow_fix_permissions_policy', 1 );

function hfxnow_fix_permissions_policy() {
	// Remove any existing Permissions-Policy header (e.g. from hosting provider)
	if ( function_exists( 'header_remove' ) ) {
		header_remove( 'Permissions-Policy' );
	}
	// Set a clean Permissions-Policy without the unrecognized browsing-topics
	header( 'Permissions-Policy: accelerometer=(), camera=(), geolocation=(), gyroscope=(), magnetometer=(), microphone=(), payment=(), usb=()' );
}

// Increase PHP limits to help prevent 502 on admin-ajax.php and async-upload.php
if ( defined( 'DOING_AJAX' ) && DOING_AJAX ) {
	@ini_set( 'memory_limit', '512M' );
	@ini_set( 'max_execution_time', '300' );
}
if ( isset( $_SERVER['REQUEST_URI'] ) && strpos( $_SERVER['REQUEST_URI'], 'async-upload.php' ) !== false ) {
	@ini_set( 'memory_limit', '512M' );
	@ini_set( 'max_execution_time', '300' );
	@ini_set( 'post_max_size', '64M' );
	@ini_set( 'upload_max_filesize', '64M' );
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
