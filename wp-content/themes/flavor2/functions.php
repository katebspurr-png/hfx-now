<?php
/**
 * Flavor 2 — Theme functions and definitions
 *
 * @package Flavor2
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'FLAVOR2_VERSION', '1.0.0' );

/**
 * Enqueue styles and scripts.
 */
function flavor2_enqueue_assets() {
	wp_enqueue_style(
		'flavor2-google-fonts',
		'https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,400;0,600;0,700;0,900;1,700&family=Barlow:wght@400;500;600&display=swap',
		array(),
		null
	);

	wp_enqueue_style(
		'flavor2-main',
		get_theme_file_uri( 'assets/css/main.css' ),
		array( 'flavor2-google-fonts' ),
		FLAVOR2_VERSION
	);

	wp_enqueue_script(
		'flavor2-main',
		get_theme_file_uri( 'assets/js/main.js' ),
		array(),
		FLAVOR2_VERSION,
		true
	);
}
add_action( 'wp_enqueue_scripts', 'flavor2_enqueue_assets' );

/**
 * Theme setup — register menus, support, etc.
 */
function flavor2_setup() {
	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'html5', array(
		'search-form',
		'comment-form',
		'comment-list',
		'gallery',
		'caption',
		'style',
		'script',
	) );

	register_nav_menus( array(
		'primary'     => __( 'Primary Navigation', 'flavor2' ),
		'footer'      => __( 'Footer Navigation', 'flavor2' ),
	) );
}
add_action( 'after_setup_theme', 'flavor2_setup' );

/**
 * Custom walker for the primary nav so we can output the CTA styling.
 */
class Flavor2_Nav_Walker extends Walker_Nav_Menu {

	public function start_el( &$output, $item, $depth = 0, $args = null, $id = 0 ) {
		$classes = empty( $item->classes ) ? array() : (array) $item->classes;

		// Mark items with the "cta" CSS class so the Submit Event button renders correctly.
		$li_class = in_array( 'cta', $classes, true ) ? ' class="cta"' : '';

		$output .= '<li' . $li_class . '>';
		$output .= '<a href="' . esc_url( $item->url ) . '">';
		$output .= esc_html( $item->title );
		$output .= '</a>';
	}

	public function end_el( &$output, $item, $depth = 0, $args = null ) {
		$output .= '</li>';
	}
}
