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
$has_tribe = function_exists( 'tribe_get_events' );
$this_week = array();
$coming_up = array();

if ( $has_tribe ) {
	$this_week = tribe_get_events( array(
		'posts_per_page' => 6,
		'start_date'     => 'now',
		'end_date'       => wp_date( 'Y-m-d', strtotime( 'next Sunday 23:59' ) ),
		'orderby'        => 'event_date',
		'order'          => 'ASC',
	) );

	$coming_up = tribe_get_events( array(
		'posts_per_page' => 5,
		'start_date'     => wp_date( 'Y-m-d', strtotime( 'next Monday' ) ),
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

  <div class="view-toggle-wrap">
    <div class="view-toggle">
      <button class="vt on" data-view="grid">Grid</button>
      <button class="vt" data-view="list">List</button>
      <button class="vt" data-view="calendar">Calendar</button>
    </div>
  </div>

  <div id="events-container">

  <?php if ( ! empty( $this_week ) ) : ?>
    <div class="event-grid" data-view-target="grid">
      <?php foreach ( $this_week as $i => $event ) :
        $wide = ( 0 === $i ); // first card is the featured wide card
        get_template_part( 'template-parts/event-card', null, array(
          'event' => $event,
          'wide'  => $wide,
        ) );
      endforeach; ?>
    </div>
    <div class="event-list" data-view-target="list" hidden>
      <?php foreach ( $this_week as $event ) :
        get_template_part( 'template-parts/event-list-item', null, array(
          'event' => $event,
        ) );
      endforeach; ?>
    </div>
    <div class="calendar-view" data-view-target="calendar" hidden>
      <div class="calendar-grid">
        <?php
        $today     = new DateTime( 'now', wp_timezone() );
        $monday    = clone $today;
        $monday->modify( 'Monday this week' );
        $day_names = array( 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun' );
        foreach ( $day_names as $dn ) :
        ?>
          <div class="cal-head"><?php echo esc_html( $dn ); ?></div>
        <?php endforeach;
        for ( $d = 0; $d < 7; $d++ ) :
          $cur = clone $monday;
          $cur->modify( "+{$d} days" );
          $day_str   = $cur->format( 'Y-m-d' );
          $is_today  = ( $day_str === $today->format( 'Y-m-d' ) );
          $day_events = array();
          foreach ( $this_week as $ev ) {
            $ev_start = tribe_get_start_date( $ev->ID, false, 'Y-m-d' );
            if ( $ev_start === $day_str ) {
              $day_events[] = $ev;
            }
          }
        ?>
          <div class="cal-day<?php echo $is_today ? ' today' : ''; ?>">
            <span class="cal-num"><?php echo esc_html( $cur->format( 'j' ) ); ?></span>
            <?php foreach ( $day_events as $cev ) : ?>
              <a href="<?php echo esc_url( get_permalink( $cev->ID ) ); ?>" class="cal-event"><?php echo esc_html( get_the_title( $cev ) ); ?></a>
            <?php endforeach; ?>
          </div>
        <?php endfor; ?>
      </div>
    </div>
  <?php else : ?>
    <?php /* Static fallback grid (design mockup data) */ ?>
    <div class="event-grid" data-view-target="grid">
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="ec wide" data-category="music" data-cost="free">
        <div class="ec-when">Saturday, March 22</div>
        <div class="ec-cat">Live Music</div>
        <div class="ec-title">Halifax Jazz Festival<br>Opening Night</div>
        <div class="ec-footer">
          <span class="ec-venue">The Carleton, Argyle St</span>
          <span class="badge white">Free &middot; 7:00 PM</span>
        </div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="ec" data-category="comedy" data-cost="paid">
        <div class="ec-when">Friday, March 21</div>
        <div class="ec-cat">Comedy</div>
        <div class="ec-title">Stand-Up Showcase</div>
        <div class="ec-footer">
          <span class="ec-venue">Yuk Yuk's &middot; 9 PM</span>
          <span class="badge paid">$15</span>
        </div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="ec" data-category="arts &amp; culture" data-cost="free">
        <div class="ec-when">Saturday, March 22</div>
        <div class="ec-cat">Arts</div>
        <div class="ec-title">AGNS First Fridays Opening</div>
        <div class="ec-footer">
          <span class="ec-venue">Art Gallery of NS &middot; 6 PM</span>
          <span class="badge free">Free</span>
        </div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="ec" data-category="outdoors" data-cost="free">
        <div class="ec-when">Sunday, March 23</div>
        <div class="ec-cat">Outdoors</div>
        <div class="ec-title">Point Pleasant Run Club</div>
        <div class="ec-footer">
          <span class="ec-venue">Point Pleasant &middot; 9 AM</span>
          <span class="badge free">Free</span>
        </div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="ec" data-category="food &amp; drink" data-cost="free">
        <div class="ec-when">Saturday, March 22</div>
        <div class="ec-cat">Food &amp; Drink</div>
        <div class="ec-title">Propeller Brewery Tap Takeover</div>
        <div class="ec-footer">
          <span class="ec-venue">Propeller Brewing &middot; 2 PM</span>
          <span class="badge free">Free Entry</span>
        </div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="ec" data-category="film" data-cost="paid">
        <div class="ec-when">Thursday, March 20</div>
        <div class="ec-cat">Film</div>
        <div class="ec-title">Carbon Arc: Cult Classics Night</div>
        <div class="ec-footer">
          <span class="ec-venue">Carbon Arc &middot; 8 PM</span>
          <span class="badge paid">$12</span>
        </div>
      </a>
    </div>
    <div class="event-list" data-view-target="list" hidden>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="music" data-cost="free">
        <div class="eli-date"><div class="eli-day">22</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Halifax Jazz Festival Opening Night</div>
        <div class="eli-meta"><span>7:00 PM</span><span class="dot"></span><span>The Carleton</span><span class="dot"></span><span>Live Music</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="comedy" data-cost="paid">
        <div class="eli-date"><div class="eli-day">21</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Stand-Up Showcase</div>
        <div class="eli-meta"><span>9:00 PM</span><span class="dot"></span><span>Yuk Yuk's</span><span class="dot"></span><span>Comedy</span></div></div>
        <div class="eli-cost">$15</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="arts &amp; culture" data-cost="free">
        <div class="eli-date"><div class="eli-day">22</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">AGNS First Fridays Opening</div>
        <div class="eli-meta"><span>6:00 PM</span><span class="dot"></span><span>Art Gallery of NS</span><span class="dot"></span><span>Arts</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="outdoors" data-cost="free">
        <div class="eli-date"><div class="eli-day">23</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Point Pleasant Run Club</div>
        <div class="eli-meta"><span>9:00 AM</span><span class="dot"></span><span>Point Pleasant</span><span class="dot"></span><span>Outdoors</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="food &amp; drink" data-cost="free">
        <div class="eli-date"><div class="eli-day">22</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Propeller Brewery Tap Takeover</div>
        <div class="eli-meta"><span>2:00 PM</span><span class="dot"></span><span>Propeller Brewing</span><span class="dot"></span><span>Food &amp; Drink</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli" data-category="film" data-cost="paid">
        <div class="eli-date"><div class="eli-day">20</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Carbon Arc: Cult Classics Night</div>
        <div class="eli-meta"><span>8:00 PM</span><span class="dot"></span><span>Carbon Arc</span><span class="dot"></span><span>Film</span></div></div>
        <div class="eli-cost">$12</div>
      </a>
    </div>
    <div class="calendar-view" data-view-target="calendar" hidden>
      <div class="calendar-grid">
        <div class="cal-head">Mon</div><div class="cal-head">Tue</div><div class="cal-head">Wed</div><div class="cal-head">Thu</div><div class="cal-head">Fri</div><div class="cal-head">Sat</div><div class="cal-head">Sun</div>
        <div class="cal-day"><span class="cal-num">17</span></div>
        <div class="cal-day"><span class="cal-num">18</span></div>
        <div class="cal-day"><span class="cal-num">19</span></div>
        <div class="cal-day"><span class="cal-num">20</span><span class="cal-event">Carbon Arc: Cult Classics</span></div>
        <div class="cal-day"><span class="cal-num">21</span><span class="cal-event">Stand-Up Showcase</span></div>
        <div class="cal-day"><span class="cal-num">22</span><span class="cal-event">Halifax Jazz Festival</span><span class="cal-event">AGNS First Fridays</span></div>
        <div class="cal-day"><span class="cal-num">23</span><span class="cal-event">Point Pleasant Run Club</span></div>
      </div>
    </div>
  <?php endif; ?>

  </div><!-- #events-container -->

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
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli">
        <div class="eli-date"><div class="eli-day">24</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Neptune Theatre &mdash; Spring Production Opening</div>
        <div class="eli-meta"><span>7:30 PM</span><span class="dot"></span><span>Neptune Theatre</span><span class="dot"></span><span>Theatre</span></div></div>
        <div class="eli-cost">$25&ndash;$65</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli">
        <div class="eli-date"><div class="eli-day">25</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Bearly's House of Blues &mdash; Tuesday Blues Jam</div>
        <div class="eli-meta"><span>9:00 PM</span><span class="dot"></span><span>Bearly's</span><span class="dot"></span><span>Live Music</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli">
        <div class="eli-date"><div class="eli-day">27</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">2037 Gottingen &mdash; Community Gathering &amp; Open Mic</div>
        <div class="eli-meta"><span>6:00 PM</span><span class="dot"></span><span>2037 Gottingen St</span><span class="dot"></span><span>Community</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli">
        <div class="eli-date"><div class="eli-day">28</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Dal Art Gallery &mdash; Artist Talk &amp; Reception</div>
        <div class="eli-meta"><span>5:00 PM</span><span class="dot"></span><span>Dal Art Gallery</span><span class="dot"></span><span>Arts</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
      <a href="<?php echo esc_url( home_url( '/events/' ) ); ?>" class="eli">
        <div class="eli-date"><div class="eli-day">29</div><div class="eli-mon">Mar</div></div>
        <div><div class="eli-title">Good Robot Brewing &mdash; Trivia Night</div>
        <div class="eli-meta"><span>7:00 PM</span><span class="dot"></span><span>Good Robot</span><span class="dot"></span><span>Food &amp; Drink</span></div></div>
        <div class="eli-cost">Free</div>
      </a>
    </div>
  <?php endif; ?>

</div>

<?php get_footer(); ?>
