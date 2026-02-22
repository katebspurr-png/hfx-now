<?php
/**
 * Filterbar Tag Filter
 *
 * @since 3.10
 */

use Tribe__Cache_Listener as Cache_Listener;

/**
 * Class Tribe__Events__Filterbar__Filters__Tag
 */
class Tribe__Events__Filterbar__Filters__Tag extends Tribe__Events__Filterbar__Filter { // phpcs:ignore PEAR.NamingConventions, StellarWP.Classes, Generic.Classes

	/**
	 * The filter type
	 *
	 * @var string
	 */
	public $type = 'select';

	/**
	 * Get the admin form for the tag filter.
	 *
	 * @return string
	 */
	public function get_admin_form() {
		$title = $this->get_title_field();
		$type  = $this->get_multichoice_type_field();
		return $title . $type;
	}

	/**
	 * Get the values for the tag filter.
	 *
	 * @return array
	 */
	protected function get_values() {
		$cache         = tribe_cache();
		$cache_id      = __CLASS__ . '_get_event_tag_values';
		$cache_trigger = Cache_Listener::TRIGGER_SAVE_POST;

		$tags_array = $cache->get( $cache_id, $cache_trigger, false );

		if ( false !== $tags_array ) {
			return $tags_array;
		}

		$tags_array = [];

		$terms = get_terms(
			[
				'taxonomy'   => 'post_tag',
				'orderby'    => 'name',
				'hide_empty' => true,
				'fields'     => 'id=>name',
			]
		);

		foreach ( $terms as $term_id => $term_name ) {
			$the_query = new WP_Query(
				[
					'post_type'      => Tribe__Events__Main::POSTTYPE,
					'tag_id'         => $term_id,
					'posts_per_page' => 1,
					'no_found_rows'  => true,
				]
			);

			if ( $the_query->have_posts() ) {
				$tags_array[ $term_id ] = [
					'name'  => $term_name,
					'value' => $term_id,
				];
			}
		}

		$cache->set( $cache_id, $tags_array, HOUR_IN_SECONDS, $cache_trigger );

		return $tags_array;
	}

	/**
	 * Setup the query args for the tag filter.
	 *
	 * @return void
	 */
	protected function setup_query_args() {
		$this->queryArgs = [ 'tag__in' => $this->currentValue ]; // phpcs:ignore WordPress.NamingConventions.ValidVariableName.UsedPropertyNotSnakeCase
	}
}
