<?php
/**
 * Template part: "Best This Weekend" featured picks in the hero.
 *
 * Queries upcoming events and displays up to 4 as pick-cards.
 * Falls back to static placeholder content when The Events Calendar is not active.
 *
 * @package Flavor2
 */

$has_tribe = function_exists( 'tribe_get_events' );

if ( $has_tribe ) {
	$picks = tribe_get_events( array(
		'posts_per_page' => 4,
		'start_date'     => 'now',
		'end_date'       => wp_date( 'Y-m-d', strtotime( 'next Sunday 23:59' ) ),
		'orderby'        => 'event_date',
		'order'          => 'ASC',
	) );
} else {
	$picks = array();
}
?>
<div class="picks-label">&#11088; Best This Weekend</div>

<?php if ( ! empty( $picks ) ) : ?>
	<?php foreach ( $picks as $i => $pick ) :
		$is_top  = ( 0 === $i );
		$cats    = get_the_terms( $pick->ID, 'tribe_events_cat' );
		$cat     = ( $cats && ! is_wp_error( $cats ) ) ? $cats[0]->name : '';
		$venue   = tribe_get_venue( $pick->ID );
		$cost    = tribe_get_cost( $pick->ID, true );
		$date    = tribe_get_start_date( $pick->ID, false, 'D M j' );
		$time    = tribe_get_start_date( $pick->ID, false, 'g:i A' );
		$meta    = implode( ' &middot; ', array_filter( array( $date, $time, $venue, $cost ) ) );
	?>
	<a href="<?php echo esc_url( get_permalink( $pick->ID ) ); ?>" class="pick-card<?php echo $is_top ? ' top' : ''; ?>">
		<div>
			<?php if ( $cat ) : ?>
				<div class="pc-cat"><?php echo esc_html( $cat ); ?></div>
			<?php endif; ?>
			<div class="pc-title"><?php echo esc_html( get_the_title( $pick ) ); ?></div>
			<div class="pc-meta"><?php echo esc_html( $meta ); ?></div>
		</div>
		<?php if ( $is_top ) : ?>
			<div class="pc-tag">Editor's Pick</div>
		<?php endif; ?>
	</a>
	<?php endforeach; ?>

<?php else : ?>
	<!-- Static fallback when no events are available -->
	<div class="pick-card top">
		<div>
			<div class="pc-cat">Live Music</div>
			<div class="pc-title">Jazz in the Garden with the HFX Quartet</div>
			<div class="pc-meta">Sat Mar 22 &middot; 7:00 PM &middot; The Carleton &middot; Free</div>
		</div>
		<div class="pc-tag">Editor's Pick</div>
	</div>
	<div class="pick-card">
		<div>
			<div class="pc-cat">Comedy</div>
			<div class="pc-title">Halifax Comedy Night</div>
			<div class="pc-meta">Fri Mar 21 &middot; 9:00 PM &middot; Yuk Yuk's &middot; $15</div>
		</div>
	</div>
	<div class="pick-card">
		<div>
			<div class="pc-cat">Community</div>
			<div class="pc-title">North End Farmers Market Opening Weekend</div>
			<div class="pc-meta">Sat&ndash;Sun &middot; 9 AM&ndash;1 PM &middot; Halifax Forum &middot; Free</div>
		</div>
		<div class="pc-tag">Family</div>
	</div>
	<div class="pick-card">
		<div>
			<div class="pc-cat">Film</div>
			<div class="pc-title">Carbon Arc: Cult Classics Night</div>
			<div class="pc-meta">Thu Mar 20 &middot; 8:00 PM &middot; Carbon Arc &middot; $12</div>
		</div>
	</div>
<?php endif; ?>
