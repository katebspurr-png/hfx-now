<?php
/**
 * Template Name: Browse
 *
 * @package HalifaxNowBroadsheet
 */

get_header();

$events     = hfx_get_events_payload(200);
$quick      = hfx_qs('quick');
$date_qs    = hfx_qs('date');
$hood_qs    = hfx_qs('hood');
$mood_qs    = hfx_qs('mood');
$browse_url = home_url('/browse/');
$tz         = wp_timezone();
$now        = current_datetime();
$today_ymd  = $now->format('Y-m-d');
$tomorrow   = $now->modify('+1 day')->format('Y-m-d');

$events = array_values(
	array_filter(
		$events,
		static function ($event) use ($quick, $date_qs, $hood_qs, $mood_qs, $today_ymd, $tomorrow, $tz) {
			$event_date = isset($event['date']) ? (string) $event['date'] : '';
			$event_time = isset($event['time']) && hfx_is_valid_event_time((string) $event['time']) ? (string) $event['time'] : '00:00';

			if ($date_qs !== '') {
				if (!hfx_is_valid_event_date($date_qs) || $event_date !== $date_qs) {
					return false;
				}
			}

			if ($hood_qs !== '') {
				$event_hood = isset($event['hood']) ? (string) $event['hood'] : '';
				if (0 !== strcasecmp(trim($event_hood), trim($hood_qs))) {
					return false;
				}
			}

			if ($mood_qs !== '') {
				$moods = isset($event['mood']) && is_array($event['mood']) ? array_map('strval', $event['mood']) : array();
				$moods = array_map(static function ($v) {
					return sanitize_title($v);
				}, $moods);
				if (!in_array(sanitize_title($mood_qs), $moods, true)) {
					return false;
				}
			}

			if ($quick === 'free') {
				return isset($event['price']) && 'free' === (string) $event['price'];
			}
			if ($quick === '') {
				return true;
			}
			if (!hfx_is_valid_event_date($event_date)) {
				return false;
			}

			if ($quick === 'tonight') {
				return $event_date === $today_ymd;
			}
			if ($quick === 'tomorrow') {
				return $event_date === $tomorrow;
			}
			if ($quick === 'weekend') {
				$event_day = DateTimeImmutable::createFromFormat('Y-m-d H:i', $event_date . ' ' . $event_time, $tz);
				if (!$event_day) {
					return false;
				}
				$w = (int) $event_day->format('w');
				return in_array($w, array(0, 5, 6), true);
			}

			return true;
		}
	)
);

$active_filters = array();
if ( $date_qs !== '' && hfx_is_valid_event_date( $date_qs ) ) {
	$active_filters[] = sprintf( __( 'Date: %s', 'halifax-now-broadsheet' ), $date_qs );
}
if ( $quick !== '' ) {
	$active_filters[] = sprintf( __( 'Quick: %s', 'halifax-now-broadsheet' ), ucfirst( $quick ) );
}
if ( $hood_qs !== '' ) {
	$active_filters[] = sprintf( __( 'Neighbourhood: %s', 'halifax-now-broadsheet' ), $hood_qs );
}
if ( $mood_qs !== '' ) {
	$active_filters[] = sprintf( __( 'Mood: %s', 'halifax-now-broadsheet' ), $mood_qs );
}
?>
<div class="v4-root bbr-root hfx-browse" data-hfx-browse data-quick="<?php echo esc_attr($quick); ?>" data-date-filter="<?php echo esc_attr($date_qs); ?>">
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
				<?php if ( ! empty( $active_filters ) ) : ?>
					<div class="bbr-active-filters"><?php echo esc_html(implode(' · ', $active_filters)); ?></div>
				<?php endif; ?>
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
