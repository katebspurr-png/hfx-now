<?php // phpcs:ignoreFile StellarWP.Classes.ValidClassName.NotSnakeCaseClass
/**
 * An implementation of the Date From filter that applies to specific contexts.
 *
 * @since   5.6.0
 *
 * @package Tribe\Events\Filterbar\Views\V2\Filters
 */

namespace Tribe\Events\Filterbar\Views\V2\Filters;

/**
 * Class Date_From
 *
 * @since   5.6.0
 *
 * @package Tribe\Events\Filterbar\Views\V2\Filters
 */
class Date_From extends \Tribe__Events__Filterbar__Filter {
	use Context_Filter;

	/**
	 * The type of filter - in this case, a date
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
				// the default value for the date input is empty.
				'value' => '',
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

	public function setup_join_clause() {
		global $wpdb;

		// Use a specific alias for our start date meta join
		$this->joinClause = " LEFT JOIN {$wpdb->postmeta} AS date_from_start ON {$wpdb->posts}.ID = date_from_start.post_id AND date_from_start.meta_key = '_EventStartDate' ";
	}

	/**
	 * Set up the where clause for the query
	 * Override the parent method to implement date-specific filtering
	 */
	protected function setup_where_clause() {
		/** @var wpdb $wpdb */
		global $wpdb;

		// Ensure we have a valid date
		if ( empty( $this->currentValue ) || ! preg_match( '/^\d{4}-\d{2}-\d{2}$/', $this->currentValue ) ) {
			return;
		}

		$selected_date = $this->currentValue;

		// Build where clause for events starting on or after the selected date.
		// Use our specific alias to avoid conflicts.
		$this->whereClause = $wpdb->prepare(
			" AND date_from_start.meta_value >= %s",
			$selected_date . ' 00:00:00'
		);
	}
}
