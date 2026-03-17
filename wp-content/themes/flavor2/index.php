<?php
/**
 * Generic fallback template.
 *
 * @package Flavor2
 */

get_header();
?>

<div class="page">

  <?php if ( have_posts() ) : ?>

    <div class="sec-head">
      <div class="sec-title">
        <?php
        if ( is_search() ) {
          printf( 'Search Results for &ldquo;%s&rdquo;', esc_html( get_search_query() ) );
        } elseif ( is_archive() ) {
          the_archive_title();
        } else {
          echo 'Latest';
        }
        ?>
      </div>
    </div>

    <div class="event-list">
      <?php while ( have_posts() ) : the_post(); ?>
        <div class="eli">
          <div class="eli-date">
            <div class="eli-day"><?php echo esc_html( get_the_date( 'j' ) ); ?></div>
            <div class="eli-mon"><?php echo esc_html( get_the_date( 'M' ) ); ?></div>
          </div>
          <div>
            <div class="eli-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></div>
            <div class="eli-meta"><?php the_excerpt(); ?></div>
          </div>
        </div>
      <?php endwhile; ?>
    </div>

    <?php the_posts_pagination(); ?>

  <?php else : ?>
    <p>Nothing found.</p>
  <?php endif; ?>

</div>

<?php get_footer(); ?>
