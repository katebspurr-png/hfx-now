<?php
/**
 * Fallback template.
 *
 * @package HalifaxNowBroadsheet
 */

get_header();
?>
<main class="hfx-shell">
	<section class="hfx-section">
		<div class="hfx-sec-hd">
			<h1 class="hfx-headline"><?php esc_html_e('Latest', 'halifax-now-broadsheet'); ?></h1>
		</div>
		<?php if (have_posts()) : ?>
			<div class="hfx-list">
				<?php while (have_posts()) : the_post(); ?>
					<article class="hfx-item">
						<h2 class="hfx-item-title"><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h2>
						<div class="hfx-item-meta"><?php echo esc_html(get_the_date()); ?></div>
					</article>
				<?php endwhile; ?>
			</div>
			<?php the_posts_navigation(); ?>
		<?php else : ?>
			<p><?php esc_html_e('No posts found.', 'halifax-now-broadsheet'); ?></p>
		<?php endif; ?>
	</section>
</main>
<?php
get_footer();
