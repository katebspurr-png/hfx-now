<?php
/**
 * Theme bootstrap and event helpers.
 *
 * @package HalifaxNowBroadsheet
 */

if (!defined('ABSPATH')) {
	exit;
}

/**
 * Theme setup.
 */
function hfx_broadsheet_setup() {
	add_theme_support('title-tag');
	add_theme_support('post-thumbnails');
	add_theme_support(
		'html5',
		array(
			'search-form',
			'comment-form',
			'comment-list',
			'gallery',
			'caption',
			'script',
			'style',
		)
	);

	register_nav_menus(
		array(
			'primary' => __('Primary Menu', 'halifax-now-broadsheet'),
		)
	);
}
add_action('after_setup_theme', 'hfx_broadsheet_setup');

/**
 * Display name for event category (Handoff: `category` = slug, `categoryLabel` = title case).
 *
 * @param array<string, mixed> $e Event payload.
 * @return string
 */
function hfx_event_category_label( array $e ) {
	if ( ! empty( $e['categoryLabel'] ) ) {
		return (string) $e['categoryLabel'];
	}
	return isset( $e['category'] ) ? (string) $e['category'] : '';
}

/**
 * Enqueue assets.
 */
function hfx_broadsheet_enqueue_assets() {
	wp_enqueue_style(
		'hfx-broadsheet-fonts',
		'https://fonts.googleapis.com/css2?family=Anton&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&family=Source+Serif+4:ital,wght@0,400;0,700;1,400&family=Space+Grotesk:wght@400;500;700&display=swap',
		array(),
		null
	);

	wp_enqueue_style(
		'hfx-broadsheet-style',
		get_stylesheet_uri(),
		array('hfx-broadsheet-fonts'),
		wp_get_theme()->get('Version')
	);

	wp_enqueue_style(
		'hfx-broadsheet-core',
		get_template_directory_uri() . '/assets/css/broadsheet.css',
		array('hfx-broadsheet-style'),
		wp_get_theme()->get('Version')
	);

	wp_enqueue_script(
		'hfx-broadsheet-ui',
		get_template_directory_uri() . '/assets/js/broadsheet-ui.js',
		array(),
		wp_get_theme()->get('Version'),
		true
	);

	wp_localize_script(
		'hfx-broadsheet-ui',
		'HFXThemeData',
		array(
			'events'    => hfx_get_events_payload(120),
			'now'       => current_time('mysql'),
			'browseUrl' => hfx_events_base_url(),
		)
	);

	if ( is_page_template( 'page-map.php' ) || is_page( 'map' ) ) {
		wp_enqueue_style(
			'hfx-leaflet-css',
			'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',
			array(),
			'1.9.4'
		);
		wp_enqueue_script(
			'hfx-leaflet-js',
			'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
			array(),
			'1.9.4',
			true
		);
	}
}
add_action('wp_enqueue_scripts', 'hfx_broadsheet_enqueue_assets');

/**
 * Canonical listing route.
 *
 * @return string
 */
function hfx_events_base_url() {
	return home_url('/events/');
}

/**
 * Canonicalize event URL to /events/{slug}.
 *
 * @param string $url Raw permalink.
 * @return string
 */
function hfx_canonical_event_url( $url ) {
	$url = is_string( $url ) ? $url : '';
	return str_replace( '/event/', '/events/', $url );
}

/**
 * Canonicalize venue URL to /venues/{slug}.
 *
 * @param string $url Raw permalink.
 * @return string
 */
function hfx_canonical_venue_url( $url ) {
	$url = is_string( $url ) ? $url : '';
	return str_replace( '/venue/', '/venues/', $url );
}

/**
 * Render browse template when slug is requested but WP page mapping is missing.
 *
 * This keeps homepage heat-map links functional in environments where the
 * Browse page has not been created/configured yet.
 */
function hfx_maybe_render_virtual_browse_page() {
	if ( ! is_404() ) {
		return;
	}

	$request_path = isset( $_SERVER['REQUEST_URI'] ) ? (string) wp_unslash( $_SERVER['REQUEST_URI'] ) : '';
	$request_path = (string) parse_url( $request_path, PHP_URL_PATH );
	$request_path = trim( $request_path, '/' );
	$browse_path  = trim( (string) parse_url( home_url( '/browse/' ), PHP_URL_PATH ), '/' );
	$events_path  = trim( (string) parse_url( hfx_events_base_url(), PHP_URL_PATH ), '/' );
	$known_paths = array_filter(array($browse_path, $events_path));

	if ( '' === $request_path || ! in_array( $request_path, $known_paths, true ) ) {
		return;
	}

	$template = locate_template( 'page-browse.php' );
	if ( '' === $template ) {
		return;
	}

	status_header( 200 );
	nocache_headers();
	include $template;
	exit;
}
add_action( 'template_redirect', 'hfx_maybe_render_virtual_browse_page', 0 );

/**
 * Redirect legacy /browse/ route to canonical /events/.
 */
function hfx_redirect_legacy_browse_route() {
	$request_path = isset($_SERVER['REQUEST_URI']) ? (string) wp_unslash($_SERVER['REQUEST_URI']) : '';
	$request_path = (string) parse_url($request_path, PHP_URL_PATH);
	if (trim($request_path, '/') !== 'browse') {
		return;
	}
	$query = isset($_SERVER['QUERY_STRING']) && is_string($_SERVER['QUERY_STRING']) ? trim($_SERVER['QUERY_STRING']) : '';
	$target = hfx_events_base_url();
	if ($query !== '') {
		$target .= '?' . $query;
	}
	wp_safe_redirect($target, 301);
	exit;
}
add_action('template_redirect', 'hfx_redirect_legacy_browse_route', 1);

/**
 * Serve event/venue canonical routes without requiring rewrite flush.
 */
function hfx_maybe_render_virtual_entity_pages() {
	if (!is_404()) {
		return;
	}
	$request_path = isset($_SERVER['REQUEST_URI']) ? (string) wp_unslash($_SERVER['REQUEST_URI']) : '';
	$request_path = trim((string) parse_url($request_path, PHP_URL_PATH), '/');
	$parts = explode('/', $request_path);
	if (count($parts) !== 2) {
		return;
	}
	list($segment, $slug) = $parts;
	$slug = sanitize_title($slug);
	if ($slug === '') {
		return;
	}
	$template = '';
	$post_type = '';
	if ($segment === 'events') {
		$post_type = 'tribe_events';
		$template = locate_template('single-event.php');
	} elseif ($segment === 'venues') {
		$post_type = 'tribe_venue';
		$template = locate_template('single-tribe_venue.php');
	}
	if ($post_type === '' || $template === '') {
		return;
	}
	$entity = get_page_by_path($slug, OBJECT, $post_type);
	if (!$entity instanceof WP_Post) {
		return;
	}
	global $post, $wp_query;
	$post = $entity;
	setup_postdata($post);
	$wp_query->is_404 = false;
	$wp_query->is_singular = true;
	$wp_query->is_single = true;
	$wp_query->queried_object = $post;
	$wp_query->queried_object_id = (int) $post->ID;
	status_header(200);
	nocache_headers();
	include $template;
	wp_reset_postdata();
	exit;
}
add_action('template_redirect', 'hfx_maybe_render_virtual_entity_pages', 2);

/**
 * Handoff §08 — REST: normalized events for headless or external clients.
 */
function hfx_register_rest_routes() {
	register_rest_route(
		'hfx/v1',
		'/events',
		array(
			'methods'             => 'GET',
			'callback'            => 'hfx_rest_serve_events',
			'permission_callback' => '__return_true',
			'args'                => array(
				'per_page' => array(
					'default'         => 100,
					'sanitize_callback' => 'absint',
				),
			),
		)
	);
}
add_action( 'rest_api_init', 'hfx_register_rest_routes' );

/**
 * @param WP_REST_Request $req Request.
 * @return WP_REST_Response
 */
function hfx_rest_serve_events( $req ) {
	$per = (int) $req->get_param( 'per_page' );
	if ( $per < 1 || $per > 500 ) {
		$per = 100;
	}
	$data   = hfx_get_events_payload( $per );
	$resp   = new WP_REST_Response( $data );
	$second = 60;
	$resp->header( 'Cache-Control', 'public, max-age=' . (int) $second );
	return $resp;
}

/**
 * Handle submit form.
 */
function hfx_handle_submit_event_form() {
	if (!isset($_POST['hfx_submit_nonce']) || !wp_verify_nonce(sanitize_text_field(wp_unslash($_POST['hfx_submit_nonce'])), 'hfx_submit_event')) {
		wp_die(esc_html__('Invalid request.', 'halifax-now-broadsheet'));
	}

	$title = isset($_POST['event_title']) ? sanitize_text_field(wp_unslash($_POST['event_title'])) : '';
	$venue = isset($_POST['event_venue']) ? sanitize_text_field(wp_unslash($_POST['event_venue'])) : '';
	$date  = isset($_POST['event_date']) ? sanitize_text_field(wp_unslash($_POST['event_date'])) : '';
	$time  = isset($_POST['event_time']) ? sanitize_text_field(wp_unslash($_POST['event_time'])) : '';
	$price = isset($_POST['event_price']) ? sanitize_text_field(wp_unslash($_POST['event_price'])) : '';
	$blurb = isset($_POST['event_blurb']) ? sanitize_textarea_field(wp_unslash($_POST['event_blurb'])) : '';
	$contact = isset($_POST['event_contact']) ? sanitize_text_field(wp_unslash($_POST['event_contact'])) : '';
	$category = isset($_POST['event_category']) ? sanitize_title(wp_unslash($_POST['event_category'])) : '';
	$hood = isset($_POST['event_neighbourhood']) ? sanitize_text_field(wp_unslash($_POST['event_neighbourhood'])) : '';
	$moods = isset($_POST['event_moods']) && is_array($_POST['event_moods']) ? array_map('sanitize_title', array_map('wp_unslash', $_POST['event_moods'])) : array();

	$admin_email = get_option('admin_email');
	$subject     = sprintf(__('New Event Submission: %s', 'halifax-now-broadsheet'), $title);
	$message     = sprintf(
		"Title: %s\nVenue: %s\nDate: %s\nTime: %s\nPrice: %s\nCategory: %s\nNeighbourhood: %s\nMoods: %s\nContact: %s\n\nDetails:\n%s",
		$title,
		$venue,
		$date,
		$time,
		$price,
		$category,
		$hood,
		implode(', ', $moods),
		$contact,
		$blurb
	);

	$post_type = post_type_exists('tribe_events') ? 'tribe_events' : 'post';
	$new_post_id = wp_insert_post(
		array(
			'post_type' => $post_type,
			'post_status' => 'pending',
			'post_title' => $title,
			'post_content' => $blurb,
			'post_excerpt' => hfx_event_str_clip($blurb, 140),
		),
		true
	);
	if (!is_wp_error($new_post_id) && $new_post_id > 0) {
		update_post_meta($new_post_id, 'hfx_neighbourhood', $hood);
		update_post_meta($new_post_id, 'hfx_moods', $moods);
		update_post_meta($new_post_id, 'hfx_short_blurb', hfx_event_str_clip($blurb, 90));
		update_post_meta($new_post_id, 'hfx_editor_blurb', $blurb);
		update_post_meta($new_post_id, '_hfx_submit_contact', $contact);
		update_post_meta($new_post_id, '_hfx_submit_venue_name', $venue);
		if ($date !== '') {
			$start = trim($date . ' ' . ($time !== '' ? $time : '00:00') . ':00');
			update_post_meta($new_post_id, '_EventStartDate', $start);
			update_post_meta($new_post_id, '_EventEndDate', $start);
		}
		if ($price !== '') {
			update_post_meta($new_post_id, '_EventCost', $price);
		}
		if ($category !== '' && taxonomy_exists('tribe_events_cat')) {
			wp_set_object_terms($new_post_id, array($category), 'tribe_events_cat', false);
		}
	}

	wp_mail($admin_email, $subject, $message);

	$redirect_url = add_query_arg('submitted', '1', wp_get_referer() ? wp_get_referer() : home_url('/submit/'));
	wp_safe_redirect($redirect_url);
	exit;
}
add_action('admin_post_hfx_submit_event', 'hfx_handle_submit_event_form');
add_action('admin_post_nopriv_hfx_submit_event', 'hfx_handle_submit_event_form');

/**
 * Get raw event posts.
 *
 * @param int $limit Post limit.
 * @return WP_Post[]
 */
function hfx_get_event_posts($limit = 100) {
	$post_types = array('post');
	if (post_type_exists('tribe_events')) {
		$post_types = array('tribe_events');
	}

	$query_args = array(
		'post_type'      => $post_types,
		'post_status'    => 'publish',
		'posts_per_page' => $limit,
		'orderby'        => 'date',
		'order'          => 'DESC',
		'no_found_rows'  => true,
	);

	$posts = get_posts($query_args);
	return is_array($posts) ? $posts : array();
}

/**
 * ACF or raw post meta (ACF first when available).
 *
 * @param int    $post_id Post ID.
 * @param string $key     Field / meta key.
 * @return mixed
 */
function hfx_get_event_field($post_id, $key) {
	$post_id = (int) $post_id;
	if (function_exists('get_field')) {
		$acf = get_field($key, $post_id);
		if (null !== $acf && false !== $acf && '' !== $acf) {
			return $acf;
		}
	}
	$meta = get_post_meta($post_id, $key, true);
	return (null === $meta || false === $meta) ? null : $meta;
}

/**
 * @param string $str Raw text.
 * @param int    $len Max length.
 * @return string
 */
function hfx_event_str_clip($str, $len = 90) {
	$s   = (string) wp_strip_all_tags((string) $str);
	$len = (int) $len;
	if (function_exists('mb_strlen') && function_exists('mb_substr') && (int) mb_strlen($s) > $len) {
		return (string) mb_substr($s, 0, $len) . '…';
	}
	if (strlen($s) > $len) {
		return substr($s, 0, $len) . '…';
	}
	return $s;
}

/**
 * @param string $text HTML or text.
 * @return string
 */
function hfx_event_first_sentence($text) {
	$t = trim((string) wp_strip_all_tags((string) $text));
	if ($t === '') {
		return '';
	}
	// phpcs:ignore WordPress.PHP -- mb regex for first sentence
	if (preg_match('/^(.+?[.!?](?:\s|\'|$))/', $t, $m)) {
		return trim($m[1]);
	}
	return $t;
}

/**
 * ECP: detect recurring (Pro) — best effort across TEC versions.
 *
 * @param int $post_id Post ID.
 * @return bool
 */
function hfx_event_is_recurring($post_id) {
	$post_id = (int) $post_id;
	if (function_exists('tribe_is_recurring_event') && post_type_exists('tribe_events')) {
		return (bool) tribe_is_recurring_event($post_id);
	}
	$ser = (string) get_post_meta($post_id, '_EventRecurrence', true);
	if (in_array($ser, array('', '0', 'a:0:{}', 'N;'), true)) {
		$rr = get_post_meta($post_id, '_tribe_ea_recurrence_id', true);
		return (bool) $rr;
	}
	if ('a:0:{}' === $ser) {
		return (bool) get_post_meta($post_id, '_tribe_ea_recurrence_id', true);
	}
	return (bool) $ser;
}

/**
 * Human-readable recurrence line for API / detail (Handoff §08 `recurring` string).
 *
 * @param int  $post_id     Post ID.
 * @param bool $is_recurring From hfx_event_is_recurring().
 * @return string
 */
function hfx_event_recurring_label( $post_id, $is_recurring ) {
	if ( ! $is_recurring ) {
		return '';
	}
	$post_id = (int) $post_id;
	$custom  = (string) get_post_meta( $post_id, '_hfx_recurring_label', true );
	if ( $custom !== '' ) {
		return $custom;
	}
	return apply_filters( 'hfx_recurring_event_label', __( 'Recurring event', 'halifax-now-broadsheet' ), $post_id );
}

/**
 * Parse TEC datetime meta to a Unix timestamp.
 *
 * @param int              $post_id   Post ID.
 * @param array<int,string> $meta_keys Ordered candidate meta keys.
 * @return int|null
 */
function hfx_event_meta_timestamp( $post_id, $meta_keys ) {
	$post_id = (int) $post_id;
	foreach ( $meta_keys as $key ) {
		$raw = (string) get_post_meta( $post_id, (string) $key, true );
		if ( '' === trim( $raw ) ) {
			continue;
		}
		$raw = html_entity_decode( wp_strip_all_tags( $raw ), ENT_QUOTES | ENT_HTML5, 'UTF-8' );
		$raw = preg_replace( '/\s+/', ' ', trim( $raw ) );
		if ( ! is_string( $raw ) || '' === $raw ) {
			continue;
		}

		$ts = strtotime( $raw );
		if ( false !== $ts ) {
			return (int) $ts;
		}

		if ( preg_match( '/^\d{4}-\d{2}-\d{2}$/', $raw ) ) {
			$ts = strtotime( $raw . ' 00:00:00' );
			if ( false !== $ts ) {
				return (int) $ts;
			}
		}

		if ( preg_match( '/^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2})(:\d{2})?$/', $raw, $m ) ) {
			$norm = $m[1] . ' ' . $m[2] . ( isset( $m[3] ) ? $m[3] : ':00' );
			$ts   = strtotime( $norm );
			if ( false !== $ts ) {
				return (int) $ts;
			}
		}
	}
	return null;
}

/**
 * Validate strict YYYY-MM-DD date format.
 *
 * @param string $value Date candidate.
 * @return bool
 */
function hfx_is_valid_event_date( $value ) {
	$value = is_string( $value ) ? trim( $value ) : '';
	if ( '' === $value || 1 !== preg_match( '/^\d{4}-\d{2}-\d{2}$/', $value ) ) {
		return false;
	}
	$dt = DateTimeImmutable::createFromFormat( '!Y-m-d', $value, wp_timezone() );
	return ( $dt instanceof DateTimeImmutable ) && $dt->format( 'Y-m-d' ) === $value;
}

/**
 * Reject epoch-like / implausible dates in payload.
 *
 * @param string $value Date candidate.
 * @return bool
 */
function hfx_is_plausible_event_date( $value ) {
	if ( ! hfx_is_valid_event_date( $value ) ) {
		return false;
	}
	$year = (int) substr( (string) $value, 0, 4 );
	return $year >= 2000 && $year <= 2100;
}

/**
 * Validate strict HH:MM time format.
 *
 * @param string $value Time candidate.
 * @return bool
 */
function hfx_is_valid_event_time( $value ) {
	$value = is_string( $value ) ? trim( $value ) : '';
	if ( '' === $value || 1 !== preg_match( '/^\d{2}:\d{2}$/', $value ) ) {
		return false;
	}
	$dt = DateTimeImmutable::createFromFormat( 'H:i', $value, wp_timezone() );
	return ( $dt instanceof DateTimeImmutable ) && $dt->format( 'H:i' ) === $value;
}

/**
 * Build sortable date-time key for event payload rows.
 *
 * Undated rows are placed at the end.
 *
 * @param array<string, mixed> $event Event payload row.
 * @return string
 */
function hfx_event_sort_key( $event ) {
	$date = isset( $event['date'] ) ? trim( (string) $event['date'] ) : '';
	$time = isset( $event['time'] ) ? trim( (string) $event['time'] ) : '';
	if ( ! hfx_is_valid_event_date( $date ) ) {
		return '9999-99-99 99:99';
	}
	if ( ! hfx_is_valid_event_time( $time ) ) {
		$time = '23:59';
	}
	return $date . ' ' . $time;
}

/**
 * Category hue map shared across selection and rendering.
 *
 * @return array<string, int>
 */
function hfx_event_category_hue_map() {
	return array(
		'music'            => 220,
		'live-music'       => 220,
		'comedy'           => 14,
		'arts'             => 280,
		'arts-culture'     => 280,
		'arts-and-culture' => 280,
		'food'             => 40,
		'food-drink'       => 40,
		'outdoors'         => 140,
		'film'             => 20,
		'theatre'          => 340,
		'community'        => 120,
		'sports'           => 0,
		'family'           => 190,
		'nightlife'        => 300,
		'market'           => 90,
		'markets'          => 90,
	);
}

/**
 * Detect generic category slugs that collapse color variety.
 *
 * @param string $slug Category slug.
 * @return bool
 */
function hfx_event_is_generic_category_slug( $slug ) {
	$slug = sanitize_title( (string) $slug );
	if ( '' === $slug ) {
		return true;
	}
	$generic = array(
		'events',
		'event',
		'all-events',
		'general',
		'misc',
		'miscellaneous',
		'other',
		'uncategorized',
	);
	return in_array( $slug, $generic, true );
}

/**
 * Priority score for choosing the most informative category term.
 *
 * Higher score wins.
 *
 * @param string $slug Category slug.
 * @return int
 */
function hfx_event_category_priority( $slug ) {
	$slug = sanitize_title( (string) $slug );
	$priority = array(
		'live-music'       => 90,
		'music'            => 90,
		'comedy'           => 88,
		'theatre'          => 86,
		'film'             => 84,
		'food-drink'       => 82,
		'food'             => 82,
		'outdoors'         => 80,
		'community'        => 78,
		'sports'           => 76,
		'family'           => 74,
		'nightlife'        => 72,
		'market'           => 70,
		'markets'          => 70,
		'arts-and-culture' => 20,
		'arts-culture'     => 20,
		'arts'             => 20,
		'events'           => 10,
		'event'            => 10,
	);
	return (int) ( $priority[ $slug ] ?? 50 );
}

/**
 * Choose the best category term for display and color seeding.
 *
 * @param array<int, WP_Term|object> $terms Candidate terms.
 * @return array{label: string, slug: string}
 */
function hfx_pick_event_category_term( $terms ) {
	$empty = array(
		'label' => '',
		'slug'  => '',
	);
	if ( ! is_array( $terms ) || empty( $terms ) ) {
		return $empty;
	}

	$candidates = array();
	foreach ( $terms as $term ) {
		$label = '';
		$slug  = '';
		if ( is_object( $term ) ) {
			if ( isset( $term->name ) && is_string( $term->name ) ) {
				$label = trim( $term->name );
			}
			if ( isset( $term->slug ) && is_string( $term->slug ) ) {
				$slug = sanitize_title( $term->slug );
			}
		}
		if ( '' === $slug && '' !== $label ) {
			$slug = sanitize_title( $label );
		}
		if ( '' === $slug && '' === $label ) {
			continue;
		}
		$candidates[] = array(
			'label' => $label,
			'slug'  => $slug,
		);
	}

	if ( empty( $candidates ) ) {
		return $empty;
	}

	$hue_map = hfx_event_category_hue_map();
	$best    = null;
	$best_score = -100000;
	foreach ( $candidates as $candidate ) {
		$slug = (string) $candidate['slug'];
		$score = hfx_event_category_priority( $slug );
		if ( isset( $hue_map[ $slug ] ) ) {
			$score += 20;
		}
		if ( hfx_event_is_generic_category_slug( $slug ) ) {
			$score -= 30;
		}
		if ( $score > $best_score ) {
			$best_score = $score;
			$best = $candidate;
		}
	}
	if ( is_array( $best ) ) {
		return $best;
	}
	return $candidates[0];
}

/**
 * Apply deterministic hue variation so repeated categories do not collapse visually.
 *
 * @param int    $hue  Base hue.
 * @param string $seed Stable event seed.
 * @return int Degrees 0–359.
 */
function hfx_event_apply_hue_variation( $hue, $seed = '' ) {
	$base_hue = (int) $hue;
	$base_hue = ( ( $base_hue % 360 ) + 360 ) % 360;
	$seed     = is_string( $seed ) ? trim( $seed ) : '';
	if ( '' === $seed ) {
		return $base_hue;
	}

	// Offset in roughly [-24, +24] degrees for controlled palette spread.
	$byte   = hexdec( substr( md5( 'hfx-hue|' . $seed ), 0, 2 ) );
	$offset = (int) round( ( ( $byte / 255 ) * 48 ) - 24 );
	return ( $base_hue + $offset + 360 ) % 360;
}

/**
 * Best-effort latitude/longitude for an event.
 *
 * @param int $post_id Event post ID.
 * @param int $venue_id Venue post ID.
 * @return array{lat: float|null, lng: float|null}
 */
function hfx_event_lat_lng( $post_id, $venue_id = 0 ) {
	$post_id = (int) $post_id;
	$venue_id = (int) $venue_id;
	$lat = null;
	$lng = null;
	$candidates = array_filter(array($post_id, $venue_id));
	foreach ($candidates as $id) {
		$maybe_lat = get_post_meta((int) $id, '_VenueLat', true);
		$maybe_lng = get_post_meta((int) $id, '_VenueLng', true);
		if ($maybe_lat === '' || $maybe_lat === null) {
			$maybe_lat = get_post_meta((int) $id, '_EventLatitude', true);
		}
		if ($maybe_lng === '' || $maybe_lng === null) {
			$maybe_lng = get_post_meta((int) $id, '_EventLongitude', true);
		}
		if (is_numeric($maybe_lat) && is_numeric($maybe_lng)) {
			$lat = (float) $maybe_lat;
			$lng = (float) $maybe_lng;
			break;
		}
	}
	if ($lat === null && function_exists('tribe_get_coordinates')) {
		$coords = tribe_get_coordinates($post_id);
		if (is_array($coords) && isset($coords['lat'], $coords['lng']) && is_numeric($coords['lat']) && is_numeric($coords['lng'])) {
			$lat = (float) $coords['lat'];
			$lng = (float) $coords['lng'];
		}
	}
	if ($lat === null || $lng === null) {
		return array('lat' => null, 'lng' => null);
	}
	if ($lat < -90 || $lat > 90 || $lng < -180 || $lng > 180) {
		return array('lat' => null, 'lng' => null);
	}
	return array('lat' => $lat, 'lng' => $lng);
}

/**
 * Convert event post to frontend payload (aligns with Halifax ECP spec / JSON contract).
 *
 * @param int $post_id Post ID.
 * @return array<string, mixed>
 */
function hfx_event_to_payload($post_id) {
	$post_id = (int) $post_id;
	$title   = get_the_title($post_id);
	$link    = hfx_canonical_event_url((string) get_permalink($post_id));

	$category     = '';
	$category_slug = '';
	$terms         = get_the_terms($post_id, 'tribe_events_cat');
	if (!is_array($terms) || empty($terms)) {
		$terms = get_the_terms($post_id, 'category');
	}
	if (is_array($terms) && !empty($terms)) {
		$chosen        = hfx_pick_event_category_term( $terms );
		$category      = (string) $chosen['label'];
		$category_slug = (string) $chosen['slug'];
	}

	$venue   = get_post_meta($post_id, '_EventVenueID', true);
	$venue_n = '';
	if (!empty($venue)) {
		$venue_n = get_the_title((int) $venue);
	}
	if (!$venue_n && function_exists('tribe_get_venue')) {
		$venue_n = tribe_get_venue($post_id);
	}
	if (!$venue_n) {
		$venue_meta_keys = array(
			'Event Venue Name',
			'EVENT VENUE NAME',
			'event_venue_name',
			'_EventVenue',
			'_Venue',
		);
		foreach ($venue_meta_keys as $mk) {
			$candidate = trim((string) get_post_meta($post_id, $mk, true));
			if ('' !== $candidate) {
				$venue_n = $candidate;
				break;
			}
		}
	}
	$coords = hfx_event_lat_lng($post_id, (int) $venue);

	$address = get_post_meta($post_id, '_EventVenueAddress', true);
	$city    = get_post_meta($post_id, '_EventVenueCity', true);
	$hood    = $city ? $city : __('Halifax', 'halifax-now-broadsheet');

	$hood_acf = hfx_get_event_field($post_id, 'hfx_neighbourhood');
	if (is_string($hood_acf) && '' !== trim($hood_acf)) {
		$hood = trim($hood_acf);
	}

	$time     = '';
	$end_time = '';
	$date     = '';
	$post_type = get_post_type( $post_id );
	$start_ts = hfx_event_meta_timestamp( $post_id, array( '_EventStartDate', '_EventStartDateUTC' ) );
	if ( null !== $start_ts ) {
		$date = function_exists( 'wp_date' ) ? wp_date( 'Y-m-d', $start_ts, wp_timezone() ) : gmdate( 'Y-m-d', $start_ts );
		$time = function_exists( 'wp_date' ) ? wp_date( 'H:i', $start_ts, wp_timezone() ) : gmdate( 'H:i', $start_ts );
	} elseif ( 'tribe_events' !== $post_type ) {
		$date = get_post_time( 'Y-m-d', false, $post_id );
		$time = get_post_time( 'H:i', false, $post_id );
	}
	$end_ts = hfx_event_meta_timestamp( $post_id, array( '_EventEndDate', '_EventEndDateUTC' ) );
	if ( null !== $end_ts ) {
		$end_time = function_exists( 'wp_date' ) ? wp_date( 'H:i', $end_ts, wp_timezone() ) : gmdate( 'H:i', $end_ts );
	}

	// Guardrails: malformed source values must not appear as valid schedule data.
	if ( ! hfx_is_plausible_event_date( (string) $date ) ) {
		$date = '';
	}
	if ( ! hfx_is_valid_event_time( (string) $time ) ) {
		$time = '';
	}
	if ( ! hfx_is_valid_event_time( (string) $end_time ) ) {
		$end_time = '';
	}
	if ($date === '') {
		$time = '';
		$end_time = '';
	}

	$price = '';
	if (function_exists('tribe_get_cost')) {
		$price = (string) tribe_get_cost($post_id, true);
	}
	$price = trim($price);
	if ($price === '') {
		$cost_meta_keys = array(
			'_EventCost',   // TEC canonical
			'Event Cost',   // CSV/header variants
			'EVENT COST',   // scraper raw header variant
			'event_cost',
		);
		foreach ( $cost_meta_keys as $mk ) {
			$candidate = trim( (string) get_post_meta( $post_id, $mk, true ) );
			if ( '' !== $candidate ) {
				$price = $candidate;
				break;
			}
		}
	}

	$is_pick = false;
	$cpick   = hfx_get_event_field($post_id, 'hfx_critic_pick');
	if (null !== $cpick && false !== $cpick && '' !== $cpick) {
		if (is_bool($cpick)) {
			$is_pick = $cpick;
		} elseif (is_string($cpick)) {
			$is_pick = in_array(strtolower(trim($cpick)), array('1', 'true', 'yes', 'on'), true);
		} else {
			$is_pick = (bool) (int) $cpick;
		}
	} else {
		$is_pick = (bool) get_post_meta($post_id, '_hfx_critic_pick', true);
	}
	if (!$is_pick) {
		$is_pick = has_term('critics-pick', 'post_tag', $post_id);
	}

	$thumb = get_the_post_thumbnail_url($post_id, 'large');
	if (!$thumb) {
		$thumb = '';
	}

	$cat_label = $category ? $category : __( 'Events', 'halifax-now-broadsheet' );
	$cat_key   = $category_slug ? (string) $category_slug : ( $category ? sanitize_title( (string) $category ) : 'events' );
	$hue_base  = hfx_event_category_hue( $cat_key, $cat_label, (string) $post_id );
	$hue       = hfx_event_apply_hue_variation( $hue_base, (string) $post_id );
	$short_acf  = hfx_get_event_field($post_id, 'hfx_short_blurb');
	$excerpt_p  = (string) get_post_field('post_excerpt', $post_id);
	$excerpt    = get_the_excerpt($post_id);
	$excerpt    = ( null !== $excerpt && false !== $excerpt ) ? (string) $excerpt : $excerpt_p;
	if (is_string($short_acf) && '' !== trim($short_acf)) {
		$short = hfx_event_str_clip(wp_strip_all_tags($short_acf), 90);
	} else {
		$short = wp_trim_words(wp_strip_all_tags('' === $excerpt ? $excerpt_p : $excerpt), 18, '…');
	}
	if ('' === trim((string) $short) && '' === $excerpt_p && (string) get_post_field('post_content', $post_id) !== '') {
		$first = hfx_event_first_sentence(get_post_field('post_content', $post_id));
		$short = $first ? hfx_event_str_clip($first, 90) : (string) $short;
	}
	$editor_blurb = hfx_get_event_field($post_id, 'hfx_editor_blurb');
	$blurb_src    = (is_string($editor_blurb) && '' !== trim($editor_blurb)) ? $editor_blurb : get_post_field('post_content', $post_id);
	$blurb        = wp_trim_words(wp_strip_all_tags((string) $blurb_src), 34);

	$mood_raw = hfx_get_event_field($post_id, 'hfx_moods');
	$moods    = array();
	if (is_array($mood_raw)) {
		$moods = array_values(array_map('strval', $mood_raw));
	} elseif (is_string($mood_raw) && $mood_raw !== '') {
		$moods = array_map('trim', explode(',', $mood_raw));
	}

	$ticket_url = (string) get_post_meta($post_id, '_EventURL', true);
	$ticket_url = esc_url_raw($ticket_url) ? $ticket_url : '';

	$organizer = '';
	$oid       = (int) get_post_meta($post_id, '_EventOrganizerID', true);
	if (function_exists('tribe_get_organizer_id')) {
		$toid = (int) tribe_get_organizer_id($post_id);
		$oid  = $toid > 0 ? $toid : $oid;
	}
	if ($oid) {
		$ot = get_the_title($oid);
		$organizer = ( is_string( $ot ) && '' !== trim( $ot ) ) ? trim( $ot ) : '';
	}

	$is_recurring  = hfx_event_is_recurring( $post_id );
	$recur_label  = hfx_event_recurring_label( $post_id, $is_recurring );

	$dc         = (string) $price;
	$free_label = __( 'Free', 'halifax-now-broadsheet' );
	if ( '' === trim( $dc ) ) {
		$is_free     = true;
		$price_label = $free_label;
	} elseif ( 0 === stripos( strtolower( $dc ), 'free' ) || preg_match( '/^[\s$]*0(?:[.,]00)?\s*$/', $dc ) ) {
		$is_free     = true;
		$price_label = ( '' === trim( $dc ) ) ? $free_label : $dc;
	} else {
		$is_free     = false;
		$price_label = $dc;
	}

	$out = array(
		'id'             => $post_id,
		'title'          => $title,
		'url'            => $link,
		'venue'          => $venue_n ? $venue_n : __( 'Venue TBA', 'halifax-now-broadsheet' ),
		'address'        => $address ? $address : '',
		'hood'           => $hood,
		// §08 data contract: `category` is tribe_events_cat slug; label for display separately.
		'category'       => $cat_key,
		'categoryLabel'  => $cat_label,
		'categorySlug'   => $cat_key,
		'hue'            => $hue,
		'date'           => $date,
		'time'           => $time,
		'endTime'        => $end_time,
		'priceLabel'     => $price_label,
		'price'          => $is_free ? 'free' : 'paid',
		'pick'           => $is_pick,
		'critic'         => $is_pick,
		'isRecurring'    => $is_recurring,
		'recurring'      => $recur_label,
		'image'          => $thumb,
		'short'          => (string) $short,
		'blurb'          => (string) $blurb,
		'mood'           => $moods,
		'organizer'      => $organizer,
		'ticketUrl'      => $ticket_url,
		'lat'            => $coords['lat'],
		'lng'            => $coords['lng'],
	);

	return $out;
}

/**
 * Category slug → OKLCH hue (Halifax ECP spec §04). Unknown slugs get a stable hash fallback.
 *
 * @param string $slug   Primary `tribe_events_cat` term slug.
 * @param string $label  Term name (used when slug is empty or unmapped).
 * @param string $seed   Deterministic seed for generic fallback variation.
 * @return int Degrees 0–359.
 */
function hfx_event_category_hue($slug, $label = '', $seed = '') {
	$map = hfx_event_category_hue_map();
	$try = array();
	if (is_string($slug) && '' !== trim($slug)) {
		$try[] = sanitize_title($slug);
		$try[] = strtolower($slug);
	}
	if (is_string($label) && '' !== trim($label)) {
		$try[] = sanitize_title($label);
		$try[] = strtolower(sanitize_title($label));
	}
	$try = array_unique(array_filter($try));
	foreach ($try as $k) {
		$k = (string) $k;
		if (isset($map[ $k ])) {
			return (int) $map[ $k ];
		}
	}
	$base = (string) ( $try[0] ?? ( is_string( $label ) ? $label : 'events' ) );
	$base = $base !== '' ? $base : 'events';
	if ( hfx_event_is_generic_category_slug( $base ) && '' !== trim( (string) $seed ) ) {
		$base .= '|' . trim( (string) $seed );
	}
	return (int) (hexdec( substr( md5( $base ), 0, 6) ) % 360);
}

/**
 * Markup: background image, grayscale/ contrast / brightness, category tint, dot screen.
 *
 * @param string   $image_url   Featured image URL or empty.
 * @param string   $category    Primary category label (fallback for hue if $hue is null).
 * @param string   $alt         Accessible name (e.g. event title).
 * @param string   $classes     Extra container classes.
 * @param int|null $hue_degrees If set, overrides category hue (0–359).
 * @return string
 */
function hfx_event_image_html( $image_url, $category, $alt, $classes = '', $hue_degrees = null ) {
	$hue   = ( null === $hue_degrees ) ? hfx_event_category_hue( '', (string) $category ) : ( (int) $hue_degrees );
	$extra = $classes;
	$has_image = is_string($image_url) && $image_url !== '';
	if (!$has_image) {
		$extra = trim($extra . ' hfx-event-img--empty hfx-img-fallback');
	}
	$class = trim('hfx-event-img ' . $extra);
	$label = $alt;
	$style = '--hfx-cat-hue: ' . (int) $hue . 'deg;';

	ob_start();
	?>
	<div
		class="<?php echo esc_attr($class); ?>"
		style="<?php echo esc_attr($style); ?>"
		role="img"
		aria-label="<?php echo esc_attr($label); ?>"
	>
		<?php if ($has_image) : ?>
			<div class="hfx-event-img__bg" style="background-image: url(<?php echo esc_url($image_url); ?>);"></div>
		<?php else : ?>
			<div class="hfx-event-img__bg" aria-hidden="true"></div>
		<?php endif; ?>
		<div class="hfx-event-img__tint" aria-hidden="true"></div>
		<div class="hfx-event-img__dots" aria-hidden="true"></div>
	</div>
	<?php
	return (string) ob_get_clean();
}

/**
 * Echo event image block.
 *
 * @param string $image_url URL.
 * @param string $category  Category.
 * @param string $alt       Label.
 * @param string $classes   Classes.
 */
function hfx_event_image_e($image_url, $category, $alt, $classes = '', $hue_degrees = null) {
	// phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- escaped in helper.
	echo hfx_event_image_html($image_url, $category, $alt, $classes, $hue_degrees);
}

/**
 * Build frontend event payload list.
 *
 * @param int $limit Event limit.
 * @return array<int, array<string, mixed>>
 */
function hfx_get_events_payload($limit = 100) {
	static $cache = array();

	$limit = (int) $limit;

	// Return immediately if already fetched in this request.
	if ( isset( $cache[ $limit ] ) ) {
		return $cache[ $limit ];
	}

	// Try transient cache (5-minute TTL) to avoid thousands of DB queries per page load.
	$transient_key = 'hfx_events_payload_v2_' . $limit;
	$cached        = get_transient( $transient_key );
	if ( false !== $cached ) {
		$cache[ $limit ] = $cached;
		return $cached;
	}

	$posts  = hfx_get_event_posts($limit);
	$events = array();

	foreach ($posts as $post) {
		$payload = hfx_event_to_payload($post->ID);
		$events[] = $payload;
	}
	usort(
		$events,
		static function ( $left, $right ) {
			$left_key  = hfx_event_sort_key( (array) $left );
			$right_key = hfx_event_sort_key( (array) $right );
			if ( $left_key === $right_key ) {
				$left_title  = isset( $left['title'] ) ? strtolower( (string) $left['title'] ) : '';
				$right_title = isset( $right['title'] ) ? strtolower( (string) $right['title'] ) : '';
				return strcmp( $left_title, $right_title );
			}
			return strcmp( $left_key, $right_key );
		}
	);

	set_transient( $transient_key, $events, 5 * MINUTE_IN_SECONDS );
	$cache[ $limit ] = $events;
	return $events;
}

/**
 * Clear all hfx_events_payload transients so the next request rebuilds from DB.
 */
function hfx_clear_events_payload_cache() {
	foreach ( array( 100, 120, 200, 250, 300, 500 ) as $limit ) {
		delete_transient( 'hfx_events_payload_' . $limit );
		delete_transient( 'hfx_events_payload_v2_' . $limit );
	}
}
add_action( 'save_post_tribe_events', 'hfx_clear_events_payload_cache' );
add_action( 'save_post',              'hfx_clear_events_payload_cache' );
add_action( 'delete_post',            'hfx_clear_events_payload_cache' );
add_action( 'transition_post_status', 'hfx_clear_events_payload_cache' );

/**
 * Query var helper.
 *
 * @param string $key Key.
 * @return string
 */
function hfx_qs($key) {
	return isset($_GET[ $key ]) ? sanitize_text_field(wp_unslash($_GET[ $key ])) : '';
}

/**
 * Weekly edition settings — issue number, volume, editorial blurb.
 * Editable at Settings → Halifax Now in WP Admin.
 */
function hfx_register_weekly_settings() {
	register_setting( 'hfx_weekly_group', 'hfx_issue_number',  array( 'sanitize_callback' => 'absint' ) );
	register_setting( 'hfx_weekly_group', 'hfx_volume_number', array( 'sanitize_callback' => 'sanitize_text_field' ) );
	register_setting( 'hfx_weekly_group', 'hfx_weekly_blurb',  array( 'sanitize_callback' => 'sanitize_textarea_field' ) );

	add_settings_section( 'hfx_weekly_section', 'Weekly Edition', '__return_false', 'hfx-settings' );

	add_settings_field(
		'hfx_issue_number',
		'Issue number',
		static function () {
			$val = get_option( 'hfx_issue_number', '' );
			echo '<input type="number" name="hfx_issue_number" value="' . esc_attr( (string) $val ) . '" min="1" style="width:80px"> ';
			echo '<p class="description">Shows as <strong>NO 117</strong> in the masthead stamp.</p>';
		},
		'hfx-settings',
		'hfx_weekly_section'
	);

	add_settings_field(
		'hfx_volume_number',
		'Volume (Roman numeral)',
		static function () {
			$val = get_option( 'hfx_volume_number', '' );
			echo '<input type="text" name="hfx_volume_number" value="' . esc_attr( (string) $val ) . '" class="regular-text" placeholder="e.g. III"> ';
			echo '<p class="description">Shows as <strong>VOL III</strong> in the masthead stamp.</p>';
		},
		'hfx-settings',
		'hfx_weekly_section'
	);

	add_settings_field(
		'hfx_weekly_blurb',
		"This week's intro",
		static function () {
			$val = get_option( 'hfx_weekly_blurb', '' );
			echo '<textarea name="hfx_weekly_blurb" rows="4" class="large-text">' . esc_textarea( (string) $val ) . '</textarea>';
			echo '<p class="description">Editorial intro on the homepage hero. Update every week. Plain text only.</p>';
		},
		'hfx-settings',
		'hfx_weekly_section'
	);
}
add_action( 'admin_init', 'hfx_register_weekly_settings' );

function hfx_add_settings_menu() {
	add_options_page(
		'Halifax Now',
		'Halifax Now',
		'manage_options',
		'hfx-settings',
		'hfx_settings_page_html'
	);
}
add_action( 'admin_menu', 'hfx_add_settings_menu' );

function hfx_settings_page_html() {
	if ( ! current_user_can( 'manage_options' ) ) {
		return;
	}
	?>
	<div class="wrap">
		<h1><?php esc_html_e( 'Halifax Now — Weekly Settings', 'halifax-now-broadsheet' ); ?></h1>
		<form method="post" action="options.php">
			<?php settings_fields( 'hfx_weekly_group' ); ?>
			<?php do_settings_sections( 'hfx-settings' ); ?>
			<?php submit_button( 'Save' ); ?>
		</form>
	</div>
	<?php
}

/**
 * Register ACF field group for HFX event metadata.
 * Fields: critic pick, moods, neighbourhood, short blurb, editor blurb.
 */
function hfx_register_acf_fields() {
	if ( ! function_exists( 'acf_add_local_field_group' ) ) {
		return;
	}

	$post_types = array( 'tribe_events', 'post' );

	acf_add_local_field_group(
		array(
			'key'      => 'group_hfx_event_meta',
			'title'    => 'HFX Event Details',
			'fields'   => array(
				array(
					'key'          => 'field_hfx_critic_pick',
					'label'        => "Critic's Pick",
					'name'         => 'hfx_critic_pick',
					'type'         => 'true_false',
					'instructions' => 'Mark this event as an editorial pick. Displays a ★ badge.',
					'default_value'=> 0,
					'ui'           => 1,
				),
				array(
					'key'          => 'field_hfx_moods',
					'label'        => 'Moods',
					'name'         => 'hfx_moods',
					'type'         => 'checkbox',
					'instructions' => 'Select all that apply.',
					'choices'      => array(
						'chill'  => '🌙 Chill',
						'rowdy'  => '🔥 Rowdy',
						'date'   => '💋 Date Night',
						'kids'   => '🧃 Kid-friendly',
						'solo'   => '👤 Solo OK',
						'crew'   => '👯 Bring a crew',
						'free'   => '🪙 Broke-friendly',
						'rainy'  => '☔ Rainy-day',
					),
					'layout'       => 'horizontal',
					'return_format'=> 'value',
				),
				array(
					'key'          => 'field_hfx_neighbourhood',
					'label'        => 'Neighbourhood',
					'name'         => 'hfx_neighbourhood',
					'type'         => 'select',
					'instructions' => 'Primary neighbourhood for map and filtering.',
					'choices'      => array(
						'Downtown'      => 'Downtown',
						'North End'     => 'North End',
						'South End'     => 'South End',
						'West End'      => 'West End',
						'Quinpool'      => 'Quinpool',
						'Spring Garden' => 'Spring Garden',
						'Dartmouth'     => 'Dartmouth',
						'Bedford'       => 'Bedford',
					),
					'allow_null'   => 1,
					'placeholder'  => 'Select neighbourhood',
					'return_format'=> 'value',
				),
				array(
					'key'          => 'field_hfx_short_blurb',
					'label'        => 'Short Blurb',
					'name'         => 'hfx_short_blurb',
					'type'         => 'text',
					'instructions' => 'One-liner for event cards. Max 90 characters.',
					'maxlength'    => 90,
					'placeholder'  => 'e.g. Live jazz every Tuesday — no cover, no fuss.',
				),
				array(
					'key'          => 'field_hfx_editor_blurb',
					'label'        => 'Editor Blurb',
					'name'         => 'hfx_editor_blurb',
					'type'         => 'textarea',
					'instructions' => 'Opinionated 2–3 sentence editorial voice for the event detail page.',
					'rows'         => 4,
					'placeholder'  => 'Write in first-person editorial voice.',
				),
			),
			'location' => array(
				array(
					array(
						'param'    => 'post_type',
						'operator' => '==',
						'value'    => 'tribe_events',
					),
				),
				array(
					array(
						'param'    => 'post_type',
						'operator' => '==',
						'value'    => 'post',
					),
				),
			),
			'position'      => 'normal',
			'style'         => 'default',
			'label_placement' => 'top',
			'active'        => true,
		)
	);
}
add_action( 'acf/init', 'hfx_register_acf_fields' );
/**
 * Format event date + time as a human label for card display.
 *
 * Returns strings like "Tonight · 8pm", "Tomorrow · 2pm", "Sunday · 9am",
 * "Thu · Apr 23 · 8pm". The CSS class already applies text-transform:uppercase,
 * so lowercase output here is intentional.
 *
 * @param string $date      YYYY-MM-DD event date (may be empty).
 * @param string $time      HH:MM 24-hour event time (may be empty).
 * @param string $today_ymd Current date as YYYY-MM-DD.
 * @return string
 */
function hfx_format_event_when( $date, $time, $today_ymd ) {
	$time_fmt = '';
	if ( is_string( $time ) && 1 === preg_match( '/^(\d{2}):(\d{2})$/', $time, $m ) ) {
		$h    = (int) $m[1];
		$min  = (int) $m[2];
		$ampm = $h >= 12 ? 'pm' : 'am';
		$h12  = $h % 12;
		if ( 0 === $h12 ) {
			$h12 = 12;
		}
		$time_fmt = $min > 0
			? sprintf( '%d:%02d%s', $h12, $min, $ampm )
			: sprintf( '%d%s', $h12, $ampm );
	}

	if ( ! is_string( $date ) || '' === $date ) {
		return $time_fmt;
	}

	$today_ts     = (int) strtotime( $today_ymd );
	$tomorrow_ymd = gmdate( 'Y-m-d', $today_ts + DAY_IN_SECONDS );
	$event_ts     = (int) strtotime( $date );

	// Treat epoch/zero timestamps as missing — these come from events where
	// _EventStartDate is empty or '0000-00-00', which resolves to Dec 31 1969
	// in Atlantic time. Both the date AND the time are garbage in this case
	// (20:00 = UTC-4 offset of epoch), so suppress everything.
	if ( $event_ts <= 0 ) {
		return '';
	}

	$diff_days    = (int) round( ( $event_ts - $today_ts ) / DAY_IN_SECONDS );

	if ( $date === $today_ymd ) {
		$label = 'Tonight';
	} elseif ( $date === $tomorrow_ymd ) {
		$label = 'Tomorrow';
	} elseif ( $diff_days > 0 && $diff_days <= 6 ) {
		$label = date_i18n( 'l', $event_ts );
	} else {
		$label = date_i18n( 'D · M j', $event_ts );
	}

	return $time_fmt ? $label . ' · ' . $time_fmt : $label;
}

/**
 * Resolve the first non-empty cost from known import/meta variants.
 *
 * @param int $post_id Event post ID.
 * @return string
 */
function hfx_resolve_event_cost_from_meta_variants( $post_id ) {
	$keys = array(
		'_EventCost',   // TEC canonical.
		'Event Cost',   // Common CSV import variant.
		'EVENT COST',   // Scraper header variant.
		'event_cost',   // Lowercase variant.
	);

	foreach ( $keys as $key ) {
		$value = trim( (string) get_post_meta( (int) $post_id, $key, true ) );
		if ( '' !== $value ) {
			return $value;
		}
	}
	return '';
}

/**
 * WP-CLI: Backfill missing _EventCost from alternate imported cost keys.
 *
 * Usage:
 *   wp hfx backfill-event-cost --dry-run=1
 *   wp hfx backfill-event-cost --force=1
 *   wp hfx backfill-event-cost --limit=500
 *   wp hfx backfill-event-cost --post_id=12345
 *
 * @param array $args Positional args (unused).
 * @param array $assoc_args Flags/options.
 * @return void
 */
function hfx_cli_backfill_event_cost( $args, $assoc_args ) {
	if ( ! defined( 'WP_CLI' ) || ! WP_CLI ) {
		return;
	}

	$dry_run = isset( $assoc_args['dry-run'] )
		? filter_var( $assoc_args['dry-run'], FILTER_VALIDATE_BOOLEAN )
		: true;
	$force = isset( $assoc_args['force'] )
		? filter_var( $assoc_args['force'], FILTER_VALIDATE_BOOLEAN )
		: false;
	$limit = isset( $assoc_args['limit'] ) ? max( 1, (int) $assoc_args['limit'] ) : 0;
	$post_id_filter = isset( $assoc_args['post_id'] ) ? (int) $assoc_args['post_id'] : 0;

	$q_args = array(
		'post_type'      => 'tribe_events',
		'post_status'    => array( 'publish', 'future', 'draft', 'pending', 'private' ),
		'fields'         => 'ids',
		'orderby'        => 'ID',
		'order'          => 'DESC',
		'posts_per_page' => $limit > 0 ? $limit : -1,
		'no_found_rows'  => true,
	);
	if ( $post_id_filter > 0 ) {
		$q_args['post__in'] = array( $post_id_filter );
	}

	$ids = get_posts( $q_args );
	if ( empty( $ids ) ) {
		WP_CLI::success( 'No matching tribe_events posts found.' );
		return;
	}

	$scanned = 0;
	$updated = 0;
	$skipped = 0;
	$already = 0;

	WP_CLI::log(
		sprintf(
			'Backfill starting (%s, force=%s, posts=%d).',
			$dry_run ? 'dry-run' : 'apply',
			$force ? 'true' : 'false',
			count( $ids )
		)
	);

	foreach ( $ids as $pid ) {
		$pid = (int) $pid;
		$scanned++;

		$current = trim( (string) get_post_meta( $pid, '_EventCost', true ) );
		if ( '' !== $current && ! $force ) {
			$already++;
			continue;
		}

		$resolved = hfx_resolve_event_cost_from_meta_variants( $pid );
		if ( '' === $resolved ) {
			$skipped++;
			continue;
		}

		if ( $dry_run ) {
			$updated++;
			WP_CLI::log( sprintf( '[dry-run] %d => _EventCost "%s"', $pid, $resolved ) );
			continue;
		}

		update_post_meta( $pid, '_EventCost', $resolved );
		$updated++;
		WP_CLI::log( sprintf( '[updated] %d => _EventCost "%s"', $pid, $resolved ) );
	}

	if ( $updated > 0 && ! $dry_run ) {
		hfx_clear_events_payload_cache();
	}

	WP_CLI::success(
		sprintf(
			'Done. scanned=%d updated=%d already=%d skipped=%d mode=%s',
			$scanned,
			$updated,
			$already,
			$skipped,
			$dry_run ? 'dry-run' : 'apply'
		)
	);
}

if ( defined( 'WP_CLI' ) && WP_CLI ) {
	WP_CLI::add_command( 'hfx backfill-event-cost', 'hfx_cli_backfill_event_cost' );
}
