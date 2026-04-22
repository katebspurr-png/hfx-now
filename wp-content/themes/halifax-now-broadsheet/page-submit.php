<?php
/**
 * Template Name: Submit
 *
 * @package HalifaxNowBroadsheet
 */

get_header();
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
					</div>

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
