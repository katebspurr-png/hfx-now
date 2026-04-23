<?php
/**
 * Front page template.
 *
 * @package HalifaxNowBroadsheet
 */

get_header();

$events       = hfx_get_events_payload(120);
$tz           = wp_timezone();
$now          = current_datetime();
$today_ymd    = $now->format('Y-m-d');
$today_start  = DateTimeImmutable::createFromFormat('!Y-m-d', $today_ymd, $tz);
$upcoming     = array();
$tonight      = array();
$weekend      = array();
$picks        = array_values(array_filter($events, static function ($event) {
	return !empty($event['pick']);
}));
$picks        = array_slice($picks, 0, 5);
$wall         = array_slice($events, 0, 10);
$browse_url   = home_url('/browse/');
$map_url      = home_url('/map/');
$venues_url   = home_url('/venues/');
$submit_url   = home_url('/submit/');
$hoods        = array_values(array_unique(array_filter(array_map(static function ($event) {
	return isset($event['hood']) ? $event['hood'] : '';
}, $events))));
sort($hoods);

$heat_days = array();
for ($i = 0; $i < 14; $i++) {
	$day_dt          = $today_start->modify('+' . $i . ' day');
	$day_key         = $day_dt->format('Y-m-d');
	$heat_days[$i]   = array(
		'key'   => $day_key,
		'label' => $day_dt->format('j'),
		'dow'   => strtoupper($day_dt->format('D')),
		'count' => 0,
	);
}

foreach ($events as $event) {
	if (empty($event['date'])) {
		continue;
	}
	$event_date = (string) $event['date'];
	$event_time = !empty($event['time']) ? (string) $event['time'] : '00:00';
	if (1 !== preg_match('/^\d{4}-\d{2}-\d{2}$/', $event_date) || 1 !== preg_match('/^\d{2}:\d{2}$/', $event_time)) {
		continue;
	}
	$event_dt = DateTimeImmutable::createFromFormat('Y-m-d H:i', $event_date . ' ' . $event_time, $tz);
	if (!$event_dt || $event_dt->format('Y-m-d') !== $event_date) {
		continue;
	}

	$event_day = DateTimeImmutable::createFromFormat('!Y-m-d', $event_date, $tz);
	if (!$event_day || $event_day < $today_start) {
		continue;
	}

	$upcoming[] = $event;
	if ($event_date === $today_ymd) {
		$tonight[] = $event;
	}

	$day_of_week = (int) $event_day->format('w');
	if (in_array($day_of_week, array(0, 5, 6), true)) {
		$weekend[] = $event;
	}

	foreach ($heat_days as $idx => $day) {
		if ($day['key'] === $event_date) {
			$heat_days[$idx]['count']++;
			break;
		}
	}
}

$tonight = array_slice($tonight, 0, 8);
$weekend = array_slice($weekend, 0, 8);

$lead_tonight = !empty($tonight) ? $tonight[0] : null;
$rest_tonight = count($tonight) > 1 ? array_slice($tonight, 1) : array();
$max_heat = 1;
$total_heat_count = 0;
foreach ($heat_days as $day) {
	if ($day['count'] > $max_heat) {
		$max_heat = $day['count'];
	}
	$total_heat_count += (int) $day['count'];
}
$has_heat_data = $total_heat_count > 0;
?>
<div class="v4-root">
	<header class="v4-mast">
		<div class="v4-datestamp"><?php echo esc_html(date_i18n('D · M j')); ?><br><span class="hot"><?php esc_html_e('Halifax Now', 'halifax-now-broadsheet'); ?></span></div>
		<div class="v4-logo">Halifax<span class="amp">,</span> Now</div>
		<div class="v4-tag"><?php esc_html_e('The city, weekly.', 'halifax-now-broadsheet'); ?><br><span class="red"><?php esc_html_e('Do stuff. Have fun.', 'halifax-now-broadsheet'); ?></span></div>
	</header>

	<nav class="v4-nav">
		<a href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('The Week', 'halifax-now-broadsheet'); ?></a>
		<a href="<?php echo esc_url($browse_url); ?>"><?php esc_html_e('All Listings', 'halifax-now-broadsheet'); ?></a>
		<a href="<?php echo esc_url($browse_url . '?quick=tonight'); ?>"><?php esc_html_e('Tonight', 'halifax-now-broadsheet'); ?></a>
		<a href="<?php echo esc_url($browse_url . '?quick=weekend'); ?>"><?php esc_html_e('Weekend', 'halifax-now-broadsheet'); ?></a>
		<a href="<?php echo esc_url($map_url); ?>"><?php esc_html_e('Map', 'halifax-now-broadsheet'); ?></a>
		<a href="<?php echo esc_url($venues_url); ?>"><?php esc_html_e('Venues', 'halifax-now-broadsheet'); ?></a>
		<a class="cta" href="<?php echo esc_url($submit_url); ?>"><?php esc_html_e('+ Submit', 'halifax-now-broadsheet'); ?></a>
	</nav>

	<section class="v4-hero">
		<div>
			<div class="v4-hero-stamp"><?php esc_html_e('Broadsheet Edition', 'halifax-now-broadsheet'); ?></div>
			<h1>Do <span class="lean"><em>stuff.</em></span><br>Have <span class="knock">fun.</span></h1>
			<p class="v4-hero-lede"><?php esc_html_e('The best of Halifax this week, rebuilt as a living broadsheet. Editorial picks up top, full listings below, and a map when you need to move fast.', 'halifax-now-broadsheet'); ?></p>
			<div class="v4-quick">
				<a class="v4-qchip" href="<?php echo esc_url($browse_url . '?quick=tonight'); ?>"><?php esc_html_e('Tonight', 'halifax-now-broadsheet'); ?></a>
				<a class="v4-qchip" href="<?php echo esc_url($browse_url . '?quick=tomorrow'); ?>"><?php esc_html_e('Tomorrow', 'halifax-now-broadsheet'); ?></a>
				<a class="v4-qchip" href="<?php echo esc_url($browse_url . '?quick=weekend'); ?>"><?php esc_html_e('Weekend', 'halifax-now-broadsheet'); ?></a>
				<a class="v4-qchip" href="<?php echo esc_url($browse_url . '?quick=free'); ?>"><?php esc_html_e('FREE / $0', 'halifax-now-broadsheet'); ?></a>
				<button class="v4-qchip surprise" data-hfx-surprise><?php esc_html_e('Surprise me', 'halifax-now-broadsheet'); ?></button>
			</div>
			<div class="v4-search">
				<input type="search" placeholder="<?php esc_attr_e('Search venues, artists, things to do...', 'halifax-now-broadsheet'); ?>" data-hfx-search>
				<button type="button" data-hfx-search-submit><?php esc_html_e('Go', 'halifax-now-broadsheet'); ?></button>
			</div>
		</div>
		<div class="v4-picks">
			<div class="v4-picks-hd"><span class="t"><?php esc_html_e("Critics' Picks", 'halifax-now-broadsheet'); ?></span><span class="s"><?php esc_html_e('This Week', 'halifax-now-broadsheet'); ?></span></div>
			<?php foreach ($picks as $pick) : ?>
				<a class="v4-pick" href="<?php echo esc_url($pick['url']); ?>">
					<div class="v4-pick-star">★</div>
					<div>
						<div class="v4-pick-ca"><?php echo esc_html(hfx_event_category_label($pick)); ?></div>
						<div class="v4-pick-t"><?php echo esc_html($pick['title']); ?></div>
						<div class="v4-pick-m"><?php echo esc_html($pick['venue']); ?></div>
					</div>
					<div class="v4-pick-price"><?php echo esc_html($pick['priceLabel']); ?></div>
				</a>
			<?php endforeach; ?>
		</div>
	</section>

	<div class="v4-moodband">
		<span class="v4-moodband-l"><?php esc_html_e('Mood:', 'halifax-now-broadsheet'); ?></span>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=chill'); ?>">🌙 Chill</a>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=rowdy'); ?>">🔥 Rowdy</a>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=date'); ?>">💋 Date Night</a>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=kids'); ?>">🧃 Kid-friendly</a>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=solo'); ?>">👤 Solo OK</a>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=crew'); ?>">👯 Bring a crew</a>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=free'); ?>">🪙 Broke-friendly</a>
		<a class="v4-mood" href="<?php echo esc_url($browse_url . '?mood=rainy'); ?>">☔ Rainy-day</a>
	</div>

	<section class="v4-sec">
		<div class="v4-page">
			<main>
				<div class="v4-sec-hd">
					<div class="h"><?php esc_html_e('Tonight in Halifax', 'halifax-now-broadsheet'); ?><span class="count"><?php echo esc_html(count($tonight)); ?> <?php esc_html_e('things', 'halifax-now-broadsheet'); ?></span></div>
					<a class="l" href="<?php echo esc_url($browse_url . '?quick=tonight'); ?>"><?php esc_html_e('See all', 'halifax-now-broadsheet'); ?></a>
				</div>
				<?php if ($lead_tonight) : ?>
					<article class="v4-feat">
						<div>
							<?php
							hfx_event_image_e(
								$lead_tonight['image'] ?? '',
								hfx_event_category_label( $lead_tonight ) ?: ( $lead_tonight['category'] ?? '' ),
								$lead_tonight['title'] ?? '',
								'v4-feat-img',
								array_key_exists('hue', $lead_tonight) ? (int) $lead_tonight['hue'] : null
							);
							?>
						</div>
						<div>
							<div class="v4-feat-cat <?php echo !empty($lead_tonight['pick']) ? 'pick' : ''; ?>">
								<?php if (!empty($lead_tonight['pick'])) : ?>★ <?php esc_html_e("Critic's Pick · ", 'halifax-now-broadsheet'); ?><?php endif; ?>
								<?php echo esc_html( hfx_event_category_label( $lead_tonight ) ); ?>
							</div>
							<h2 class="v4-feat-title"><a href="<?php echo esc_url($lead_tonight['url']); ?>"><?php echo esc_html($lead_tonight['title']); ?></a></h2>
							<p class="v4-feat-blurb"><?php echo esc_html($lead_tonight['blurb']); ?></p>
							<div class="v4-feat-meta">
								<span><?php echo esc_html($lead_tonight['time'] . ' · ' . $lead_tonight['venue'] . ' · ' . $lead_tonight['hood']); ?></span>
								<span class="price <?php echo $lead_tonight['price'] === 'free' ? 'free' : ''; ?>"><?php echo esc_html($lead_tonight['priceLabel']); ?></span>
							</div>
						</div>
					</article>
				<?php endif; ?>
				<div class="v4-list">
					<?php foreach ($rest_tonight as $event) : ?>
						<a class="v4-item" href="<?php echo esc_url($event['url']); ?>">
							<div class="v4-item-date">
								<div class="n"><?php echo esc_html(date_i18n('j', strtotime($event['date']))); ?></div>
								<div class="m"><?php echo esc_html(date_i18n('M', strtotime($event['date']))); ?></div>
							</div>
							<div>
								<div class="v4-item-cat"><?php echo esc_html( hfx_event_category_label( $event ) ); ?></div>
								<div class="v4-item-t"><?php echo esc_html($event['title']); ?></div>
								<div class="v4-item-b"><?php echo esc_html($event['short']); ?></div>
								<div class="v4-item-m"><?php echo esc_html($event['time'] . ' · ' . $event['venue'] . ' · ' . $event['hood']); ?></div>
							</div>
							<div class="v4-item-price <?php echo $event['price'] === 'paid' ? 'paid' : ''; ?>"><?php echo esc_html($event['priceLabel']); ?></div>
						</a>
					<?php endforeach; ?>
				</div>
			</main>
			<aside class="hfx-home-aside">
				<div class="hfx-rightnow-box">
					<div class="hfx-rightnow-hd"><?php esc_html_e('Right now', 'halifax-now-broadsheet'); ?></div>
					<div class="hfx-rightnow-time">4:42 pm</div>
					<div class="hfx-rightnow-meta"><?php esc_html_e('Friday · 9°C · Clear', 'halifax-now-broadsheet'); ?></div>
					<div class="hfx-rightnow-copy"><strong><?php echo esc_html(count($tonight)); ?> <?php esc_html_e('events', 'halifax-now-broadsheet'); ?></strong> <?php esc_html_e('tonight. Sunset 8:07pm. Bring a layer.', 'halifax-now-broadsheet'); ?></div>
				</div>

				<button class="hfx-surprise-btn" data-hfx-surprise>🎲 <?php esc_html_e('Surprise me', 'halifax-now-broadsheet'); ?> →</button>

				<div class="hfx-home-card">
					<div class="hfx-home-card-hd"><?php esc_html_e('The neighbourhoods', 'halifax-now-broadsheet'); ?></div>
					<div class="hfx-hood-grid">
						<?php foreach (array_slice($hoods, 0, 8) as $hood) : ?>
							<a class="hfx-hood-pill" href="<?php echo esc_url($browse_url . '?hood=' . rawurlencode($hood)); ?>"><?php echo esc_html($hood); ?></a>
						<?php endforeach; ?>
					</div>
				</div>

				<div class="hfx-home-card">
					<div class="hfx-home-card-hd"><?php esc_html_e('Busy nights · Next 2 weeks', 'halifax-now-broadsheet'); ?></div>
					<div class="hfx-heatstrip">
						<?php foreach ($heat_days as $day) : ?>
							<?php $shade = (int) round(50 + (170 * ($day['count'] / $max_heat))); ?>
							<?php
							$heat_classes = 'hfx-heat-day';
							$heat_classes .= $day['count'] > 0 ? ' has-events' : ' is-empty';
							$heat_classes .= $day['key'] === $today_ymd ? ' is-today' : '';
							?>
							<a class="<?php echo esc_attr($heat_classes); ?>" href="<?php echo esc_url($browse_url . '?date=' . rawurlencode($day['key'])); ?>" style="background-color: rgb(80, 96, <?php echo esc_attr((string) $shade); ?>);" aria-label="<?php echo esc_attr(sprintf(__('%1$s %2$s: %3$d events', 'halifax-now-broadsheet'), $day['dow'], $day['label'], (int) $day['count'])); ?>">
								<span class="dow"><?php echo esc_html(substr($day['dow'], 0, 1)); ?></span>
								<span class="day"><?php echo esc_html($day['label']); ?></span>
								<span class="ct"><?php echo esc_html((string) $day['count']); ?></span>
							</a>
						<?php endforeach; ?>
					</div>
					<div class="hfx-heat-legend">
						<?php echo esc_html($has_heat_data ? __('Darker = busier', 'halifax-now-broadsheet') : __('No dated events in next 2 weeks', 'halifax-now-broadsheet')); ?>
					</div>
				</div>

				<div class="hfx-map-card">
					<div class="hfx-home-card-hd"><?php esc_html_e('The map', 'halifax-now-broadsheet'); ?></div>
					<div class="hfx-mini-map-preview">
						<div class="hfx-mini-map-label">HALIFAX</div>
					</div>
					<a class="hfx-map-open-btn" href="<?php echo esc_url($map_url); ?>"><?php esc_html_e('Open full map', 'halifax-now-broadsheet'); ?> →</a>
				</div>
			</aside>
		</div>
	</section>

	<section class="v4-sec">
		<div class="v4-sec-hd">
			<div class="h"><?php esc_html_e('The Wall', 'halifax-now-broadsheet'); ?><span class="count">+ <?php echo esc_html(count($wall)); ?> <?php esc_html_e('upcoming', 'halifax-now-broadsheet'); ?></span></div>
			<a class="l" href="<?php echo esc_url($browse_url); ?>"><?php esc_html_e('All listings', 'halifax-now-broadsheet'); ?></a>
		</div>
		<div class="v4-wall">
			<?php foreach ($wall as $index => $event) : ?>
				<a class="v4-card <?php echo $index === 0 ? 'wide' : ''; ?>" href="<?php echo esc_url($event['url']); ?>">
					<?php
					hfx_event_image_e(
						$event['image'] ?? '',
						hfx_event_category_label( $event ) ?: ( $event['category'] ?? '' ),
						$event['title'] ?? '',
						'v4-card-img',
						array_key_exists('hue', $event) ? (int) $event['hue'] : null
					);
					?>
					<div class="v4-card-body">
						<div class="v4-card-when"><?php echo esc_html( hfx_format_event_when( $event['date'] ?? '', $event['time'] ?? '', $today_ymd ) ); ?></div>
						<div class="v4-card-title"><?php echo esc_html($event['title']); ?></div>
						<div class="v4-card-b"><?php echo esc_html($event['short']); ?></div>
						<div class="v4-card-meta"><span><?php echo esc_html($event['venue']); ?></span><span class="price"><?php echo esc_html($event['priceLabel']); ?></span></div>
					</div>
				</a>
			<?php endforeach; ?>
		</div>
	</section>

	<section class="v4-sec">
		<div class="v4-sec-hd">
			<div class="h"><?php esc_html_e('Weekend', 'halifax-now-broadsheet'); ?><span class="count"><?php echo esc_html(count($weekend)); ?></span></div>
			<a class="l" href="<?php echo esc_url($browse_url . '?quick=weekend'); ?>"><?php esc_html_e('Full weekend', 'halifax-now-broadsheet'); ?></a>
		</div>
		<div class="v4-list">
			<?php foreach ($weekend as $event) : ?>
				<a class="v4-item" href="<?php echo esc_url($event['url']); ?>">
					<div class="v4-item-date">
						<div class="n"><?php echo esc_html(date_i18n('j', strtotime($event['date']))); ?></div>
						<div class="m"><?php echo esc_html(date_i18n('M', strtotime($event['date']))); ?></div>
					</div>
					<div>
						<div class="v4-item-cat"><?php echo esc_html( hfx_event_category_label( $event ) ); ?></div>
						<div class="v4-item-t"><?php echo esc_html($event['title']); ?></div>
						<div class="v4-item-m"><?php echo esc_html($event['time'] . ' · ' . $event['venue']); ?></div>
					</div>
					<div class="v4-item-price <?php echo $event['price'] === 'paid' ? 'paid' : ''; ?>"><?php echo esc_html($event['priceLabel']); ?></div>
				</a>
			<?php endforeach; ?>
		</div>
	</section>

	<footer class="v4-footer">
		<div class="v4-footer-big">Halifax<span class="amp">,</span><br><span class="acid">Now.</span></div>
		<div class="v4-footer-bot"><span><?php esc_html_e('Do stuff. Have fun.', 'halifax-now-broadsheet'); ?></span><span><?php esc_html_e('Built for Haligonians.', 'halifax-now-broadsheet'); ?></span></div>
	</footer>
</div>
<?php
get_footer();
