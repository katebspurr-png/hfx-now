<!-- MARQUEE -->
<?php get_template_part( 'template-parts/marquee' ); ?>

<!-- FOOTER -->
<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand">
        <div class="fn"><?php bloginfo( 'name' ); ?></div>
        <div class="ft"><?php bloginfo( 'description' ); ?></div>
      </div>
      <div class="footer-cols">
        <div class="footer-col">
          <div class="footer-col-head">Browse</div>
          <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>">All Events</a>
          <a href="<?php echo esc_url( home_url( '/events/this-weekend/' ) ); ?>">This Weekend</a>
          <a href="<?php echo esc_url( home_url( '/events/category/free/' ) ); ?>">Free Events</a>
          <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>">By Category</a>
          <a href="<?php echo esc_url( home_url( '/venues/' ) ); ?>">By Venue</a>
        </div>
        <div class="footer-col">
          <div class="footer-col-head">Info</div>
          <a href="<?php echo esc_url( home_url( '/submit-event/' ) ); ?>">Submit an Event</a>
          <a href="<?php echo esc_url( home_url( '/about/' ) ); ?>">About Halifax Now</a>
          <a href="<?php echo esc_url( home_url( '/contact/' ) ); ?>">Contact</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <span>&copy; <?php echo esc_html( date( 'Y' ) ); ?> <?php bloginfo( 'name' ); ?> &mdash; Built for Haligonians, by Haligonians</span>
      <span class="footer-smiley">&#9786;</span>
    </div>
  </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
