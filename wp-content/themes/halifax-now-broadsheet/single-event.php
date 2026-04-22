<?php
/**
 * Single event template.
 *
 * @package HalifaxNowBroadsheet
 */

get_header();

the_post();
$event = hfx_event_to_payload(get_the_ID());
?>
<div class="v4-root bed-root">
	<section class="v4-sec bed-wrap">
		<a class="bed-back" href="<?php echo esc_url(home_url('/browse/')); ?>"><?php esc_html_e('← Back to the week', 'halifax-now-broadsheet'); ?></a>
		<div class="bed-kicker <?php echo !empty($event['pick']) ? 'pick' : ''; ?>">
			<?php
			if (!empty($event['pick'])) {
				echo esc_html('★ Critics Pick · ');
			}
			echo esc_html( hfx_event_category_label( $event ) . ' · ' . $event['hood'] );
			?>
		</div>
		<h1 class="bed-h1"><?php the_title(); ?></h1>
		<p class="bed-lede"><?php echo esc_html($event['blurb']); ?></p>

		<?php
		if (!empty($event['image'])) {
			hfx_event_image_e(
				$event['image'],
				hfx_event_category_label( $event ) ?: ( $event['category'] ?? '' ),
				$event['title'] ?? '',
				'bed-hero-img',
				array_key_exists( 'hue', $event ) ? (int) $event['hue'] : null
			);
		}
		?>

		<div class="bed-grid">
			<div class="bed-body">
				<h3><?php esc_html_e('What to expect.', 'halifax-now-broadsheet'); ?></h3>
				<p>
					<strong><?php esc_html_e('The room.', 'halifax-now-broadsheet'); ?></strong>
					<?php
					echo esc_html(
						$event['venue'] . ' at ' . $event['address'] . ', in the heart of ' . $event['hood'] . '. Doors at ' . $event['time'] . '.'
					);
					?>
				</p>
				<p><?php echo esc_html($event['blurb']); ?></p>
				<div class="bed-pullquote"><?php echo esc_html('"' . ($event['short'] ? $event['short'] : $event['blurb']) . '"'); ?></div>
				<h3><?php esc_html_e('Getting there.', 'halifax-now-broadsheet'); ?></h3>
				<p><strong><?php esc_html_e('Transit.', 'halifax-now-broadsheet'); ?></strong> <?php esc_html_e('Transit routes stop within a two-minute walk. Parking exists but you know how it is downtown.', 'halifax-now-broadsheet'); ?></p>
				<p><strong><?php esc_html_e('Accessibility.', 'halifax-now-broadsheet'); ?></strong> <?php esc_html_e('Wheelchair accessible entrance. Ask at the door for seating accommodations.', 'halifax-now-broadsheet'); ?></p>
				<div class="hfx-event-content"><?php the_content(); ?></div>
			</div>
			<aside class="bed-side">
				<div class="bed-keybox">
					<div class="hd"><?php esc_html_e('The Details', 'halifax-now-broadsheet'); ?></div>
					<div class="body">
					<div class="bed-keyrow"><div class="bed-kt"><?php esc_html_e('When', 'halifax-now-broadsheet'); ?></div><div class="bed-kv"><?php echo esc_html($event['date'] . ' · ' . $event['time']); ?></div></div>
					<div class="bed-keyrow"><div class="bed-kt"><?php esc_html_e('Where', 'halifax-now-broadsheet'); ?></div><div class="bed-kv"><?php echo esc_html($event['venue']); ?><span class="sub"><?php echo esc_html($event['address']); ?></span></div></div>
					<div class="bed-keyrow"><div class="bed-kt"><?php esc_html_e('Neighbourhood', 'halifax-now-broadsheet'); ?></div><div class="bed-kv"><?php echo esc_html($event['hood']); ?></div></div>
					<?php if (!empty($event['organizer'])) : ?>
					<div class="bed-keyrow"><div class="bed-kt"><?php esc_html_e('Presented by', 'halifax-now-broadsheet'); ?></div><div class="bed-kv"><?php echo esc_html($event['organizer']); ?></div></div>
					<?php endif; ?>
					<div class="bed-keyrow"><div class="bed-kt"><?php esc_html_e('Cost', 'halifax-now-broadsheet'); ?></div><div class="bed-kv <?php echo $event['price'] === 'free' ? 'free' : ''; ?>"><?php echo esc_html($event['priceLabel']); ?></div></div>
					<?php if ( ! empty( $event['isRecurring'] ) ) : ?>
					<div class="bed-keyrow"><div class="bed-kt"><?php esc_html_e( 'Schedule', 'halifax-now-broadsheet' ); ?></div><div class="bed-kv"><?php echo esc_html( ! empty( $event['recurring'] ) ? (string) $event['recurring'] : __( 'Recurring event', 'halifax-now-broadsheet' ) ); ?></div></div>
					<?php endif; ?>
					</div>
				</div>
				<?php
				$ticket = !empty($event['ticketUrl']) ? $event['ticketUrl'] : '';
				if ($ticket && filter_var($ticket, FILTER_VALIDATE_URL)) :
					?>
					<a class="bed-cta" href="<?php echo esc_url($ticket); ?>" rel="noopener noreferrer" target="_blank"><?php esc_html_e('Get Tickets ->', 'halifax-now-broadsheet'); ?></a>
				<?php endif; ?>
				<?php
				$gcal_url = '';
				if ( ! empty( $event['date'] ) ) {
					$t_start  = strtotime( $event['date'] . ' ' . ( $event['time'] ?: '00:00' ) );
					$t_end    = ! empty( $event['endTime'] )
						? strtotime( $event['date'] . ' ' . $event['endTime'] )
						: $t_start + 2 * HOUR_IN_SECONDS;
					$gcal_url = add_query_arg(
						array(
							'action'   => 'TEMPLATE',
							'text'     => rawurlencode( $event['title'] ),
							'dates'    => gmdate( 'Ymd\THis\Z', $t_start ) . '/' . gmdate( 'Ymd\THis\Z', $t_end ),
							'details'  => rawurlencode( $event['blurb'] ),
							'location' => rawurlencode( trim( $event['venue'] . ' ' . $event['address'] ) ),
						),
						'https://calendar.google.com/calendar/render'
					);
				}
				if ( $gcal_url ) :
					?>
					<a class="bed-cta alt" href="<?php echo esc_url( $gcal_url ); ?>" rel="noopener noreferrer" target="_blank"><?php esc_html_e('+ Add to Calendar', 'halifax-now-broadsheet'); ?></a>
				<?php endif; ?>
				<button
					class="bed-cta ghost"
					type="button"
					data-hfx-share
					data-share-url="<?php echo esc_attr( get_permalink() ); ?>"
					data-share-title="<?php echo esc_attr( $event['title'] ); ?>"
				><?php esc_html_e('Share', 'halifax-now-broadsheet'); ?></button>
			</aside>
		</div>
	</section>
</div>
<?php
get_footer();
