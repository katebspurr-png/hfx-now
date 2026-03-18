<?php
/**
 * Template part: Category filter chip bar.
 *
 * @package Flavor2
 */

$categories = array(
	'All',
	'This Weekend',
	'Free',
	'Music',
	'Arts & Culture',
	'Comedy',
	'Community',
	'Food & Drink',
	'Outdoors',
	'Sports',
	'Family',
	'Film',
);
?>
<div class="filter-bar">
  <span class="filter-bar-label">Filter:</span>
  <?php foreach ( $categories as $cat ) : ?>
    <button class="chip<?php echo ( 'All' === $cat ) ? ' on' : ''; ?>" aria-pressed="<?php echo ( 'All' === $cat ) ? 'true' : 'false'; ?>"><?php echo esc_html( $cat ); ?></button>
  <?php endforeach; ?>
</div>
