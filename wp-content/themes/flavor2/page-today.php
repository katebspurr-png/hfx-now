<?php
/**
 * Template Name: Today
 *
 * Displays today's events with a featured highlight at the top.
 *
 * @package Flavor2
 */

get_header();

$has_tribe   = function_exists( 'tribe_get_events' );
$today_start = wp_date( 'Y-m-d 00:00:00' );
$today_end   = wp_date( 'Y-m-d 23:59:59' );
$today_label = wp_date( 'l, F j' );
$events      = array();

if ( $has_tribe ) {
	$events = tribe_get_events( array(
		'posts_per_page' => -1,
		'start_date'     => $today_start,
		'end_date'       => $today_end,
		'orderby'        => 'event_date',
		'order'          => 'ASC',
	) );
}

$featured  = ! empty( $events ) ? $events[0] : null;
$remaining = ! empty( $events ) ? array_slice( $events, 1 ) : array();
?>

<!-- Hero -->
<section class="hero hero--today">
  <div class="hero-left">
    <div class="hero-eyebrow">Today in Halifax</div>
    <h1><?php echo esc_html( $today_label ); ?></h1>
    <p class="hero-desc">
      <?php
      $count = count( $events );
      if ( $count > 0 ) {
        printf( '%d %s happening today.', $count, $count === 1 ? 'event' : 'events' );
      } else {
        echo 'Check back soon for upcoming events.';
      }
      ?>
    </p>
  </div>
</section>

<div class="page">

<?php if ( $featured ) :
	$f_cats    = get_the_terms( $featured->ID, 'tribe_events_cat' );
	$f_cat     = ( $f_cats && ! is_wp_error( $f_cats ) ) ? $f_cats[0]->name : '';
	$f_time    = $has_tribe ? tribe_get_start_date( $featured->ID, false, 'g:i A' ) : '';
	$f_venue   = $has_tribe ? tribe_get_venue( $featured->ID ) : '';
	$f_cost    = $has_tribe ? tribe_get_cost( $featured->ID, true ) : '';
	$f_is_free = ( stripos( $f_cost, 'free' ) !== false || empty( $f_cost ) );
?>

  <!-- Featured Event -->
  <div class="sec-head">
    <div class="sec-title">Featured</div>
  </div>

  <a href="<?php echo esc_url( get_permalink( $featured ) ); ?>" class="today-featured">
    <?php if ( has_post_thumbnail( $featured ) ) : ?>
      <div class="today-featured-img">
        <?php echo get_the_post_thumbnail( $featured, 'large' ); ?>
      </div>
    <?php endif; ?>
    <div class="today-featured-body">
      <?php if ( $f_cat ) : ?>
        <div class="ec-cat"><?php echo esc_html( $f_cat ); ?></div>
      <?php endif; ?>
      <div class="today-featured-title"><?php echo esc_html( get_the_title( $featured ) ); ?></div>
      <div class="today-featured-meta">
        <?php if ( $f_time ) : ?>
          <span><?php echo esc_html( $f_time ); ?></span>
        <?php endif; ?>
        <?php if ( $f_venue ) : ?>
          <span class="dot"></span>
          <span><?php echo esc_html( $f_venue ); ?></span>
        <?php endif; ?>
      </div>
      <span class="badge <?php echo $f_is_free ? 'free' : 'paid'; ?>">
        <?php echo esc_html( $f_is_free ? 'Free' : $f_cost ); ?>
      </span>
    </div>
  </a>

<?php endif; ?>

<?php if ( ! empty( $remaining ) ) : ?>

  <!-- Rest of Today's Events -->
  <div class="sec-head">
    <div class="sec-title">Also Today</div>
    <span class="sec-link"><?php echo count( $remaining ); ?> more</span>
  </div>

  <div class="event-list">
    <?php foreach ( $remaining as $event ) :
      get_template_part( 'template-parts/event-list-item', null, array(
        'event' => $event,
      ) );
    endforeach; ?>
  </div>

<?php elseif ( empty( $events ) ) : ?>

  <?php /* ── Static fallback when no events plugin ── */ ?>
  <div class="sec-head">
    <div class="sec-title">Featured</div>
  </div>

  <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="today-featured">
    <div class="today-featured-body">
      <div class="ec-cat">Live Music</div>
      <div class="today-featured-title">Halifax Jazz Festival Opening Night</div>
      <div class="today-featured-meta">
        <span>7:00 PM</span>
        <span class="dot"></span>
        <span>The Carleton, Argyle St</span>
      </div>
      <span class="badge free">Free</span>
    </div>
  </a>

  <div class="sec-head">
    <div class="sec-title">Also Today</div>
    <span class="sec-link">4 more</span>
  </div>

  <div class="event-list">
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="comedy" data-cost="paid">
      <div class="eli-date"><div class="eli-day"><?php echo esc_html( wp_date( 'j' ) ); ?></div><div class="eli-mon"><?php echo esc_html( wp_date( 'M' ) ); ?></div></div>
      <div><div class="eli-title">Stand-Up Showcase</div>
      <div class="eli-meta"><span>9:00 PM</span><span class="dot"></span><span>Yuk Yuk's</span><span class="dot"></span><span>Comedy</span></div></div>
      <div class="eli-cost">$15</div>
    </a>
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="arts &amp; culture" data-cost="free">
      <div class="eli-date"><div class="eli-day"><?php echo esc_html( wp_date( 'j' ) ); ?></div><div class="eli-mon"><?php echo esc_html( wp_date( 'M' ) ); ?></div></div>
      <div><div class="eli-title">AGNS First Fridays Opening</div>
      <div class="eli-meta"><span>6:00 PM</span><span class="dot"></span><span>Art Gallery of NS</span><span class="dot"></span><span>Arts</span></div></div>
      <div class="eli-cost">Free</div>
    </a>
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="community" data-cost="free">
      <div class="eli-date"><div class="eli-day"><?php echo esc_html( wp_date( 'j' ) ); ?></div><div class="eli-mon"><?php echo esc_html( wp_date( 'M' ) ); ?></div></div>
      <div><div class="eli-title">2037 Gottingen &mdash; Community Open Mic</div>
      <div class="eli-meta"><span>6:00 PM</span><span class="dot"></span><span>2037 Gottingen St</span><span class="dot"></span><span>Community</span></div></div>
      <div class="eli-cost">Free</div>
    </a>
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="food &amp; drink" data-cost="free">
      <div class="eli-date"><div class="eli-day"><?php echo esc_html( wp_date( 'j' ) ); ?></div><div class="eli-mon"><?php echo esc_html( wp_date( 'M' ) ); ?></div></div>
      <div><div class="eli-title">Propeller Brewery Tap Takeover</div>
      <div class="eli-meta"><span>2:00 PM</span><span class="dot"></span><span>Propeller Brewing</span><span class="dot"></span><span>Food &amp; Drink</span></div></div>
      <div class="eli-cost">Free</div>
    </a>
  </div>

<?php endif; ?>

  <div class="back-link">
    <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="sec-link">&larr; Back to Home</a>
  </div>

</div>

<?php get_footer(); ?>
