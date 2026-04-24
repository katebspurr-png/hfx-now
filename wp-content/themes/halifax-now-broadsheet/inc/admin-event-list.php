<?php
/**
 * Admin event list: custom columns and extended quick-edit for tribe_events.
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

// ── Columns ───────────────────────────────────────────────────────────────────

add_filter( 'manage_tribe_events_posts_columns', 'hfx_admin_event_columns' );
function hfx_admin_event_columns( $cols ) {
	unset( $cols['series'] );

	$new = array();
	foreach ( $cols as $key => $label ) {
		$new[ $key ] = $label;
		if ( 'title' === $key ) {
			$new['hfx_venue'] = 'Venue';
			$new['hfx_price'] = 'Price';
			$new['hfx_hood']  = 'Hood';
			$new['hfx_pick']  = '★';
		}
	}
	return $new;
}

add_action( 'manage_tribe_events_posts_custom_column', 'hfx_admin_event_column', 10, 2 );
function hfx_admin_event_column( $col, $post_id ) {
	switch ( $col ) {

		case 'hfx_venue':
			$vid = (int) get_post_meta( $post_id, '_EventVenueID', true );
			if ( $vid ) {
				$name = get_the_title( $vid );
				$link = get_edit_post_link( $vid );
				if ( $name && $link ) {
					echo '<a href="' . esc_url( $link ) . '">' . esc_html( $name ) . '</a>';
				} elseif ( $name ) {
					echo esc_html( $name );
				} else {
					echo '<span class="hfx-dim">—</span>';
				}
			} elseif ( function_exists( 'tribe_get_venue' ) ) {
				$v = wp_strip_all_tags( (string) tribe_get_venue( $post_id, false, false ) );
				echo $v !== '' ? esc_html( $v ) : '<span class="hfx-dim">—</span>';
			} else {
				echo '<span class="hfx-dim">—</span>';
			}
			break;

		case 'hfx_price':
			$price = trim( (string) get_post_meta( $post_id, '_EventCost', true ) );
			echo $price !== '' ? esc_html( $price ) : '<span class="hfx-dim">Free</span>';
			break;

		case 'hfx_hood':
			$hood = trim( (string) get_post_meta( $post_id, 'hfx_neighbourhood', true ) );
			echo $hood !== '' ? esc_html( $hood ) : '<span class="hfx-dim">—</span>';
			break;

		case 'hfx_pick':
			$pick    = get_post_meta( $post_id, 'hfx_critic_pick', true );
			$is_pick = $pick && '0' !== (string) $pick;
			if ( $is_pick ) {
				echo '<span title="Critic\'s Pick" style="color:#f0a500;font-size:16px;">★</span>';
			}

			// Hidden data block read by quick-edit JS (rendered once, in this column).
			$price     = trim( (string) get_post_meta( $post_id, '_EventCost', true ) );
			$hood      = trim( (string) get_post_meta( $post_id, 'hfx_neighbourhood', true ) );
			$venue_id  = (int) get_post_meta( $post_id, '_EventVenueID', true );
			$moods_raw = get_post_meta( $post_id, 'hfx_moods', true );
			$moods     = is_array( $moods_raw ) ? $moods_raw
				: ( is_string( $moods_raw ) && $moods_raw !== '' ? array_map( 'trim', explode( ',', $moods_raw ) ) : array() );

			$start_raw = (string) get_post_meta( $post_id, '_EventStartDate', true );
			$end_raw   = (string) get_post_meta( $post_id, '_EventEndDate', true );
			$start_dt  = $start_raw ? date_create( $start_raw ) : false;
			$end_dt    = $end_raw   ? date_create( $end_raw )   : false;
			$start_date = $start_dt ? $start_dt->format( 'Y-m-d' ) : '';
			$start_time = $start_dt ? $start_dt->format( 'H:i' )   : '';
			$end_date   = $end_dt   ? $end_dt->format( 'Y-m-d' )   : '';
			$end_time   = $end_dt   ? $end_dt->format( 'H:i' )     : '';

			printf(
				'<span class="hfx-row-data" style="display:none" data-venue-id="%s" data-price="%s" data-hood="%s" data-pick="%s" data-moods="%s" data-start-date="%s" data-start-time="%s" data-end-date="%s" data-end-time="%s"></span>',
				esc_attr( (string) $venue_id ),
				esc_attr( $price ),
				esc_attr( $hood ),
				esc_attr( $is_pick ? '1' : '0' ),
				esc_attr( (string) wp_json_encode( array_values( $moods ) ) ),
				esc_attr( $start_date ),
				esc_attr( $start_time ),
				esc_attr( $end_date ),
				esc_attr( $end_time )
			);
			break;
	}
}

add_filter( 'manage_edit-tribe_events_sortable_columns', 'hfx_admin_event_sortable_columns' );
function hfx_admin_event_sortable_columns( $cols ) {
	$cols['hfx_price'] = 'hfx_price';
	$cols['hfx_hood']  = 'hfx_hood';
	$cols['hfx_pick']  = 'hfx_pick';
	return $cols;
}

add_action( 'pre_get_posts', 'hfx_admin_event_sort_query' );
function hfx_admin_event_sort_query( $query ) {
	if ( ! is_admin() || ! $query->is_main_query() ) {
		return;
	}
	$map = array(
		'hfx_price' => '_EventCost',
		'hfx_hood'  => 'hfx_neighbourhood',
		'hfx_pick'  => 'hfx_critic_pick',
	);
	$ob = $query->get( 'orderby' );
	if ( isset( $map[ $ob ] ) ) {
		$query->set( 'meta_key', $map[ $ob ] );
		$query->set( 'orderby', 'meta_value' );
	}
}

// ── Admin styles ──────────────────────────────────────────────────────────────

add_action( 'admin_head', 'hfx_admin_event_css' );
function hfx_admin_event_css() {
	global $post_type;
	if ( 'tribe_events' !== $post_type ) {
		return;
	}
	?>
	<style>
	.column-hfx_venue { width: 130px; }
	.column-hfx_price { width: 60px; }
	.column-hfx_hood  { width: 110px; }
	.column-hfx_pick  { width: 28px; text-align: center !important; }
	td.column-hfx_pick { text-align: center; }
	.column-title { min-width: 160px; }
	.hfx-dim { color: #bbb; }

	/* Quick-edit panel */
	#hfx-quick-edit {
		clear: both;
		margin-top: 10px;
		padding-top: 10px;
		border-top: 1px solid #ddd;
	}
	#hfx-quick-edit h4 {
		margin: 0 0 8px;
		font-size: 12px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: .04em;
		color: #555;
	}
	.hfx-qe-row {
		display: flex;
		flex-wrap: wrap;
		gap: 8px 24px;
		align-items: flex-end;
	}
	.hfx-qe-field {
		display: flex;
		flex-direction: column;
		gap: 3px;
	}
	.hfx-qe-field > span {
		font-size: 11px;
		font-weight: 600;
		text-transform: uppercase;
		color: #777;
	}
	.hfx-qe-pick-wrap {
		padding-bottom: 4px;
	}
	.hfx-moods-grid {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 16px;
		margin-top: 4px;
	}
	.hfx-moods-grid label {
		font-weight: normal;
	}
	</style>
	<?php
}

// ── Quick-edit fields ─────────────────────────────────────────────────────────

add_action( 'quick_edit_custom_box', 'hfx_admin_event_quick_edit', 10, 2 );
function hfx_admin_event_quick_edit( $col, $post_type ) {
	// Render once, anchored to the first custom column.
	if ( 'tribe_events' !== $post_type || 'hfx_venue' !== $col ) {
		return;
	}

	$hoods = array(
		''               => '— neighbourhood —',
		'Downtown'       => 'Downtown',
		'North End'      => 'North End',
		'South End'      => 'South End',
		'West End'       => 'West End',
		'Quinpool'       => 'Quinpool',
		'Spring Garden'  => 'Spring Garden',
		'Dartmouth'      => 'Dartmouth',
		'Bedford'        => 'Bedford',
	);

	$moods = array(
		'chill' => '🌙 Chill',
		'rowdy' => '🔥 Rowdy',
		'date'  => '💋 Date Night',
		'kids'  => '🧃 Kid-friendly',
		'solo'  => '👤 Solo OK',
		'crew'  => '👯 Bring a crew',
		'free'  => '🪙 Broke-friendly',
		'rainy' => '☔ Rainy-day',
	);

	$venues = get_posts( array(
		'post_type'      => 'tribe_venue',
		'post_status'    => 'publish',
		'posts_per_page' => -1,
		'orderby'        => 'title',
		'order'          => 'ASC',
		'no_found_rows'  => true,
	) );

	wp_nonce_field( 'hfx_quick_edit', 'hfx_qe_nonce' );
	?>
	<input type="hidden" name="hfx_qe_initialized" id="hfx-qe-initialized" value="0">
	<div id="hfx-quick-edit">
		<h4>Halifax Now</h4>
		<div class="hfx-qe-row">

			<div class="hfx-qe-field">
				<span>Venue</span>
				<select name="hfx_qe_venue_id" id="hfx-qe-venue-id" style="max-width:200px">
					<option value="0">— no venue —</option>
					<?php foreach ( $venues as $v ) : ?>
						<option value="<?php echo esc_attr( (string) $v->ID ); ?>"><?php echo esc_html( $v->post_title ); ?></option>
					<?php endforeach; ?>
				</select>
			</div>

			<div class="hfx-qe-field">
				<span>Price</span>
				<input type="text" name="hfx_qe_price" id="hfx-qe-price" style="width:80px" placeholder="e.g. $15">
			</div>

			<div class="hfx-qe-field">
				<span>Neighbourhood</span>
				<select name="hfx_qe_hood" id="hfx-qe-hood">
					<?php foreach ( $hoods as $val => $label ) : ?>
						<option value="<?php echo esc_attr( $val ); ?>"><?php echo esc_html( $label ); ?></option>
					<?php endforeach; ?>
				</select>
			</div>

			<div class="hfx-qe-field hfx-qe-pick-wrap">
				<label>
					<input type="checkbox" name="hfx_qe_pick" id="hfx-qe-pick" value="1">
					★ Critic's Pick
				</label>
			</div>

		</div>

		<div class="hfx-qe-row" style="margin-top:8px;">

			<div class="hfx-qe-field">
				<span>Start date</span>
				<div style="display:flex;gap:6px;">
					<input type="date" name="hfx_qe_start_date" id="hfx-qe-start-date">
					<input type="time" name="hfx_qe_start_time" id="hfx-qe-start-time">
				</div>
			</div>

			<div class="hfx-qe-field">
				<span>End date</span>
				<div style="display:flex;gap:6px;">
					<input type="date" name="hfx_qe_end_date" id="hfx-qe-end-date">
					<input type="time" name="hfx_qe_end_time" id="hfx-qe-end-time">
				</div>
			</div>

		</div>

		<div class="hfx-qe-field" style="margin-top:10px;">
			<span>Moods</span>
			<div class="hfx-moods-grid">
				<?php foreach ( $moods as $val => $label ) : ?>
					<label>
						<input type="checkbox" name="hfx_qe_moods[]" class="hfx-qe-mood" value="<?php echo esc_attr( $val ); ?>">
						<?php echo esc_html( $label ); ?>
					</label>
				<?php endforeach; ?>
			</div>
		</div>
	</div>
	<?php
}

// ── JS: populate quick-edit from row data ─────────────────────────────────────

add_action( 'admin_footer', 'hfx_admin_event_quick_edit_js' );
function hfx_admin_event_quick_edit_js() {
	global $post_type;
	if ( 'tribe_events' !== $post_type ) {
		return;
	}
	?>
	<script>
	(function ($) {
		function hfxFillQuickEdit(postId) {
			var $row  = $('#post-' + postId);
			var $qe   = $('#edit-' + postId);
			var $data = $row.find('.hfx-row-data');
			if (!$data.length || !$qe.length) return;

			// Use .attr() — avoids jQuery's .data() caching and auto-type-casting.
			$qe.find('#hfx-qe-venue-id').val($data.attr('data-venue-id') || '0');
			$qe.find('#hfx-qe-price').val($data.attr('data-price') || '');
			$qe.find('#hfx-qe-hood').val($data.attr('data-hood') || '');
			$qe.find('#hfx-qe-pick').prop('checked', $data.attr('data-pick') === '1');
			$qe.find('#hfx-qe-start-date').val($data.attr('data-start-date') || '');
			$qe.find('#hfx-qe-start-time').val($data.attr('data-start-time') || '');
			$qe.find('#hfx-qe-end-date').val($data.attr('data-end-date') || '');
			$qe.find('#hfx-qe-end-time').val($data.attr('data-end-time') || '');

			var moods = [];
			try { moods = JSON.parse($data.attr('data-moods') || '[]'); } catch (e) {}
			$qe.find('.hfx-qe-mood').each(function () {
				$(this).prop('checked', moods.indexOf($(this).val()) !== -1);
			});

			$qe.find('#hfx-qe-initialized').val('1');
		}

		// MutationObserver: fires the instant the quick-edit row enters the DOM,
		// regardless of script load order or TEC overrides on inlineEditPost.edit.
		new MutationObserver(function (mutations) {
			mutations.forEach(function (m) {
				m.addedNodes.forEach(function (node) {
					if (node.nodeType !== 1) return;
					var match = (node.id || '').match(/^edit-(\d+)$/);
					if (match) hfxFillQuickEdit(parseInt(match[1], 10));
				});
			});
		}).observe(document.body, { childList: true, subtree: true });
	}(jQuery));
	</script>
	<?php
}

// ── Save quick-edit fields ────────────────────────────────────────────────────

add_action( 'save_post_tribe_events', 'hfx_save_quick_edit_event' );
function hfx_save_quick_edit_event( $post_id ) {
	if ( ! isset( $_POST['hfx_qe_nonce'] ) ) {
		return;
	}
	if ( ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['hfx_qe_nonce'] ) ), 'hfx_quick_edit' ) ) {
		return;
	}
	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}
	if ( defined( 'DOING_AUTOSAVE' ) && DOING_AUTOSAVE ) {
		return;
	}

	// Only trust empty/unchecked values when JS confirmed it pre-populated the form.
	// If JS didn't run, skip overwriting existing data with defaults.
	$initialized = isset( $_POST['hfx_qe_initialized'] ) && '1' === $_POST['hfx_qe_initialized'];

	// Venue — always save (dropdown always sends a value).
	if ( isset( $_POST['hfx_qe_venue_id'] ) ) {
		$venue_id = absint( $_POST['hfx_qe_venue_id'] );
		if ( $venue_id > 0 && get_post_type( $venue_id ) === 'tribe_venue' ) {
			update_post_meta( $post_id, '_EventVenueID', $venue_id );
		} elseif ( 0 === $venue_id && $initialized ) {
			delete_post_meta( $post_id, '_EventVenueID' );
		}
	}

	// Price — always save (text field, user can see its value).
	update_post_meta(
		$post_id,
		'_EventCost',
		isset( $_POST['hfx_qe_price'] ) ? sanitize_text_field( wp_unslash( $_POST['hfx_qe_price'] ) ) : ''
	);

	// Neighbourhood — only clear if JS confirmed the form was pre-populated.
	$new_hood = isset( $_POST['hfx_qe_hood'] ) ? sanitize_text_field( wp_unslash( $_POST['hfx_qe_hood'] ) ) : '';
	if ( $new_hood !== '' || $initialized ) {
		update_post_meta( $post_id, 'hfx_neighbourhood', $new_hood );
	}

	// Critic's pick — only save 0 (uncheck) if JS confirmed pre-population.
	$new_pick = isset( $_POST['hfx_qe_pick'] ) ? 1 : 0;
	if ( $new_pick === 1 || $initialized ) {
		update_post_meta( $post_id, 'hfx_critic_pick', $new_pick );
	}

	// Moods — only overwrite with empty if JS confirmed pre-population.
	$new_moods = array();
	if ( isset( $_POST['hfx_qe_moods'] ) && is_array( $_POST['hfx_qe_moods'] ) ) {
		$new_moods = array_map( 'sanitize_key', array_map( 'wp_unslash', $_POST['hfx_qe_moods'] ) );
	}
	if ( ! empty( $new_moods ) || $initialized ) {
		update_post_meta( $post_id, 'hfx_moods', $new_moods );
	}

	// Dates: only save when both date and time are provided and valid.
	if ( ! empty( $_POST['hfx_qe_start_date'] ) && ! empty( $_POST['hfx_qe_start_time'] ) ) {
		$start_date = sanitize_text_field( wp_unslash( $_POST['hfx_qe_start_date'] ) );
		$start_time = sanitize_text_field( wp_unslash( $_POST['hfx_qe_start_time'] ) );
		$start_dt   = date_create_from_format( 'Y-m-d H:i', $start_date . ' ' . $start_time );
		if ( $start_dt ) {
			$formatted = $start_dt->format( 'Y-m-d H:i:s' );
			update_post_meta( $post_id, '_EventStartDate', $formatted );
			update_post_meta( $post_id, '_EventStartDateUTC', $formatted );
		}
	}

	if ( ! empty( $_POST['hfx_qe_end_date'] ) && ! empty( $_POST['hfx_qe_end_time'] ) ) {
		$end_date = sanitize_text_field( wp_unslash( $_POST['hfx_qe_end_date'] ) );
		$end_time = sanitize_text_field( wp_unslash( $_POST['hfx_qe_end_time'] ) );
		$end_dt   = date_create_from_format( 'Y-m-d H:i', $end_date . ' ' . $end_time );
		if ( $end_dt ) {
			$formatted = $end_dt->format( 'Y-m-d H:i:s' );
			update_post_meta( $post_id, '_EventEndDate', $formatted );
			update_post_meta( $post_id, '_EventEndDateUTC', $formatted );
		}
	}
}
