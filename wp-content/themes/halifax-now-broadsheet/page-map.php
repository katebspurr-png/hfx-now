<?php
/**
 * Template Name: Map
 *
 * @package HalifaxNowBroadsheet
 */

get_header();

$events = hfx_get_events_payload(200);
$events_with_coords = array_values(array_filter($events, static function ($event) {
	return isset($event['lat'], $event['lng']) && is_numeric($event['lat']) && is_numeric($event['lng']);
}));
?>
<div class="v4-root hfx-map-page bmap-root" data-hfx-map-page>
	<div class="bmap-bar">
		<a class="bmap-bar-logo" href="<?php echo esc_url(home_url('/')); ?>">Halifax<span class="comma">,</span> Now</a>
		<a class="bmap-chip back" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('← The Week', 'halifax-now-broadsheet'); ?></a>
		<a class="bmap-chip back" href="<?php echo esc_url(hfx_events_base_url()); ?>"><?php esc_html_e('List View', 'halifax-now-broadsheet'); ?></a>
		<a class="bmap-chip" href="<?php echo esc_url(hfx_events_base_url() . '?quick=tonight'); ?>"><?php esc_html_e('★ Tonight', 'halifax-now-broadsheet'); ?></a>
		<a class="bmap-chip" href="<?php echo esc_url(hfx_events_base_url() . '?quick=weekend'); ?>"><?php esc_html_e('Weekend', 'halifax-now-broadsheet'); ?></a>
		<a class="bmap-chip" href="<?php echo esc_url(hfx_events_base_url() . '?quick=free'); ?>"><?php esc_html_e('Free', 'halifax-now-broadsheet'); ?></a>
		<div class="bmap-count"><?php echo esc_html(count($events_with_coords)); ?> <?php esc_html_e('events on map', 'halifax-now-broadsheet'); ?></div>
	</div>

	<section class="v4-sec bmap-wrap">
		<div class="hfx-map-layout bmap-layout">
			<aside class="hfx-map-list bmap-list">
				<div class="hfx-map-list-hd bmap-list-hd">
					<div class="t"><?php esc_html_e('On the map', 'halifax-now-broadsheet'); ?></div>
					<div class="s"><?php echo esc_html(count($events_with_coords)); ?> <?php esc_html_e('events · tap to highlight', 'halifax-now-broadsheet'); ?></div>
				</div>
				<?php foreach ($events_with_coords as $event) : ?>
					<a class="hfx-map-row bmap-row" href="<?php echo esc_url($event['url']); ?>">
						<div class="hfx-map-row-title bmap-row-title"><?php echo esc_html($event['title']); ?></div>
						<div class="hfx-map-row-meta bmap-row-meta"><?php echo esc_html($event['hood'] . ' · ' . $event['time']); ?></div>
					</a>
				<?php endforeach; ?>
			</aside>
			<div class="hfx-map-canvas bmap-canvas" data-hfx-map-canvas>
				<?php if (empty($events_with_coords)) : ?>
					<div class="hfx-map-overlay bmap-overlay"><?php esc_html_e('No event coordinates available yet.', 'halifax-now-broadsheet'); ?></div>
				<?php endif; ?>
			</div>
		</div>
	</section>
</div>
<?php
get_footer();
