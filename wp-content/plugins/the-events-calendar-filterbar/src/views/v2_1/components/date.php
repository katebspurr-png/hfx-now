<?php
/**
 * View: Date Component
 *
 * Override this template in your own theme by creating a file at:
 * [your-theme]/tribe/events-filterbar/v2_1/components/date.php
 *
 * See more documentation about our views templating system.
 *
 * @link http://evnt.is/1aiy
 *
 * @var string  $label Label for the calendar input.
 * @var string  $value Value for the calendar input.
 * @var string  $id    ID of the calendar input.
 * @var string  $name  Name attribute for the calendar input.
 *
 * @version 5.6.0
 */

?>

<div
	class="tribe-filter-bar-c-date"
>
	<input
		class="tribe-filter-bar-c-date__input"
		id="<?php echo esc_attr( $id ); ?>"
		name="<?php echo esc_attr( $name ); ?>"
		type="date"
		value="<?php echo esc_attr( $value ); ?>"
		data-js="tribe-filter-bar-c-date-input"
	/>
</div>
