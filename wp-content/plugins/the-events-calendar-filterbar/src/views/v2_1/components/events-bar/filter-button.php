<?php
/**
 * View: Filter Button Component
 *
 * Override this template in your own theme by creating a file at:
 * [your-theme]/tribe/events-filterbar/v2_1/components/events-bar/filter-button.php
 *
 * See more documentation about our views templating system.
 *
 * @link http://evnt.is/1aiy
 *
 * @var string $breakpoint_pointer String we use as pointer to the current view we are setting up with breakpoints.
 * @var string $filterbar_state    Current state of the entire Filter Bar, either `open` or `closed`.
 *
 * @version 5.5.10
 *
 * @since 5.0.0
 * @since 5.5.10 Adjusted icon to be hidden from screen readers.
 */

$button_classes = [ 'tribe-events-c-events-bar__filter-button' ];

if ( empty( $filterbar_state ) || 'closed' === $filterbar_state ) {
	$button_text   = __( 'Show filters', 'tribe-events-filter-view' );
	$aria_expanded = 'false';
} else {
	$button_classes[] = 'tribe-events-c-events-bar__filter-button--active';
	$button_text      = __( 'Hide filters', 'tribe-events-filter-view' );
	$aria_expanded    = 'true';
}
?>
<div class="tribe-events-c-events-bar__filter-button-container">
	<button
		<?php tribe_classes( $button_classes ); ?>
		aria-controls="tribe-filter-bar--<?php echo esc_attr( $breakpoint_pointer ); ?>"
		aria-expanded="<?php echo esc_attr( $aria_expanded ); ?>"
		data-js="tribe-events-filter-button"
	>
		<svg aria-hidden="true" <?php tribe_classes( [ 'tribe-events-c-events-bar__filter-button-icon', 'tribe-common-c-svgicon', 'tribe-common-c-svgicon--filter' ] ); ?> viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" clip-rule="evenodd" d="M4.44 1a.775.775 0 10-1.55 0v1.89H1a.775.775 0 000 1.55h1.89v1.893a.775.775 0 001.55 0V4.44H17a.775.775 0 000-1.55H4.44V1zM.224 14.332c0-.428.347-.775.775-.775h12.56v-1.893a.775.775 0 011.55 0v1.893h1.89a.775.775 0 010 1.55h-1.89v1.89a.775.775 0 01-1.55 0v-1.89H.998a.775.775 0 01-.775-.775z"/></svg>
		<span class="tribe-events-c-events-bar__filter-button-text tribe-common-b2 tribe-common-a11y-visual-hide">
			<?php echo esc_html( $button_text ); ?>
		</span>
	</button>
</div>
