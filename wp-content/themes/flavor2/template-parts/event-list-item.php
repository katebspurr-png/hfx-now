<?php
/**
 * Template part: Single event row for the list view.
 *
 * Expected: $args['event'] — WP_Post (tribe_events)
 *
 * @package Flavor2
 */

$event = isset( $args['event'] ) ? $args['event'] : null;

if ( ! $event ) {
	return;
}

$has_tribe = function_exists( 'tribe_get_start_date' );
$cats      = get_the_terms( $event->ID, 'tribe_events_cat' );
$cat       = ( $cats && ! is_wp_error( $cats ) ) ? $cats[0]->name : '';
$day       = $has_tribe ? tribe_get_start_date( $event->ID, false, 'j' ) : '';
$month     = $has_tribe ? tribe_get_start_date( $event->ID, false, 'M' ) : '';
$time      = $has_tribe ? tribe_get_start_date( $event->ID, false, 'g:i A' ) : '';
$venue     = $has_tribe ? tribe_get_venue( $event->ID ) : '';
$cost      = $has_tribe ? tribe_get_cost( $event->ID, true ) : '';
$permalink = get_permalink( $event );
?>
<a href="<?php echo esc_url( $permalink ); ?>" class="eli">
  <div class="eli-date">
    <div class="eli-day"><?php echo esc_html( $day ); ?></div>
    <div class="eli-mon"><?php echo esc_html( $month ); ?></div>
  </div>
  <div>
    <div class="eli-title"><?php echo esc_html( get_the_title( $event ) ); ?></div>
    <div class="eli-meta">
      <?php if ( $time ) : ?>
        <span><?php echo esc_html( $time ); ?></span><span class="dot"></span>
      <?php endif; ?>
      <?php if ( $venue ) : ?>
        <span><?php echo esc_html( $venue ); ?></span><span class="dot"></span>
      <?php endif; ?>
      <?php if ( $cat ) : ?>
        <span><?php echo esc_html( $cat ); ?></span>
      <?php endif; ?>
    </div>
  </div>
  <div class="eli-cost"><?php echo esc_html( $cost ?: 'Free' ); ?></div>
</a>
