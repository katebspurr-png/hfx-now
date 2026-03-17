<?php
/**
 * 404 template.
 *
 * @package Flavor2
 */

get_header();
?>

<div class="page page--404">
  <h1>404</h1>
  <div class="sec-title">Page Not Found</div>
  <p>
    The page you're looking for doesn't exist or has been moved. Let's get you back to discovering events.
  </p>
  <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="btn-primary">Back to Home</a>
</div>

<?php get_footer(); ?>
