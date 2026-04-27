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
$cat_qs     = hfx_qs('cat');
$search_qs  = hfx_qs('s');
$browse_url = hfx_events_base_url();
$tz         = wp_timezone();
$now        = current_datetime();
$today_ymd  = $now->format('Y-m-d');
$tomorrow   = $now->modify('+1 day')->format('Y-m-d');
$active_cats = array_values(array_filter(array_map('sanitize_title', array_map('trim', explode(',', $cat_qs)))));
$active_moods = array_values(array_filter(array_map('sanitize_title', array_map('trim', explode(',', $mood_qs)))));
$active_hoods = array_values(array_filter(array_map('sanitize_text_field', array_map('trim', explode(',', $hood_qs)))));

$available_categories = array();
$available_moods = array();
$available_hoods = array();
foreach ($events as $ev_scan) {
	if (!empty($ev_scan['category']) && is_string($ev_scan['category'])) {
		$key = sanitize_title((string) $ev_scan['category']);
		$available_categories[$key] = hfx_event_category_label($ev_scan);
	}
	if (!empty($ev_scan['hood']) && is_string($ev_scan['hood'])) {
		$hkey = trim((string) $ev_scan['hood']);
		$available_hoods[$hkey] = $hkey;
	}
	if (!empty($ev_scan['mood']) && is_array($ev_scan['mood'])) {
		foreach ($ev_scan['mood'] as $mood_key) {
			$mood_slug = sanitize_title((string) $mood_key);
			if ($mood_slug !== '') {
				$available_moods[$mood_slug] = ucfirst(str_replace('-', ' ', $mood_slug));
			}
		}
	}
}
ksort($available_categories);
ksort($available_moods);
ksort($available_hoods);

$events = array_values(
	array_filter(
		$events,
		static function ($event) use ($quick, $date_qs, $active_hoods, $active_moods, $active_cats, $today_ymd, $tomorrow, $tz) {
			$event_date = isset($event['date']) ? (string) $event['date'] : '';
			$event_time = isset($event['time']) && hfx_is_valid_event_time((string) $event['time']) ? (string) $event['time'] : '00:00';

			if ($date_qs !== '') {
				if (!hfx_is_valid_event_date($date_qs) || $event_date !== $date_qs) {
					return false;
				}
			}

			if (!empty($active_hoods)) {
				$event_hood = isset($event['hood']) ? (string) $event['hood'] : '';
				$hood_match = false;
				foreach ($active_hoods as $hood_key) {
					if (0 === strcasecmp(trim($event_hood), trim($hood_key))) {
						$hood_match = true;
						break;
					}
				}
				if (!$hood_match) {
					return false;
				}
			}

			if (!empty($active_moods)) {
				$moods = isset($event['mood']) && is_array($event['mood']) ? array_map('strval', $event['mood']) : array();
				$moods = array_map(static function ($v) {
					return sanitize_title($v);
				}, $moods);
				$mood_match = false;
				foreach ($active_moods as $mood_key) {
					if (in_array($mood_key, $moods, true)) {
						$mood_match = true;
						break;
					}
				}
				if (!$mood_match) {
					return false;
				}
			}

			if (!empty($active_cats)) {
				$event_cat = isset($event['category']) ? sanitize_title((string) $event['category']) : '';
				if (!in_array($event_cat, $active_cats, true)) {
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

if ($search_qs !== '') {
	$search_term = strtolower(trim($search_qs));
	$events = array_values(
		array_filter(
			$events,
			static function ($event) use ($search_term) {
				$haystack = implode(
					' ',
					array_filter(
						array(
							isset($event['title']) ? (string) $event['title'] : '',
							isset($event['venue']) ? (string) $event['venue'] : '',
							isset($event['hood']) ? (string) $event['hood'] : '',
							isset($event['categoryLabel']) ? (string) $event['categoryLabel'] : '',
							isset($event['blurb']) ? (string) $event['blurb'] : '',
							isset($event['short']) ? (string) $event['short'] : '',
						)
					)
				);
				return false !== strpos(strtolower($haystack), $search_term);
			}
		)
	);
}

$active_filters = array();
if ( $date_qs !== '' && hfx_is_valid_event_date( $date_qs ) ) {
	$active_filters[] = sprintf( __( 'Date: %s', 'halifax-now-broadsheet' ), $date_qs );
}
if ( $quick !== '' ) {
	$active_filters[] = sprintf( __( 'Quick: %s', 'halifax-now-broadsheet' ), ucfirst( $quick ) );
}
if ( ! empty( $active_cats ) ) {
	$active_filters[] = sprintf( __( 'Category: %s', 'halifax-now-broadsheet' ), implode( ', ', $active_cats ) );
}
if ( ! empty( $active_hoods ) ) {
	$active_filters[] = sprintf( __( 'Neighbourhood: %s', 'halifax-now-broadsheet' ), implode( ', ', $active_hoods ) );
}
if ( ! empty( $active_moods ) ) {
	$active_filters[] = sprintf( __( 'Mood: %s', 'halifax-now-broadsheet' ), implode( ', ', $active_moods ) );
}
if ( $search_qs !== '' ) {
	$active_filters[] = sprintf( __( 'Search: %s', 'halifax-now-broadsheet' ), $search_qs );
}
?>
<div class="v4-root bbr-root hfx-browse" data-hfx-browse data-quick="<?php echo esc_attr($quick); ?>" data-date-filter="<?php echo esc_attr($date_qs); ?>" data-search="<?php echo esc_attr($search_qs); ?>">
	<header class="v4-mast">
		<div class="v4-datestamp"><?php esc_html_e('All Listings', 'halifax-now-broadsheet'); ?></div>
		<div class="v4-logo">Halifax<span class="amp">,</span> Now</div>
		<div class="v4-tag"><?php esc_html_e('Browse events', 'halifax-now-broadsheet'); ?></div>
	</header>
	<?php hfx_render_broadsheet_nav('browse'); ?>

	<div class="bbr-filterband">
		<div class="bbr-filter-section">
			<span class="bbr-filter-label"><?php esc_html_e('Quick', 'halifax-now-broadsheet'); ?></span>
			<button class="bbr-chip" data-hfx-quick="tonight"><?php esc_html_e('Tonight', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip" data-hfx-quick="tomorrow"><?php esc_html_e('Tomorrow', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip" data-hfx-quick="weekend"><?php esc_html_e('Weekend', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip" data-hfx-quick="free"><?php esc_html_e('Free', 'halifax-now-broadsheet'); ?></button>
			<button class="bbr-chip bbr-chip-clear" data-hfx-clear><?php esc_html_e('Clear', 'halifax-now-broadsheet'); ?></button>
		</div>
		<div class="bbr-filter-section" data-hfx-filter-group="category">
			<span class="bbr-filter-label"><?php esc_html_e('Category', 'halifax-now-broadsheet'); ?></span>
			<?php foreach ($available_categories as $cat_key => $cat_label) : ?>
				<button class="bbr-chip<?php echo in_array($cat_key, $active_cats, true) ? ' on' : ''; ?>" type="button" data-hfx-filter="category" data-value="<?php echo esc_attr($cat_key); ?>"><?php echo esc_html($cat_label); ?></button>
			<?php endforeach; ?>
		</div>
		<div class="bbr-filter-section" data-hfx-filter-group="mood">
			<span class="bbr-filter-label"><?php esc_html_e('Mood', 'halifax-now-broadsheet'); ?></span>
			<?php foreach ($available_moods as $mood_key => $mood_label) : ?>
				<button class="bbr-chip<?php echo in_array($mood_key, $active_moods, true) ? ' on' : ''; ?>" type="button" data-hfx-filter="mood" data-value="<?php echo esc_attr($mood_key); ?>"><?php echo esc_html($mood_label); ?></button>
			<?php endforeach; ?>
		</div>
		<div class="bbr-filter-section" data-hfx-filter-group="hood">
			<span class="bbr-filter-label"><?php esc_html_e('Neighbourhood', 'halifax-now-broadsheet'); ?></span>
			<?php foreach ($available_hoods as $hood_key) : ?>
				<button class="bbr-chip<?php echo in_array($hood_key, $active_hoods, true) ? ' on' : ''; ?>" type="button" data-hfx-filter="hood" data-value="<?php echo esc_attr($hood_key); ?>"><?php echo esc_html($hood_key); ?></button>
			<?php endforeach; ?>
		</div>
		<div class="bbr-filter-section">
			<span class="bbr-filter-label"><?php esc_html_e('Search', 'halifax-now-broadsheet'); ?></span>
			<input type="search" class="hfx-inline-search bbr-search" placeholder="<?php esc_attr_e('Search title or venue', 'halifax-now-broadsheet'); ?>" value="<?php echo esc_attr($search_qs); ?>" data-hfx-live-search>
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
					data-category="<?php echo esc_attr(sanitize_title((string) ($event['category'] ?? ''))); ?>"
					data-hood="<?php echo esc_attr((string) ($event['hood'] ?? '')); ?>"
					data-moods="<?php echo esc_attr(implode(',', array_map('sanitize_title', is_array($event['mood']) ? $event['mood'] : array()))); ?>"
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
