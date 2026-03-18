<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<!-- NAV -->
<nav>
  <a href="<?php echo esc_url( home_url( '/' ) ); ?>" class="nav-logo">
    <div class="smiley">
      <svg width="42" height="42" viewBox="0 0 42 42" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" focusable="false">
        <circle cx="21" cy="21" r="19" stroke="#1A0FCC" stroke-width="2.2" fill="none"/>
        <line x1="15" y1="13" x2="15" y2="19.5" stroke="#1A0FCC" stroke-width="2.2" stroke-linecap="round"/>
        <line x1="21" y1="11" x2="21" y2="17.5" stroke="#1A0FCC" stroke-width="2.2" stroke-linecap="round"/>
        <path d="M12.5 27 Q21 34 29.5 27" stroke="#1A0FCC" stroke-width="2.2" stroke-linecap="round" fill="none"/>
      </svg>
    </div>
    <div class="logo-lockup">
      <div class="logo-name"><?php bloginfo( 'name' ); ?></div>
      <div class="logo-tag"><?php bloginfo( 'description' ); ?></div>
    </div>
  </a>

  <button class="nav-toggle" aria-label="Menu" aria-expanded="false">
    <span></span><span></span><span></span>
  </button>

  <?php if ( has_nav_menu( 'primary' ) ) : ?>
    <?php
    wp_nav_menu( array(
      'theme_location' => 'primary',
      'container'      => false,
      'menu_class'     => 'nav-links',
      'items_wrap'     => '<ul class="%2$s">%3$s</ul>',
      'walker'         => new Flavor2_Nav_Walker(),
      'depth'          => 1,
    ) );
    ?>
  <?php else : ?>
    <ul class="nav-links">
      <li><a href="<?php echo esc_url( home_url( '/today/' ) ); ?>">Today</a></li>
      <li><a href="<?php echo esc_url( home_url( '/events/' ) ); ?>">Events</a></li>
      <li><a href="<?php echo esc_url( home_url( '/events/this-weekend/' ) ); ?>">This Weekend</a></li>
      <li><a href="<?php echo esc_url( home_url( '/events/category/free/' ) ); ?>">Free</a></li>
      <li><a href="<?php echo esc_url( home_url( '/venues/' ) ); ?>">Venues</a></li>
      <li class="cta"><a href="<?php echo esc_url( home_url( '/submit-event/' ) ); ?>">Submit Event</a></li>
    </ul>
  <?php endif; ?>
</nav>
