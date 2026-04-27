<?php
/**
 * Template Name: Venues
 *
 * @package HalifaxNowBroadsheet
 */

get_header();

$events         = hfx_get_events_payload(250);
$grouped_venues = array();
foreach ($events as $event) {
	$key = $event['venue'];
	if (!isset($grouped_venues[ $key ])) {
		$grouped_venues[ $key ] = array();
	}
	$grouped_venues[ $key ][] = $event;
}
ksort($grouped_venues);
?>
<div class="v4-root bvn-root">
	<?php hfx_render_broadsheet_nav('venues'); ?>
	<section class="v4-sec bvn-wrap">
		<a class="bvn-back" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('← Back', 'halifax-now-broadsheet'); ?></a>
		<div class="bvn-hero">
			<div class="bvn-hero-img hfx-img-fallback"></div>
			<div class="bvn-hero-overlay"></div>
			<div class="bvn-hero-content">
				<div class="bvn-kicker"><?php esc_html_e('Venue profile', 'halifax-now-broadsheet'); ?></div>
				<h1 class="bvn-name"><?php esc_html_e('Know the room.', 'halifax-now-broadsheet'); ?></h1>
				<p class="bvn-lede"><?php esc_html_e("One of Halifax's go-to event venues. Check the calendar for what's coming up.", 'halifax-now-broadsheet'); ?></p>
			</div>
		</div>

		<?php foreach ($grouped_venues as $venue => $venue_events) : ?>
			<article class="hfx-venue-block bvn-box">
				<div class="v4-sec-hd bvn-sec-hd">
					<div class="h"><?php esc_html_e('Upcoming at', 'halifax-now-broadsheet'); ?> <em><?php echo esc_html($venue); ?></em><span class="count"><?php echo esc_html(count($venue_events)); ?></span></div>
				</div>
				<div class="v4-list bvn-grid">
					<?php foreach (array_slice($venue_events, 0, 8) as $event) : ?>
						<a class="v4-item bvn-item" href="<?php echo esc_url($event['url']); ?>">
							<div class="v4-item-date bvn-item-date">
								<div class="n"><?php echo esc_html(date_i18n('j', strtotime($event['date']))); ?></div>
								<div class="m"><?php echo esc_html(date_i18n('M', strtotime($event['date']))); ?></div>
							</div>
							<div>
								<div class="v4-item-cat bvn-item-cat"><?php echo esc_html( hfx_event_category_label( $event ) ); ?></div>
								<div class="v4-item-t bvn-item-t"><?php echo esc_html($event['title']); ?></div>
								<div class="v4-item-m bvn-item-m"><?php echo esc_html($event['time'] . ' · ' . $event['hood']); ?></div>
							</div>
							<div class="v4-item-price bvn-item-price <?php echo $event['price'] === 'paid' ? 'paid' : ''; ?>"><?php echo esc_html($event['priceLabel']); ?></div>
						</a>
					<?php endforeach; ?>
				</div>
			</article>
		<?php endforeach; ?>
	</section>
</div>
<?php
get_footer();
