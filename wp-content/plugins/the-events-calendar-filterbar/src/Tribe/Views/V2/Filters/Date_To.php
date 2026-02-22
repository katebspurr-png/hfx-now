<?php // phpcs:ignoreFile StellarWP.Classes.ValidClassName.NotSnakeCaseClass
/**
 * An implementation of the Date To filter that applies to specific contexts.
 *
 * @since   5.6.0
 *
 * @package Tribe\Events\Filterbar\Views\V2\Filters
 */

namespace Tribe\Events\Filterbar\Views\V2\Filters;

use Tribe__Events__Filterbar__Filter;

/**
 * Class Date_To
 *
 * @since   5.6.0
 *
 * @package Tribe\Events\Filterbar\Views\V2\Filters
 */
class Date_To extends Tribe__Events__Filterbar__Filter {
	use Context_Filter;

	/**
	 * The type of filter - in this case, a calendar
	 * @var string
	 */
	public $type = 'date';

	/**
	 * Get the values for the filter
	 *
	 * @return array Empty array as calendar doesn't need predefined values
	 */
	protected function get_values() {
		return [
			[
				'value' => date( 'Y-m-d', strtotime( '+30 days' ) )
			]
		];
	}

	/**
	 * Get the admin form for filter settings
	 *
	 * @return string The form HTML
	 */
	public function get_admin_form() {
		return $this->get_title_field();
	}

	/**
	 * Set up the join clause for the query
	 * Override the parent method to use specific table aliases
	 */
	protected function setup_join_clause() {
		global $wpdb;

		// Add join for end date reference if needed.
		$this->joinClause = " LEFT JOIN {$wpdb->postmeta} AS date_to_end ON {$wpdb->posts}.ID = date_to_end.post_id AND date_to_end.meta_key = '_EventEndDate' ";
	}

	/**
	 * Set up the where clause for the query
	 * Override the parent method to implement date-specific filtering with specific aliases
	 */
	protected function setup_where_clause() {
		global $wpdb;

		// Ensure we have a valid date.
		if ( empty( $this->currentValue ) || ! preg_match( '/^\d{4}-\d{2}-\d{2}$/', $this->currentValue ) ) {
			return;
		}

		$selected_date = $this->currentValue;

		// Build where clause for events starting before or on the selected date.
		// Use our specific alias to avoid conflicts.
		$this->whereClause = $wpdb->prepare(
			" AND date_to_end.meta_value <= %s",
			$selected_date . ' 23:59:59'
		);
	}
}
