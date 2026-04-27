<?php
/**
 * Single venue template.
 *
 * @package HalifaxNowBroadsheet
 */

get_header();

the_post();
$venue_id = get_the_ID();
$venue_name = get_the_title();
$venue_address = '';
if (function_exists('tribe_get_full_address')) {
	$venue_address = (string) tribe_get_full_address($venue_id);
}
if ($venue_address === '') {
	$venue_address = (string) get_post_meta($venue_id, '_VenueAddress', true);
}
$venue_phone = (string) get_post_meta($venue_id, '_VenuePhone', true);
$events = array_values(array_filter(hfx_get_events_payload(250), static function ($event) use ($venue_name) {
	return isset($event['venue']) && 0 === strcasecmp((string) $event['venue'], (string) $venue_name);
}));
$upcoming_count = count($events);
$free_count = count(array_filter($events, static function ($event) {
	return isset($event['price']) && $event['price'] === 'free';
}));
$hood = '';
if (!empty($events[0]['hood'])) {
	$hood = (string) $events[0]['hood'];
}
?>
<div class="v4-root bvn-root">
	<?php hfx_render_broadsheet_nav('venues'); ?>
	<section class="v4-sec bvn-wrap">
		<a class="bvn-back" href="<?php echo esc_url(home_url('/venues/')); ?>"><?php esc_html_e('← Back', 'halifax-now-broadsheet'); ?></a>
		<div class="bvn-hero">
			<div class="bvn-hero-img hfx-img-fallback"></div>
			<div class="bvn-hero-overlay"></div>
			<div class="bvn-hero-content">
				<div class="bvn-kicker"><?php esc_html_e('Venue profile', 'halifax-now-broadsheet'); ?></div>
				<h1 class="bvn-name"><?php echo esc_html($venue_name); ?></h1>
				<p class="bvn-lede"><?php the_excerpt(); ?></p>
			</div>
		</div>
		<div class="bvn-stats">
			<div class="bvn-stat"><strong><?php echo esc_html((string) $upcoming_count); ?></strong> <?php esc_html_e('Upcoming', 'halifax-now-broadsheet'); ?></div>
			<div class="bvn-stat"><strong><?php echo esc_html((string) $free_count); ?></strong> <?php esc_html_e('Free', 'halifax-now-broadsheet'); ?></div>
			<?php if ($hood !== '') : ?>
				<div class="bvn-stat"><strong><?php echo esc_html($hood); ?></strong> <?php esc_html_e('Neighbourhood', 'halifax-now-broadsheet'); ?></div>
			<?php endif; ?>
			<?php if ($venue_phone !== '') : ?>
				<div class="bvn-stat"><strong><?php echo esc_html($venue_phone); ?></strong> <?php esc_html_e('Phone', 'halifax-now-broadsheet'); ?></div>
			<?php endif; ?>
		</div>

		<article class="hfx-venue-block bvn-box">
			<div class="v4-sec-hd bvn-sec-hd">
				<div class="h"><?php esc_html_e('Upcoming at', 'halifax-now-broadsheet'); ?> <em><?php echo esc_html($venue_name); ?></em><span class="count"><?php echo esc_html((string) $upcoming_count); ?></span></div>
			</div>
			<?php if ($venue_address !== '') : ?>
				<p class="bvn-address"><?php echo esc_html($venue_address); ?></p>
			<?php endif; ?>
			<div class="v4-list bvn-grid">
				<?php foreach (array_slice($events, 0, 14) as $event) : ?>
					<a class="v4-item bvn-item" href="<?php echo esc_url($event['url']); ?>">
						<div class="v4-item-date bvn-item-date">
							<div class="n"><?php echo esc_html(date_i18n('j', strtotime((string) $event['date']))); ?></div>
							<div class="m"><?php echo esc_html(date_i18n('M', strtotime((string) $event['date']))); ?></div>
						</div>
						<div>
							<div class="v4-item-cat bvn-item-cat"><?php echo esc_html(hfx_event_category_label($event)); ?></div>
							<div class="v4-item-t bvn-item-t"><?php echo esc_html((string) $event['title']); ?></div>
							<div class="v4-item-m bvn-item-m"><?php echo esc_html((string) $event['time'] . ' · ' . (string) $event['hood']); ?></div>
						</div>
						<div class="v4-item-price bvn-item-price <?php echo $event['price'] === 'paid' ? 'paid' : ''; ?>"><?php echo esc_html((string) $event['priceLabel']); ?></div>
					</a>
				<?php endforeach; ?>
			</div>
		</article>
	</section>
</div>
<?php
get_footer();
