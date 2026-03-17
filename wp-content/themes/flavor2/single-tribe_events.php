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

<section class="hero" style="padding:40px 40px 36px;">
  <div class="hero-left">
    <?php if ( $cat ) : ?>
      <div class="hero-eyebrow"><?php echo esc_html( $cat ); ?></div>
    <?php endif; ?>
    <h1 style="font-size:52px; margin-bottom:16px;"><?php the_title(); ?></h1>
    <p class="hero-desc" style="max-width:480px; opacity:0.65;">
      <?php echo esc_html( $date ); ?>
      <?php if ( $start ) : ?>
        &middot; <?php echo esc_html( $start ); ?><?php if ( $end ) echo ' &ndash; ' . esc_html( $end ); ?>
      <?php endif; ?>
      <?php if ( $venue ) : ?>
        &middot; <?php echo esc_html( $venue ); ?>
      <?php endif; ?>
    </p>
  </div>
  <div class="hero-right" style="align-items:flex-end;">
    <span class="badge <?php echo $is_free ? 'free' : 'paid'; ?>" style="font-size:14px; padding:6px 14px;">
      <?php echo esc_html( $is_free ? 'Free' : $cost ); ?>
    </span>
  </div>
</section>

<div class="page" style="max-width:820px;">

  <?php if ( has_post_thumbnail() ) : ?>
    <div style="margin-bottom:32px;">
      <?php the_post_thumbnail( 'large', array( 'style' => 'width:100%; height:auto; display:block; border:1.5px solid var(--black);' ) ); ?>
    </div>
  <?php endif; ?>

  <div class="event-single-content" style="font-size:16px; line-height:1.75; margin-bottom:40px;">
    <?php the_content(); ?>
  </div>

  <!-- Event details sidebar-style block -->
  <div style="border:1.5px solid var(--black); padding:24px 28px; margin-bottom:40px;">
    <div class="sec-title" style="font-size:18px; margin-bottom:16px;">Event Details</div>

    <?php if ( $date ) : ?>
      <div style="margin-bottom:12px;">
        <strong style="font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; font-size:10px; letter-spacing:0.14em; color:var(--muted);">Date</strong><br>
        <?php echo esc_html( $date ); ?>
      </div>
    <?php endif; ?>

    <?php if ( $start ) : ?>
      <div style="margin-bottom:12px;">
        <strong style="font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; font-size:10px; letter-spacing:0.14em; color:var(--muted);">Time</strong><br>
        <?php echo esc_html( $start ); ?><?php if ( $end ) echo ' &ndash; ' . esc_html( $end ); ?>
      </div>
    <?php endif; ?>

    <?php if ( $venue ) : ?>
      <div style="margin-bottom:12px;">
        <strong style="font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; font-size:10px; letter-spacing:0.14em; color:var(--muted);">Venue</strong><br>
        <?php echo esc_html( $venue ); ?>
        <?php if ( $address ) : ?>
          <br><span style="font-size:13px; color:var(--muted);"><?php echo esc_html( $address ); ?></span>
        <?php endif; ?>
        <?php if ( $map_link ) : ?>
          <br><a href="<?php echo esc_url( $map_link ); ?>" target="_blank" rel="noopener" style="font-size:13px; color:var(--blue);">View Map &rarr;</a>
        <?php endif; ?>
      </div>
    <?php endif; ?>

    <?php if ( $cost ) : ?>
      <div>
        <strong style="font-family:'Barlow Condensed',sans-serif; text-transform:uppercase; font-size:10px; letter-spacing:0.14em; color:var(--muted);">Cost</strong><br>
        <?php echo esc_html( $cost ); ?>
      </div>
    <?php endif; ?>
  </div>

  <div style="margin-bottom:40px;">
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="sec-link">&larr; Back to All Events</a>
  </div>

</div>

<?php endif; ?>

<?php get_footer(); ?>
