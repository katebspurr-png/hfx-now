<?php
/**
 * View: Top Bar - Navigation
 *
 * Override this template in your own theme by creating a file at:
 * [your-theme]/tribe/events-pro/v2/photo/top-bar/nav.php
 *
 * See more documentation about our views templating system.
 *
 * @link https://evnt.is/1aiy
 *
 * @version 7.7.13
 *
 * @since 7.7.13 Add aria-label attribute to nav. [TEC-5732]
 *
 * @var string $prev_url The URL to the previous page, if any, or an empty string.
 * @var string $next_url The URL to the next page, if any, or an empty string.
 */

$nav_aria_label = sprintf(
	// Translators: %s: Events (plural).
	__( 'Top %s list pagination', 'tribe-events-calendar-pro' ),
	tribe_get_event_label_plural_lowercase()
);
?>
<nav class="tribe-events-c-top-bar__nav tribe-common-a11y-hidden" aria-label="<?php echo esc_attr( $nav_aria_label ); ?>">
	<ul class="tribe-events-c-top-bar__nav-list">
		<?php
		if ( ! empty( $prev_url ) ) {
			$this->template( 'photo/top-bar/nav/prev' );
		} else {
			$this->template( 'photo/top-bar/nav/prev-disabled' );
		}
		?>

		<?php
		if ( ! empty( $next_url ) ) {
			$this->template( 'photo/top-bar/nav/next' );
		} else {
			$this->template( 'photo/top-bar/nav/next-disabled' );
		}
		?>
	</ul>
</nav>
