<?php
/**
 * 404 template.
 *
 * @package Flavor2
 */

get_header();
?>

<div class="page" style="text-align:center; padding-top:80px; padding-bottom:80px;">
  <h1 style="font-family:'Barlow Condensed',sans-serif; font-weight:900; font-size:120px; color:var(--blue); line-height:1; margin-bottom:16px;">404</h1>
  <div class="sec-title" style="display:inline; border:none;">Page Not Found</div>
  <p style="color:var(--muted); margin:16px 0 28px; max-width:360px; margin-left:auto; margin-right:auto;">
    The page you're looking for doesn't exist or has been moved. Let's get you back to discovering events.
  </p>
  <a href="<?php echo esc_url( home_url( '/' ) ); ?>" style="font-family:'Barlow Condensed',sans-serif; font-weight:700; font-size:13px; letter-spacing:0.1em; text-transform:uppercase; background:var(--blue); color:var(--white); padding:12px 24px; text-decoration:none; display:inline-block; transition:background 0.12s;">Back to Home</a>
</div>

<?php get_footer(); ?>
