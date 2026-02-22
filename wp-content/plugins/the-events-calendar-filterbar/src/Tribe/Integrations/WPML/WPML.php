<?php
/**
 * Class Tribe__Events__Filterbar__Integrations__WPML__WPML
 *
 * Handles anything relating to Events Filterbar and WPML integration
 *
 * @since 4.5.8
 */
class Tribe__Events__Filterbar__Integrations__WPML__WPML {

	/**
	 * Hooks any required filters and actions.
	 *
	 * @since  4.5.8
	 *
	 * @return void
	 */
	public function hook() {

		// Add WPML integration for the additional fields functionality.
		add_filter( 'tribe_events_filter_additional_fields_query', [ __CLASS__, 'wpml_filter_additional_fields_query' ] );

		// Add filter for organizer IDs to get original language IDs.
		add_filter( 'tribe_filterbar_organizer_ids', [ __CLASS__, 'filter_organizer_ids' ], 10, 1 );

		// Add filter for venue IDs to get original language IDs.
		add_filter( 'tribe_filterbar_venue_ids', [ __CLASS__, 'filter_venue_ids' ], 10, 1 );

	}

	/**
	 * Add WPML integration for the additional fields functionality from Events Calendar Pro.
	 *
	 * @param string $query
	 *
	 * @since  4.5.8
	 * @return string
	 */
	public static function wpml_filter_additional_fields_query( $query ) {

		global $wpdb;

		// If Events Calendar Pro is not active we cannot support additional fields.
		if ( ! class_exists( 'Tribe__Events__Pro__Main' ) ) {
			return $query;
		}

		$language = apply_filters( 'wpml_current_language', false );
		$join     = "INNER JOIN {$wpdb->prefix}icl_translations ON element_id = $wpdb->posts.ID AND element_type = CONCAT( 'post_', $wpdb->posts.post_type )";
		$where    = $wpdb->prefix . "icl_translations.language_code = '" . $language . "'";
		$query    = str_replace( 'WHERE', $join . ' WHERE ', $query ) . ' AND ' . $where;

		return $query;
	}

	/**
	 * Get the original post IDs for the provided IDs.
	 *
	 * @since 5.5.10
	 *
	 * @param array<int> $post_ids  Array of post IDs to get original IDs for.
	 * @param string     $post_type The post type to convert IDs for.
	 *
	 * @return array<int> Array of original post IDs.
	 */
	public static function get_original_post_ids( $post_ids, $post_type ) {
		return array_map(
			function ( $id ) use ( $post_type ) {
				return self::convert_to_original_id( $id, $post_type );
			},
			$post_ids
		);
	}

	/**
	 * Converts a single post ID to its original language version.
	 *
	 * @since 5.5.10
	 *
	 * @param int    $id        The post ID to convert.
	 * @param string $post_type The post type to convert the ID for.
	 *
	 * @return int The original language version of the post ID.
	 */
	protected static function convert_to_original_id( $id, $post_type ) {

		/**
		 * Get the default language for the site.
		 *
		 * @since 5.5.10
		 *
		 * @return string The language code.
		 */
		$wpml_default_lang = apply_filters( 'wpml_default_language', null );

		/**
		 * Filters a post ID to get its original language version using WPML.
		 *
		 * @since 5.5.10
		 *
		 * @param int    $id                The post ID to convert.
		 * @param string $post_type         The post type of the post.
		 * @param bool   true               Whether to return original if translation is missing.
		 * @param string $wpml_default_lang The language code to convert to (null = default language).
		 *
		 * @return int The original language version of the post ID
		 */
		return apply_filters( 'wpml_object_id', $id, $post_type, true, $wpml_default_lang );
	}

	/**
	 * Filter organizer IDs to get their original language versions.
	 *
	 * @since 5.5.10
	 *
	 * @param array $organizer_ids Array of organizer post IDs.
	 *
	 * @return array Modified array of organizer post IDs.
	 */
	public static function filter_organizer_ids( $organizer_ids ) {
		return self::get_original_post_ids( $organizer_ids, Tribe__Events__Main::ORGANIZER_POST_TYPE );
	}

	/**
	 * Filter venue IDs to get their original language versions.
	 *
	 * @since 5.5.10
	 *
	 * @param array $venue_ids Array of venue post IDs.
	 *
	 * @return array Modified array of venue post IDs.
	 */
	public static function filter_venue_ids( $venue_ids ) {
		return self::get_original_post_ids( $venue_ids, Tribe__Events__Main::VENUE_POST_TYPE );
	}

}
