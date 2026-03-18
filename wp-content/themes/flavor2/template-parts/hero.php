<?php
/**
 * Template part: Hero section with search and featured picks.
 *
 * @package Flavor2
 */
?>
<section class="hero">
  <div class="hero-left">
    <div class="hero-eyebrow">Halifax, Nova Scotia</div>
    <h1>Find your<br>next<br>thing.</h1>
    <p class="hero-desc">Halifax's most comprehensive event calendar. No Instagram scrolling, no FOMO &mdash; just everything happening near you.</p>
    <div class="search-bar">
      <form role="search" method="get" action="<?php echo esc_url( home_url( '/' ) ); ?>" class="search-form">
        <input type="text" name="s" placeholder="Search events, venues, artists..." value="<?php echo esc_attr( get_search_query() ); ?>">
        <input type="hidden" name="post_type" value="tribe_events">
        <button type="submit">Search</button>
      </form>
    </div>
  </div>
  <div class="hero-right">
    <?php get_template_part( 'template-parts/hero-picks' ); ?>
  </div>
</section>
