<?php
/**
 * Front page template — the main landing page for Halifax-Now.ca.
 *
 * Displays: hero, filter bar, "Happening This Week" grid, "Coming Up" list.
 *
 * @package Flavor2
 */

get_header();

/* ── Hero ── */
get_template_part( 'template-parts/hero' );

/* ── Filter bar ── */
get_template_part( 'template-parts/filter-bar' );

/* ── Query: This Week (grid) ── */
$has_tribe  = function_exists( 'tribe_get_events' );
$this_week  = array();
$coming_up  = array();

if ( $has_tribe ) {
	$this_week = tribe_get_events( array(
		'posts_per_page' => 6,
		'start_date'     => 'now',
		'end_date'       => date( 'Y-m-d', strtotime( 'next Sunday 23:59' ) ),
		'orderby'        => 'event_date',
		'order'          => 'ASC',
	) );

	$coming_up = tribe_get_events( array(
		'posts_per_page' => 5,
		'start_date'     => date( 'Y-m-d', strtotime( 'next Monday' ) ),
		'orderby'        => 'event_date',
		'order'          => 'ASC',
	) );
}
?>

<div class="page">

  <!-- ── Happening This Week ── -->
  <div class="sec-head">
    <div class="sec-title">Happening This Week</div>
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="sec-link">View All &rarr;</a>
  </div>

  <div style="display:flex; justify-content:flex-end; margin-bottom:20px;">
    <div class="view-toggle">
      <button class="vt on">Grid</button>
      <button class="vt">List</button>
      <button class="vt">Calendar</button>
    </div>
  </div>

  <?php if ( ! empty( $this_week ) ) : ?>
    <div class="event-grid">
      <?php foreach ( $this_week as $i => $event ) :
        $wide = ( 0 === $i ); // first card is the featured wide card
        get_template_part( 'template-parts/event-card', null, array(
          'event' => $event,
          'wide'  => $wide,
        ) );
      endforeach; ?>
    </div>
  <?php else : ?>
    <?php /* Static fallback grid (design mockup data) */ ?>
    <div class="event-grid">
      <div class="ec wide">
        <div class="ec-when">Saturday, March 22</div>
        <div class="ec-cat">Live Music</div>
        <div class="ec-title">Halifax Jazz Festival<br>Opening Night</div>
        <div class="ec-footer">
          <span class="ec-venue">The Carleton, Argyle St</span>
          <span class="badge white">Free &middot; 7:00 PM</span>
        </div>
      </div>
      <div class="ec">
        <div class="ec-when">Friday, March 21</div>
        <div class="ec-cat">Comedy</div>
        <div class="ec-title">Stand-Up Showcase</div>
        <div class="ec-footer">
          <span class="ec-venue">Yuk Yuk's &middot; 9 PM</span>
          <span class="badge paid">$15</span>
        </div>
      </div>
      <div class="ec">
        <div class="ec-when">Saturday, March 22</div>
        <div class="ec-cat">Arts</div>
        <div class="ec-title">AGNS First Fridays Opening</div>
        <div class="ec-footer">
          <span class="ec-venue">Art Gallery of NS &middot; 6 PM</span>
          <span class="badge free">Free</span>
        </div>
      </div>
      <div class="ec">
        <div class="ec-when">Sunday, March 23</div>
        <div class="ec-cat">Outdoors</div>
        <div class="ec-title">Point Pleasant Run Club</div>
        <div class="ec-footer">
          <span class="ec-venue">Point Pleasant &middot; 9 AM</span>
          <span class="badge free">Free</span>
        </div>
      </div>
      <div class="ec">
        <div class="ec-when">Saturday, March 22</div>
        <div class="ec-cat">Food &amp; Drink</div>
        <div class="ec-title">Propeller Brewery Tap Takeover</div>
        <div class="ec-footer">
          <span class="ec-venue">Propeller Brewing &middot; 2 PM</span>
          <span class="badge free">Free Entry</span>
        </div>
      </div>
      <div class="ec">
        <div class="ec-when">Thursday, March 20</div>
        <div class="ec-cat">Film</div>
        <div class="ec-title">Carbon Arc: Cult Classics Night</div>
        <div class="ec-footer">
          <span class="ec-venue">Carbon Arc &middot; 8 PM</span>
          <span class="badge paid">$12</span>
        </div>
      </div>
    </div>
  <?php endif; ?>

  <!-- ── Coming Up ── -->
  <div class="sec-head">
    <div class="sec-title">Coming Up</div>
    <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="sec-link">Full Calendar &rarr;</a>
  </div>

  <?php if ( ! empty( $coming_up ) ) : ?>
    <div class="event-list">
      <?php foreach ( $coming_up as $event ) :
        get_template_part( 'template-parts/event-list-item', null, array(
          'event' => $event,
        ) );
      endforeach; ?>
    </div>
  <?php else : ?>
    <?php /* Static fallback list */ ?>
    <div class="event-list">
      <div class="eli">
        <div class="eli-date"><div class="eli-day">24</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Neptune Theatre &mdash; Spring Production Opening</div>
        <div class="eli-meta"><span>7:30 PM</span><span class="dot"></span><span>Neptune Theatre</span><span class="dot"></span><span>Theatre</span></div></div>
        <div class="eli-cost">$25&ndash;$65</div>
      </div>
      <div class="eli">
        <div class="eli-date"><div class="eli-day">25</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Bearly's House of Blues &mdash; Tuesday Blues Jam</div>
        <div class="eli-meta"><span>9:00 PM</span><span class="dot"></span><span>Bearly's</span><span class="dot"></span><span>Live Music</span></div></div>
        <div class="eli-cost">Free</div>
      </div>
      <div class="eli">
        <div class="eli-date"><div class="eli-day">27</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">2037 Gottingen &mdash; Community Gathering &amp; Open Mic</div>
        <div class="eli-meta"><span>6:00 PM</span><span class="dot"></span><span>2037 Gottingen St</span><span class="dot"></span><span>Community</span></div></div>
        <div class="eli-cost">Free</div>
      </div>
      <div class="eli">
        <div class="eli-date"><div class="eli-day">28</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Dal Art Gallery &mdash; Artist Talk &amp; Reception</div>
        <div class="eli-meta"><span>5:00 PM</span><span class="dot"></span><span>Dal Art Gallery</span><span class="dot"></span><span>Arts</span></div></div>
        <div class="eli-cost">Free</div>
      </div>
      <div class="eli">
        <div class="eli-date"><div class="eli-day">29</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Good Robot Brewing &mdash; Trivia Night</div>
        <div class="eli-meta"><span>7:00 PM</span><span class="dot"></span><span>Good Robot</span><span class="dot"></span><span>Food &amp; Drink</span></div></div>
        <div class="eli-cost">Free</div>
      </div>
    </div>
  <?php endif; ?>

</div>

<?php get_footer(); ?>
