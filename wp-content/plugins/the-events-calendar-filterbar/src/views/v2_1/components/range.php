<?php
/**
 * View: Range Component
 *
 * Override this template in your own theme by creating a file at:
 * [your-theme]/tribe/events-filterbar/v2_1/components/range.php
 *
 * See more documentation about our views templating system.
 *
 * @link http://evnt.is/1aiy
 *
 * @version 5.5.10
 *
 * @since 5.0.0
 * @since 5.5.10 Added keyboard navigation.
 *
 * @var string  $label Label for the range.
 * @var string  $value Value for the range.
 * @var string  $id    ID of the range.
 * @var string  $name  Name attribute for the range.
 * @var string  $min   Min value for the range.
 * @var string  $max   Max value for the range.
 *
 */
?>
<div
	class="tribe-filter-bar-c-range"
	role="group"
	aria-labelledby="<?php echo esc_attr( $id ); ?>-label"
>
	<label
		class="tribe-filter-bar-c-range__label"
		for="<?php echo esc_attr( $id ); ?>"
		id="<?php echo esc_attr( $id ); ?>-label"
	>
		<?php echo esc_html( $label ); ?>
	</label>
	<input
		class="tribe-filter-bar-c-range__input"
		id="<?php echo esc_attr( $id ); ?>"
		name="<?php echo esc_attr( $name ); ?>"
		type="hidden"
		value="<?php echo esc_attr( $value ); ?>"
		aria-hidden="true"
	/>
	<div
		class="tribe-filter-bar-c-range__slider"
		data-js="tribe-filter-bar-c-range-slider"
		data-min="<?php echo esc_attr( $min ); ?>"
		data-max="<?php echo esc_attr( $max ); ?>"
		role="slider"
		aria-valuemin="<?php echo esc_attr( $min ); ?>"
		aria-valuemax="<?php echo esc_attr( $max ); ?>"
		aria-valuenow="<?php echo esc_attr( $value ); ?>"
		aria-label="<?php echo esc_attr( $label ); ?>"
		tabindex="0"
	>
	</div>
</div>
