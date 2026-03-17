<?php
/**
 * Search results template.
 *
 * @package Flavor2
 */

get_header();
?>

<div class="page">

  <div class="sec-head">
    <div class="sec-title">
      <?php printf( 'Results for &ldquo;%s&rdquo;', esc_html( get_search_query() ) ); ?>
    </div>
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="sec-link">All Events &rarr;</a>
  </div>

  <?php if ( have_posts() ) : ?>
    <div class="event-list">
      <?php while ( have_posts() ) : the_post();
        $has_tribe = function_exists( 'tribe_get_start_date' );
        $is_event  = ( 'tribe_events' === get_post_type() );
        $cats      = $is_event ? get_the_terms( get_the_ID(), 'tribe_events_cat' ) : false;
        $cat       = ( $cats && ! is_wp_error( $cats ) ) ? $cats[0]->name : '';
        $day       = ( $is_event && $has_tribe ) ? tribe_get_start_date( null, false, 'j' ) : get_the_date( 'j' );
        $month     = ( $is_event && $has_tribe ) ? tribe_get_start_date( null, false, 'M' ) : get_the_date( 'M' );
        $time      = ( $is_event && $has_tribe ) ? tribe_get_start_date( null, false, 'g:i A' ) : '';
        $venue     = ( $is_event && $has_tribe ) ? tribe_get_venue() : '';
        $cost      = ( $is_event && $has_tribe ) ? tribe_get_cost( null, true ) : '';
      ?>
        <a href="<?php the_permalink(); ?>" class="eli">
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
              <?php elseif ( ! $is_event ) : ?>
                <span><?php echo esc_html( get_post_type_object( get_post_type() )->labels->singular_name ); ?></span>
              <?php endif; ?>
            </div>
          </div>
          <div class="eli-cost"><?php echo esc_html( $cost ?: '' ); ?></div>
        </a>
      <?php endwhile; ?>
    </div>

    <?php the_posts_pagination( array(
      'prev_text' => '&larr; Previous',
      'next_text' => 'Next &rarr;',
    ) ); ?>

  <?php else : ?>
    <div style="padding:60px 0; text-align:center;">
      <div class="sec-title" style="border:none; margin-bottom:12px;">No results found</div>
      <p style="color:var(--muted); margin-bottom:24px;">Try a different search term or browse all events.</p>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="sec-link">Browse Events &rarr;</a>
    </div>
  <?php endif; ?>

</div>

<?php get_footer(); ?>
