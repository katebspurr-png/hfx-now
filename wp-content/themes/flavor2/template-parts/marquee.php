<?php
/**
 * Template part: Scrolling marquee band.
 *
 * @package Flavor2
 */

$items = array(
	'Do Stuff',
	'Have Fun',
	'Halifax Events',
	'700+ Events Listed',
	'No Instagram Required',
	'Free & Paid',
	'Updated Daily',
);
?>
<div class="marquee-band">
  <div class="marquee-track">
    <?php /* Duplicate the set so the scroll loops seamlessly */ ?>
    <?php for ( $r = 0; $r < 2; $r++ ) : ?>
      <?php foreach ( $items as $item ) : ?>
        <span class="marquee-item"><?php echo esc_html( $item ); ?> <span class="star">&#9733;</span></span>
      <?php endforeach; ?>
    <?php endfor; ?>
  </div>
</div>
