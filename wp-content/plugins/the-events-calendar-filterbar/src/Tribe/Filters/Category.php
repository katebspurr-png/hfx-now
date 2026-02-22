<?php

use Tribe__Utils__Array as Arr;

/**
 * Class Tribe__Events__Filterbar__Filters__Category
 */
class Tribe__Events__Filterbar__Filters__Category extends Tribe__Events__Filterbar__Filter {

	public $type = 'select';

	public function get_admin_form() {
		$title = $this->get_title_field();
		$type  = $this->get_multichoice_type_field();

		// Add our custom control.
		$visible_categories = $this->get_visible_categories_field();

		// Return all fields.
		return $title . $type . $visible_categories;
	}

	/**
	 * Get the list of category IDs that are allowed to be shown in the frontend filter.
	 *
	 * @since 5.6.0
	 *
	 * @return array
	 */
	protected function get_current_filter_allowed_cats(): array {
		// Get the current filter settings.
		$current_active_filters = Tribe__Events__Filterbar__View::instance()->get_filter_settings();

		// Get the current selected categories (default to empty array).
		return $current_active_filters['eventcategory']['visible_categories'] ?? [];
	}

	/**
	 * Create a multiselect field to control which categories show in filter
	 */
	protected function get_visible_categories_field() {
		// Get the current selected categories (default to empty array).
		$visible_cats = $this->get_current_filter_allowed_cats();

		// Get all event categories.
		$categories = get_terms(
			[
				'taxonomy'   => Tribe__Events__Main::TAXONOMY,
				'hide_empty' => false,
				'orderby'    => 'name',
				'order'      => 'ASC',
			]
		);

		// Create the field HTML.
		$field  = '<div class="tribe_events_active_filter_visible_categories">';
		$field .= '<p>' . __( 'Select which categories to show in the frontend filter:', 'tribe-events-filter-view' ) . '</p>';

		if ( ! empty( $categories ) ) {
			$field .= sprintf(
				'<select name="%s[]" multiple="multiple" class="tribe-dropdown" data-placeholder="%s" style="width: 100%%;">',
				$this->get_admin_field_name( 'visible_categories' ),
				esc_attr__( 'Select categories to display', 'tribe-events-filter-view' )
			);

			// Option to select all categories.
			$field .= sprintf(
				'<option value="all" %s>%s</option>',
				selected( in_array( 'all', $visible_cats ), true, false ),
				esc_html__( 'All Categories', 'tribe-events-filter-view' )
			);

			// Add all categories as options.
			foreach ( $categories as $category ) {
				$field .= sprintf(
					'<option value="%s" %s>%s</option>',
					esc_attr( $category->term_id ),
					selected( in_array( $category->term_id, $visible_cats ), true, false ),
					esc_html( $category->name )
				);
			}

			$field .= '</select>';

			// Add some help text.
			$field .= '<p class="description">' . __( 'If no categories are selected, all categories will be shown. Select "All Categories" to explicitly show all categories.', 'tribe-events-filter-view' ) . '</p>';
		} else {
			$field .= '<p>' . __( 'No event categories found.', 'tribe-events-filter-view' ) . '</p>';
		}

		$field .= '</div>';

		// Add script to initialize select2.
		$field .= "
            <script type='text/javascript'>
            jQuery(document).ready(function($) {
                $('.tribe-dropdown').select2({
                    dropdownCssClass: 'tribe-select2-results__option',
                    width: '100%'
                });

                // Handle the 'All Categories' option.
                $('.tribe-dropdown').on('change', function() {
                    var selectedValues = $(this).val() || [];

                    // If 'all' is selected, deselect other options.
                    if (selectedValues.includes('all')) {
                        $(this).val(['all']).trigger('change.select2');
                    }
                });
            });
            </script>
            ";

		return $field;
	}


	protected function get_values() {
		$terms = [];

		$args = [
			'taxonomy'   => Tribe__Events__Main::TAXONOMY,
			'orderby'    => 'name',
			'order'      => 'ASC',
			'number'     => 200,
			'hide_empty' => true,
		];

		$allowed_cats = $this->get_current_filter_allowed_cats();

		if ( ! empty( $allowed_cats ) && ! in_array( 'all', $allowed_cats, true ) ) {
			$args['include'] = $allowed_cats;
		}

		/**
		 * Filter the args of displaying categories.
		 *
		 * @since 5.5.8
		 *
		 * @param array $args   The arguments passed to the `get_terms()` query when filtering for categories.
		 * @param self  $filter The instance of the filter that we are filtering the args for.
		 */
		$args = (array) apply_filters( 'tec_events_filter_filters_category_get_terms_args', $args, $this );

		// Load all available event categories.
		$source = get_terms( $args );

		if ( empty( $source ) || is_wp_error( $source ) ) {
			return [];
		}

		// Preprocess the terms.
		foreach ( $source as $term ) {
			$terms[ (int) $term->term_id ] = $term;
			$term->parent                  = (int) $term->parent;
			$term->depth                   = 0;
			$term->children                = [];
		}

		// Initially copy the source list of terms to our ordered list.
		$ordered_terms = $terms;

		// Re-order!
		foreach ( $terms as $id => $term ) {
			// Skip root elements.
			if ( 0 === $term->parent ) {
				continue;
			}

			// Reposition child terms within the ordered terms list.
			unset( $ordered_terms[ $id ] );
			$term->depth                             = $this->get_depth( $term );
			$terms[ $term->parent ]->children[ $id ] = $term;
		}

		// Finally flatten out and return.
		return $this->flattened_term_list( $ordered_terms );
	}

	/**
	 * Get Term Depth.
	 *
	 * @since 4.5
	 *
	 * @param     $term
	 * @param int $level
	 *
	 * @return int
	 */
	protected function get_depth( $term, $level = 0 ) {
		if ( ! $term instanceof WP_Term ) {
			return 0;
		}

		if ( 0 == $term->parent ) {
			return $level;
		} else {
			++$level;
			$term = get_term_by( 'id', $term->parent, Tribe__Events__Main::TAXONOMY );

			return $this->get_depth( $term, $level );
		}
	}

	/**
	 * Flatten out the hierarchical list of event categories into a single list of values,
	 * applying formatting (non-breaking spaces) to help indicate the depth of each nested
	 * item.
	 *
	 * @param array $term_items
	 * @param array $existing_list
	 *
	 * @return array
	 */
	protected function flattened_term_list( array $term_items, array $existing_list = null ) {
		// Pull in the existing list when called recursively.
		$flat_list = is_array( $existing_list ) ? $existing_list : [];

		// Add each item - including nested items - to the flattened list.
		foreach ( $term_items as $term ) {

			$has_child        = ! empty( $term->children ) ? ' has-child closed' : '';
			$parent_child_cat = '';
			if ( ! $term->parent && $has_child ) {
				$parent_child_cat = ' parent-' . absint( $term->term_id );
			} elseif ( $term->parent && $has_child ) {
				$parent_child_cat = ' parent-' . absint( $term->term_id ) . ' child-' . absint( $term->parent );
			} elseif ( $term->parent && ! $has_child ) {
				$parent_child_cat = ' child-' . absint( $term->parent );
			}

			$flat_list[] = [
				'name'  => $term->name,
				'depth' => $term->depth,
				'value' => $term->term_id,
				'data'  => [ 'slug' => $term->slug ],
				'class' =>
					esc_html( $this->set_category_class( $term->depth ) ) .
					'tribe-events-category-' . $term->slug .
					$parent_child_cat .
					$has_child,
			];

			if ( ! empty( $term->children ) ) {
				$child_items = $this->flattened_term_list( $term->children, $existing_list );
				$flat_list   = array_merge( $flat_list, $child_items );
			}
		}

		return $flat_list;
	}

	/**
	 * Return class based on dept of the event category.
	 *
	 * @param $depth
	 *
	 * @return bool|string
	 */
	protected function set_category_class( $depth ) {

		$class = 'tribe-parent-cat ';

		if ( 1 == $depth ) {
			$class = 'tribe-child-cat ';
		} elseif ( 1 <= $depth ) {
			$class = 'tribe-grandchild-cat tribe-depth-' . $depth . ' ';
		}

		/**
		 * Filter the event category class based on the term depth for the Filter Bar.
		 *
		 * @param string $class class as a string
		 * @param int    $depth numeric value of the depth, parent is 0
		 */
		$class = apply_filters( 'tribe_events_filter_event_category_display_class', $class, $depth );

		return $class;
	}

	/**
	 * This method will only be called when the user has applied the filter (during the
	 * tribe_events_pre_get_posts action) and sets up the taxonomy query, respecting any
	 * other taxonomy queries that might already have been setup (whether by The Events
	 * Calendar, another plugin or some custom code, etc).
	 *
	 * @see Tribe__Events__Filterbar__Filter::pre_get_posts()
	 *
	 * @param WP_Query $query
	 */
	protected function pre_get_posts( WP_Query $query ) {
		$existing_rules = (array) $query->get( 'tax_query' );
		$values         = (array) $this->currentValue;

		// If select display and event category has children get all those ids for query.
		if ( 'select' === $this->type ) {

			$categories = get_categories(
				[
					'taxonomy' => Tribe__Events__Main::TAXONOMY,
					'child_of' => current( $values ),
				]
			);

			if ( ! empty( $categories ) ) {
				foreach ( $categories as $category ) {
					$values[] = $category->term_id;
				}
			}
		} elseif ( 'multiselect' === $this->type ) {
			// Any value that will evaluate to empty, we drop.
			$values = array_filter( Arr::list_to_array( $values ) );
		}

		$new_rule = [
			'taxonomy' => Tribe__Events__Main::TAXONOMY,
			'operator' => 'IN',
			'terms'    => array_map( 'absint', $values ),
		];

		/**
		 * Controls the relationship between different taxonomy queries.
		 *
		 * If set to an empty value, then no attempt will be made by the additional field filter
		 * to set the meta_query "relation" parameter.
		 *
		 * @var string $relation "AND"|"OR"
		 */
		$relationship = apply_filters( 'tribe_events_filter_taxonomy_relationship', 'AND' );

		/**
		 * If taxonomy filter meta queries should be nested and grouped together.
		 *
		 * The default is true in WordPress 4.1 and greater, which allows for greater flexibility
		 * when combined with taxonomy queries added by other filters/other plugins.
		 *
		 * @var bool $group
		 */
		$nest = apply_filters( 'tribe_events_filter_nest_taxonomy_queries', version_compare( $GLOBALS['wp_version'], '4.1', '>=' ) );

		if ( $nest ) {
			$tax_query = array_replace_recursive( $existing_rules, [ __CLASS__ => [ $new_rule ] ] );
		} else {
			$tax_query = [];
			$append    = true;

			foreach ( $existing_rules as $existing_rule_key => $existing_rule_value ) {
				if ( $existing_rule_value === '' ) {
					continue;
				}

				if ( is_int( $existing_rule_key ) ) {
					$tax_query[] = $existing_rule_value;
				} else {
					$tax_query[ $existing_rule_key ] = $existing_rule_value;
				}

				if ( ! is_array( $existing_rule_value ) ) {
					continue;
				}

				if ( $existing_rule_value == $new_rule ) {
					$append = false;
					break;
				}
			}

			if ( $append ) {
				$tax_query[] = $new_rule;
			}
		}

		// Apply the relationship (we leave this late, or the recursive array merge would potentially cause duplicates).
		if ( ! empty( $relationship ) && $nest ) {
			$tax_query[ __CLASS__ ]['relation'] = $relationship;
		} elseif ( ! empty( $relationship ) ) {
			$tax_query['relation'] = $relationship;
		}

		// Apply our new meta query rules.
		$query->set( 'tax_query', $tax_query );
	}
}
