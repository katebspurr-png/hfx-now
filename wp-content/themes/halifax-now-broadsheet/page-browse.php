<?php
/**
 * Template Name: Browse
 *
 * @package HalifaxNowBroadsheet
 */

get_header();

$events     = hfx_get_events_payload(200);
$quick      = hfx_qs('quick');
$browse_url = home_url('/browse/');
?>
<div class="v4-root bbr-root hfx-browse" data-hfx-browse data-quick="<?php echo esc_attr($quick); ?>">
	<header class="v4-mast">
		<div class="v4-datestamp"><?php esc_html_e('All Listings', 'halifax-now-broadsheet'); ?></div>
		<div class="v4-logo">Halifax<span class="amp">,</span> Now</div>
		<div class="v4-tag"><?php esc_html_e('Browse events', 'halifax-now-broadsheet'); ?></div>
	</header>

	<div class="bbr-filterband">
		<div class="bbr-filter-section">
			<span class="bbr-filter-label"><?php esc_html_e('Quick', 'halifax-now-broadsheet'); ?></span>
			<button class="bbr-chip" data-hfx-quick="tonight"><?php esc_html_e('Tonight', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip" data-hfx-quick="tomorrow"><?php esc_html_e('Tomorrow', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip" data-hfx-quick="weekend"><?php esc_html_e('Weekend', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip" data-hfx-quick="free"><?php esc_html_e('Free', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip" data-hfx-clear><?php esc_html_e('Clear', 'halifax-now-broadsheet'); ?></button>
		</div>
		<div class="bbr-filter-section">
			<span class="bbr-filter-label"><?php esc_html_e('Search', 'halifax-now-broadsheet'); ?></span>
			<input type="search" class="hfx-inline-search bbr-search" placeholder="<?php esc_attr_e('Search title or venue', 'halifax-now-broadsheet'); ?>" data-hfx-live-search>
		</div>
		<div class="bbr-filter-section">
			<a class="bbr-chip" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('Home', 'halifax-now-broadsheet'); ?></a>
			<a class="bbr-chip" href="<?php echo esc_url(home_url('/map/')); ?>"><?php esc_html_e('Map', 'halifax-now-broadsheet'); ?></a>
			<a class="bbr-chip" href="<?php echo esc_url(home_url('/venues/')); ?>"><?php esc_html_e('Venues', 'halifax-now-broadsheet'); ?></a>
			<a class="bbr-chip bbr-chip-acid" href="<?php echo esc_url(home_url('/submit/')); ?>"><?php esc_html_e('Submit', 'halifax-now-broadsheet'); ?></a>
		</div>
	</div>

	<section class="v4-sec bbr-wrap">
		<div class="bbr-results-bar">
			<div class="bbr-count" data-hfx-count>
				<em><?php echo esc_html(count($events)); ?></em>
				<span class="sub"><?php esc_html_e('events · sorted by date', 'halifax-now-broadsheet'); ?></span>
			</div>
			<div class="bbr-view-toggle">
				<button type="button" class="bbr-view-btn on"><?php esc_html_e('List', 'halifax-now-broadsheet'); ?></button>
			</div>
		</div>

		<div class="hfx-list bbr-grid" data-hfx-list>
			<?php foreach ($events as $event) : ?>
				<a
					class="v4-item bbr-item hfx-event-row"
					href="<?php echo esc_url($event['url']); ?>"
					data-date="<?php echo esc_attr($event['date']); ?>"
					data-time="<?php echo esc_attr($event['time']); ?>"
					data-price="<?php echo esc_attr($event['price']); ?>"
					data-title="<?php echo esc_attr(strtolower($event['title'])); ?>"
					data-venue="<?php echo esc_attr(strtolower($event['venue'])); ?>"
				>
					<div class="v4-item-date bbr-item-time">
						<div class="n"><?php echo esc_html(date_i18n('j', strtotime($event['date']))); ?></div>
						<div class="m"><?php echo esc_html(date_i18n('M', strtotime($event['date']))); ?></div>
					</div>
					<div>
						<div class="v4-item-cat bbr-item-cat"><?php echo esc_html( hfx_event_category_label( $event ) ); ?></div>
						<div class="v4-item-t bbr-item-t"><?php echo esc_html($event['title']); ?></div>
						<div class="v4-item-b bbr-item-b"><?php echo esc_html($event['short']); ?></div>
						<div class="v4-item-m bbr-item-m"><?php echo esc_html($event['time'] . ' · ' . $event['venue'] . ' · ' . $event['hood']); ?></div>
					</div>
					<div class="v4-item-price bbr-item-price <?php echo $event['price'] === 'paid' ? 'paid' : ''; ?>"><?php echo esc_html($event['priceLabel']); ?></div>
				</a>
			<?php endforeach; ?>
		</div>
		<div class="hfx-empty-state bbr-empty" data-hfx-empty hidden>
			<?php esc_html_e('No matching events found. Try clearing filters.', 'halifax-now-broadsheet'); ?>
		</div>
	</section>
</div>
<?php
get_footer();
