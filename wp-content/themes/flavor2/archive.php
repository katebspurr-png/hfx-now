<?php
/**
 * Archive template — used for event archives, category archives, etc.
 *
 * @package Flavor2
 */

get_header();

get_template_part( 'template-parts/filter-bar' );
?>

<div class="page">

  <div class="sec-head">
    <div class="sec-title">
      <?php
      if ( is_post_type_archive( 'tribe_events' ) ) {
        echo 'All Events';
      } else {
        the_archive_title();
      }
      ?>
    </div>
    <?php if ( ! is_post_type_archive( 'tribe_events' ) ) : ?>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="sec-link">All Events &rarr;</a>
    <?php endif; ?>
  </div>

  <?php if ( have_posts() ) : ?>
    <div class="event-list">
      <?php while ( have_posts() ) : the_post();
        $has_tribe = function_exists( 'tribe_get_start_date' );
        $cats      = get_the_terms( get_the_ID(), 'tribe_events_cat' );
        $cat       = ( $cats && ! is_wp_error( $cats ) ) ? $cats[0]->name : '';
        $day       = $has_tribe ? tribe_get_start_date( null, false, 'j' ) : get_the_date( 'j' );
        $month     = $has_tribe ? tribe_get_start_date( null, false, 'M' ) : get_the_date( 'M' );
        $time      = $has_tribe ? tribe_get_start_date( null, false, 'g:i A' ) : '';
        $venue     = $has_tribe ? tribe_get_venue() : '';
        $cost      = $has_tribe ? tribe_get_cost( null, true ) : '';
        $is_free   = ( stripos( $cost, 'free' ) !== false || empty( $cost ) );
      ?>
        <a href="<?php the_permalink(); ?>" class="eli" data-category="<?php echo esc_attr( strtolower( $cat ) ); ?>" data-cost="<?php echo $is_free ? 'free' : 'paid'; ?>">
          <div class="eli-date">
            <div class="eli-day"><?php echo esc_html( $day ); ?></div>
            <div class="eli-mon"><?php echo esc_html( $month ); ?></div>
          </div>
          <div>
            <div class="eli-title"><?php the_title(); ?></div>
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
      <?php endwhile; ?>
    </div>

    <?php the_posts_pagination( array(
      'prev_text' => '&larr; Previous',
      'next_text' => 'Next &rarr;',
    ) ); ?>

  <?php else : ?>
    <p class="no-events">No events found.</p>
  <?php endif; ?>

</div>

<?php get_footer(); ?>
