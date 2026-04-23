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
		'https://fonts.googleapis.com/css2?family=Anton&family=Inter:wght@400;500;600&family=Inter+Tight:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:ital,wght@0,700;0,900;1,700;1,900&family=Source+Serif+4:ital,wght@0,400;0,700;1,400&family=Space+Grotesk:wght@400;500;700&display=swap',
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
			'browseUrl' => home_url('/browse/'),
		)
	);
}
add_action('wp_enqueue_scripts', 'hfx_broadsheet_enqueue_assets');

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
	$browse_path  = (string) parse_url( home_url( '/browse/' ), PHP_URL_PATH );
	$browse_path  = trim( $browse_path, '/' );

	if ( '' === $request_path || $request_path !== $browse_path ) {
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

	$admin_email = get_option('admin_email');
	$subject     = sprintf(__('New Event Submission: %s', 'halifax-now-broadsheet'), $title);
	$message     = sprintf(
		"Title: %s\nVenue: %s\nDate: %s\nTime: %s\nPrice: %s\nContact: %s\n\nDetails:\n%s",
		$title,
		$venue,
		$date,
		$time,
		$price,
		$contact,
		$blurb
	);

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
	);

	if (post_type_exists('tribe_events')) {
		$query_args['meta_key'] = '_EventStartDate';
		$query_args['orderby']  = 'meta_value';
		$query_args['order']    = 'ASC';
	}

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
	foreach ( $candidates as $candidate ) {
		if ( ! hfx_event_is_generic_category_slug( $candidate['slug'] ) && isset( $hue_map[ $candidate['slug'] ] ) ) {
			return $candidate;
		}
	}
	foreach ( $candidates as $candidate ) {
		if ( ! hfx_event_is_generic_category_slug( $candidate['slug'] ) ) {
			return $candidate;
		}
	}

	return $candidates[0];
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
	$link    = get_permalink($post_id);

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
	if ( ! hfx_is_valid_event_date( (string) $date ) ) {
		$date = '';
	}
	if ( ! hfx_is_valid_event_time( (string) $time ) ) {
		$time = '';
	}
	if ( ! hfx_is_valid_event_time( (string) $end_time ) ) {
		$end_time = '';
	}

	$price = '';
	if (function_exists('tribe_get_cost')) {
		$price = (string) tribe_get_cost($post_id, true);
	}
	$price = trim($price);
	if ($price === '') {
		$price = (string) get_post_meta($post_id, '_EventCost', true);
		$price = trim($price);
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
	$hue       = hfx_event_category_hue( $cat_key, $cat_label, (string) $post_id );
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
	$transient_key = 'hfx_events_payload_' . $limit;
	$cached        = get_transient( $transient_key );
	if ( false !== $cached ) {
		$cache[ $limit ] = $cached;
		return $cached;
	}

	$posts  = hfx_get_event_posts($limit);
	$events = array();

	foreach ($posts as $post) {
		$events[] = hfx_event_to_payload($post->ID);
	}

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
