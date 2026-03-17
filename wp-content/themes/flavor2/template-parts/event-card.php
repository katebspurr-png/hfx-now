<?php
/**
 * Template part: Single event card for the grid view.
 *
 * Expected variables (set before get_template_part):
 *   $flavor2_event — WP_Post object (tribe_events)
 *   $flavor2_wide  — bool, whether to render as wide/featured card
 *
 * @package Flavor2
 */

$event = isset( $flavor2_event ) ? $flavor2_event : ( isset( $args['event'] ) ? $args['event'] : null );
$wide  = isset( $flavor2_wide )  ? $flavor2_wide  : ( isset( $args['wide'] )  ? $args['wide']  : false );

if ( ! $event ) {
	return;
}

$has_tribe = function_exists( 'tribe_get_start_date' );
$cats      = get_the_terms( $event->ID, 'tribe_events_cat' );
$cat       = ( $cats && ! is_wp_error( $cats ) ) ? $cats[0]->name : '';
$when      = $has_tribe ? tribe_get_start_date( $event->ID, false, 'l, F j' ) : '';
$venue     = $has_tribe ? tribe_get_venue( $event->ID ) : '';
$time      = $has_tribe ? tribe_get_start_date( $event->ID, false, 'g:i A' ) : '';
$cost      = $has_tribe ? tribe_get_cost( $event->ID, true ) : '';
$is_free   = ( stripos( $cost, 'free' ) !== false || empty( $cost ) );
$permalink = get_permalink( $event );

$badge_class = $is_free ? 'free' : 'paid';
if ( $wide ) {
	$badge_class = 'white';
	$badge_text  = $is_free ? 'Free' : esc_html( $cost );
	if ( $time ) {
		$badge_text .= ' &middot; ' . esc_html( $time );
	}
} else {
	$badge_text = $is_free ? 'Free' : esc_html( $cost );
}

$venue_label = $venue;
if ( ! $wide && $time ) {
	$venue_label .= ' &middot; ' . $time;
}
?>
<a href="<?php echo esc_url( $permalink ); ?>" class="ec<?php echo $wide ? ' wide' : ''; ?>" data-category="<?php echo esc_attr( strtolower( $cat ) ); ?>" data-cost="<?php echo $is_free ? 'free' : 'paid'; ?>">
  <div class="ec-when"><?php echo esc_html( $when ); ?></div>
  <?php if ( $cat ) : ?>
    <div class="ec-cat"><?php echo esc_html( $cat ); ?></div>
  <?php endif; ?>
  <div class="ec-title"><?php echo esc_html( get_the_title( $event ) ); ?></div>
  <div class="ec-footer">
    <span class="ec-venue"><?php echo $venue_label; ?></span>
    <span class="badge <?php echo esc_attr( $badge_class ); ?>"><?php echo $badge_text; ?></span>
  </div>
</a>
