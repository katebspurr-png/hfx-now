<?php
/**
 * Single event template for The Events Calendar.
 *
 * @package Flavor2
 */

get_header();

if ( have_posts() ) : the_post();

$has_tribe = function_exists( 'tribe_get_start_date' );
$cats      = get_the_terms( get_the_ID(), 'tribe_events_cat' );
$cat       = ( $cats && ! is_wp_error( $cats ) ) ? $cats[0]->name : '';
$venue     = $has_tribe ? tribe_get_venue() : '';
$address   = $has_tribe ? tribe_get_full_address() : '';
$date      = $has_tribe ? tribe_get_start_date( null, true, 'l, F j, Y' ) : '';
$start     = $has_tribe ? tribe_get_start_date( null, false, 'g:i A' ) : '';
$end       = $has_tribe ? tribe_get_end_date( null, false, 'g:i A' ) : '';
$cost      = $has_tribe ? tribe_get_cost( null, true ) : '';
$is_free   = ( stripos( $cost, 'free' ) !== false || empty( $cost ) );
$map_link  = $has_tribe ? tribe_get_map_link() : '';
?>

<section class="hero hero--single">
  <div class="hero-left">
    <?php if ( $cat ) : ?>
      <div class="hero-eyebrow"><?php echo esc_html( $cat ); ?></div>
    <?php endif; ?>
    <h1><?php the_title(); ?></h1>
    <p class="hero-desc">
      <?php echo esc_html( $date ); ?>
      <?php if ( $start ) : ?>
        &middot; <?php echo esc_html( $start ); ?><?php if ( $end ) echo ' &ndash; ' . esc_html( $end ); ?>
      <?php endif; ?>
      <?php if ( $venue ) : ?>
        &middot; <?php echo esc_html( $venue ); ?>
      <?php endif; ?>
    </p>
  </div>
  <div class="hero-right">
    <span class="badge <?php echo $is_free ? 'free' : 'paid'; ?>">
      <?php echo esc_html( $is_free ? 'Free' : $cost ); ?>
    </span>
  </div>
</section>

<div class="page page--narrow">

  <?php if ( has_post_thumbnail() ) : ?>
    <div class="event-thumb">
      <?php the_post_thumbnail( 'large' ); ?>
    </div>
  <?php endif; ?>

  <div class="event-single-content">
    <?php the_content(); ?>
  </div>

  <!-- Event details sidebar-style block -->
  <div class="event-details-box">
    <div class="sec-title">Event Details</div>

    <?php if ( $date ) : ?>
      <div class="detail-item">
        <strong class="detail-label">Date</strong><br>
        <?php echo esc_html( $date ); ?>
      </div>
    <?php endif; ?>

    <?php if ( $start ) : ?>
      <div class="detail-item">
        <strong class="detail-label">Time</strong><br>
        <?php echo esc_html( $start ); ?><?php if ( $end ) echo ' &ndash; ' . esc_html( $end ); ?>
      </div>
    <?php endif; ?>

    <?php if ( $venue ) : ?>
      <div class="detail-item">
        <strong class="detail-label">Venue</strong><br>
        <?php echo esc_html( $venue ); ?>
        <?php if ( $address ) : ?>
          <br><span class="detail-address"><?php echo esc_html( $address ); ?></span>
        <?php endif; ?>
        <?php if ( $map_link ) : ?>
          <br><a href="<?php echo esc_url( $map_link ); ?>" target="_blank" rel="noopener" class="detail-map">View Map &rarr;</a>
        <?php endif; ?>
      </div>
    <?php endif; ?>

    <?php if ( $cost ) : ?>
      <div class="detail-item">
        <strong class="detail-label">Cost</strong><br>
        <?php echo esc_html( $cost ); ?>
      </div>
    <?php endif; ?>
  </div>

  <div class="back-link">
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="sec-link">&larr; Back to All Events</a>
  </div>

</div>

<?php endif; ?>

<?php get_footer(); ?>
