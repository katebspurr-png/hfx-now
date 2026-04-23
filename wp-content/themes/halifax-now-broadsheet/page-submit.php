<?php
/**
 * Template Name: Submit
 *
 * @package HalifaxNowBroadsheet
 */

get_header();
$category_choices = array(
	'music' => __('Live Music', 'halifax-now-broadsheet'),
	'comedy' => __('Comedy', 'halifax-now-broadsheet'),
	'arts' => __('Arts & Culture', 'halifax-now-broadsheet'),
	'food' => __('Food & Drink', 'halifax-now-broadsheet'),
	'outdoors' => __('Outdoors', 'halifax-now-broadsheet'),
	'film' => __('Film', 'halifax-now-broadsheet'),
	'theatre' => __('Theatre', 'halifax-now-broadsheet'),
	'community' => __('Community', 'halifax-now-broadsheet'),
	'sports' => __('Sports', 'halifax-now-broadsheet'),
	'family' => __('Family', 'halifax-now-broadsheet'),
	'nightlife' => __('Nightlife', 'halifax-now-broadsheet'),
	'markets' => __('Markets', 'halifax-now-broadsheet'),
);
$hood_choices = array(
	'Downtown',
	'North End',
	'South End',
	'West End',
	'Quinpool',
	'Spring Garden',
	'Dartmouth',
	'Bedford',
);
$mood_choices = array(
	'chill' => '🌙 ' . __('Chill', 'halifax-now-broadsheet'),
	'rowdy' => '🔥 ' . __('Rowdy', 'halifax-now-broadsheet'),
	'date' => '💋 ' . __('Date Night', 'halifax-now-broadsheet'),
	'kids' => '🧃 ' . __('Kid-friendly', 'halifax-now-broadsheet'),
	'solo' => '👤 ' . __('Solo OK', 'halifax-now-broadsheet'),
	'crew' => '👯 ' . __('Bring a crew', 'halifax-now-broadsheet'),
	'free' => '🪙 ' . __('Broke-friendly', 'halifax-now-broadsheet'),
	'rainy' => '☔ ' . __('Rainy-day', 'halifax-now-broadsheet'),
);
?>
<div class="v4-root bsub-root">
	<section class="v4-sec bsub-wrap">
		<a class="bsub-back" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('← Back to the week', 'halifax-now-broadsheet'); ?></a>
		<div class="bsub-kicker"><span class="bsub-kicker-inner"><?php esc_html_e('★ Free · Human-reviewed · Usually live in 24h', 'halifax-now-broadsheet'); ?></span></div>
		<div class="hfx-submit-wrap bsub-shell">
			<?php if ('1' === hfx_qs('submitted')) : ?>
				<div class="hfx-submit-success bsub-success">
					<div class="big"><?php esc_html_e('Done.', 'halifax-now-broadsheet'); ?></div>
					<div class="sub"><?php esc_html_e("We've got it.", 'halifax-now-broadsheet'); ?></div>
					<p><?php esc_html_e("We read every submission. If it's a good fit for Halifax Now, it'll be live within 24 hours — sometimes faster. We'll reach out if we have questions.", 'halifax-now-broadsheet'); ?></p>
					<a class="v4-qchip" href="<?php echo esc_url(home_url('/submit/')); ?>"><?php esc_html_e('Submit another event', 'halifax-now-broadsheet'); ?></a>
				</div>
			<?php else : ?>
				<h1 class="hfx-submit-title bsub-h1"><?php esc_html_e("Tell us what's happening.", 'halifax-now-broadsheet'); ?></h1>
				<p class="bsub-lede"><?php esc_html_e('Every event on Halifax Now is reviewed by a real person. We care about what goes in the calendar - so we read everything you send. Free to submit, always.', 'halifax-now-broadsheet'); ?></p>

				<div class="bsub-rules">
					<div class="bsub-rule">
						<div class="num">01</div>
						<div class="t"><?php esc_html_e('Free to list', 'halifax-now-broadsheet'); ?></div>
						<div class="s"><?php esc_html_e("No fees, no pay-to-play. If it's happening in Halifax, it belongs here.", 'halifax-now-broadsheet'); ?></div>
					</div>
					<div class="bsub-rule">
						<div class="num">02</div>
						<div class="t"><?php esc_html_e('Human-reviewed', 'halifax-now-broadsheet'); ?></div>
						<div class="s"><?php esc_html_e('A real editor reads every submission. We approve within 24 hours, usually less.', 'halifax-now-broadsheet'); ?></div>
					</div>
					<div class="bsub-rule">
						<div class="num">03</div>
						<div class="t"><?php esc_html_e('We may edit', 'halifax-now-broadsheet'); ?></div>
						<div class="s"><?php esc_html_e("We'll keep your facts; we might tighten the copy.", 'halifax-now-broadsheet'); ?></div>
					</div>
				</div>

				<form class="hfx-submit-form bsub-form" method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
					<input type="hidden" name="action" value="hfx_submit_event">
					<?php wp_nonce_field('hfx_submit_event', 'hfx_submit_nonce'); ?>

					<label>
						<span><?php esc_html_e('Event title', 'halifax-now-broadsheet'); ?> <strong><?php esc_html_e('Required', 'halifax-now-broadsheet'); ?></strong></span>
						<input class="bsub-input big" type="text" name="event_title" placeholder="<?php esc_attr_e("What's it called?", 'halifax-now-broadsheet'); ?>" required>
					</label>
					<label>
						<span><?php esc_html_e('Venue', 'halifax-now-broadsheet'); ?> <strong><?php esc_html_e('Required', 'halifax-now-broadsheet'); ?></strong></span>
						<input class="bsub-input" type="text" name="event_venue" placeholder="<?php esc_attr_e('The Carleton, 1685 Argyle St', 'halifax-now-broadsheet'); ?>" required>
					</label>
					<div class="hfx-submit-grid">
						<label>
							<span><?php esc_html_e('Date', 'halifax-now-broadsheet'); ?> <strong><?php esc_html_e('Required', 'halifax-now-broadsheet'); ?></strong></span>
							<input class="bsub-input" type="date" name="event_date" required>
						</label>
						<label>
							<span><?php esc_html_e('Start time', 'halifax-now-broadsheet'); ?> <strong><?php esc_html_e('Required', 'halifax-now-broadsheet'); ?></strong></span>
							<input class="bsub-input" type="time" name="event_time" required>
						</label>
						<label>
							<span><?php esc_html_e('Price', 'halifax-now-broadsheet'); ?></span>
							<input class="bsub-input" type="text" name="event_price" placeholder="<?php esc_attr_e('Free / $15 / $25-$45', 'halifax-now-broadsheet'); ?>">
						</label>
						<label>
							<span><?php esc_html_e('Category', 'halifax-now-broadsheet'); ?> <strong><?php esc_html_e('Required', 'halifax-now-broadsheet'); ?></strong></span>
							<select class="bsub-input" name="event_category" required>
								<option value=""><?php esc_html_e('Select category', 'halifax-now-broadsheet'); ?></option>
								<?php foreach ($category_choices as $value => $label) : ?>
									<option value="<?php echo esc_attr($value); ?>"><?php echo esc_html($label); ?></option>
								<?php endforeach; ?>
							</select>
						</label>
						<label>
							<span><?php esc_html_e('Neighbourhood', 'halifax-now-broadsheet'); ?> <strong><?php esc_html_e('Required', 'halifax-now-broadsheet'); ?></strong></span>
							<select class="bsub-input" name="event_neighbourhood" required>
								<option value=""><?php esc_html_e('Select neighbourhood', 'halifax-now-broadsheet'); ?></option>
								<?php foreach ($hood_choices as $label) : ?>
									<option value="<?php echo esc_attr($label); ?>"><?php echo esc_html($label); ?></option>
								<?php endforeach; ?>
							</select>
						</label>
					</div>
					<fieldset class="bsub-moods">
						<legend><?php esc_html_e('Mood (select all that apply)', 'halifax-now-broadsheet'); ?></legend>
						<div class="bsub-mood-grid">
							<?php foreach ($mood_choices as $value => $label) : ?>
								<label class="bsub-mood-chip">
									<input type="checkbox" name="event_moods[]" value="<?php echo esc_attr($value); ?>">
									<span><?php echo esc_html($label); ?></span>
								</label>
							<?php endforeach; ?>
						</div>
					</fieldset>

					<label>
						<span><?php esc_html_e('Tell us about it', 'halifax-now-broadsheet'); ?></span>
						<textarea class="bsub-textarea" name="event_blurb" rows="6" placeholder="<?php esc_attr_e("What's the vibe? Who's it for? Anything worth knowing?", 'halifax-now-broadsheet'); ?>" required></textarea>
					</label>
					<label>
						<span><?php esc_html_e('Your contact (optional)', 'halifax-now-broadsheet'); ?></span>
						<input class="bsub-input" type="text" name="event_contact" placeholder="<?php esc_attr_e('email or phone - only if we need to follow up', 'halifax-now-broadsheet'); ?>">
					</label>
					<button type="submit" class="v4-qchip bsub-submit"><?php esc_html_e('Send it in ->', 'halifax-now-broadsheet'); ?></button>
					<p class="bsub-note"><?php esc_html_e('We usually respond within 24 hours. Recurring events? Submit once and note the schedule in the description.', 'halifax-now-broadsheet'); ?></p>
				</form>
			<?php endif; ?>
		</div>
	</section>
</div>
<?php
get_footer();
