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
	$new = array();
	foreach ( $cols as $key => $label ) {
		$new[ $key ] = $label;
		if ( 'title' === $key ) {
			$new['hfx_venue'] = 'Venue';
			$new['hfx_price'] = 'Price';
			$new['hfx_hood']  = 'Neighbourhood';
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
				$v = (string) tribe_get_venue( $post_id );
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
			$price    = trim( (string) get_post_meta( $post_id, '_EventCost', true ) );
			$hood     = trim( (string) get_post_meta( $post_id, 'hfx_neighbourhood', true ) );
			$moods_raw = get_post_meta( $post_id, 'hfx_moods', true );
			$moods    = is_array( $moods_raw ) ? $moods_raw
				: ( is_string( $moods_raw ) && $moods_raw !== '' ? array_map( 'trim', explode( ',', $moods_raw ) ) : array() );

			printf(
				'<span class="hfx-row-data" style="display:none" data-price="%s" data-hood="%s" data-pick="%s" data-moods="%s"></span>',
				esc_attr( $price ),
				esc_attr( $hood ),
				esc_attr( $is_pick ? '1' : '0' ),
				esc_attr( (string) wp_json_encode( array_values( $moods ) ) )
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
	.column-hfx_venue { width: 150px; }
	.column-hfx_price { width: 68px; }
	.column-hfx_hood  { width: 120px; }
	.column-hfx_pick  { width: 30px; text-align: center !important; }
	td.column-hfx_pick { text-align: center; }
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

	wp_nonce_field( 'hfx_quick_edit', 'hfx_qe_nonce' );
	?>
	<div id="hfx-quick-edit">
		<h4>Halifax Now</h4>
		<div class="hfx-qe-row">

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
		var _orig = inlineEditPost.edit;
		inlineEditPost.edit = function (id) {
			_orig.apply(this, arguments);
			var postId = typeof id === 'object' ? parseInt(this.getId(id), 10) : parseInt(id, 10);
			if (!postId) return;

			var $data = $('#post-' + postId).find('.hfx-row-data');
			var $qe   = $('#edit-' + postId);

			$qe.find('#hfx-qe-price').val($data.data('price') || '');
			$qe.find('#hfx-qe-hood').val($data.data('hood') || '');
			$qe.find('#hfx-qe-pick').prop('checked', String($data.data('pick')) === '1');

			var moods = $data.data('moods') || [];
			$qe.find('.hfx-qe-mood').each(function () {
				$(this).prop('checked', moods.indexOf($(this).val()) !== -1);
			});
		};
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

	update_post_meta(
		$post_id,
		'_EventCost',
		isset( $_POST['hfx_qe_price'] ) ? sanitize_text_field( wp_unslash( $_POST['hfx_qe_price'] ) ) : ''
	);

	update_post_meta(
		$post_id,
		'hfx_neighbourhood',
		isset( $_POST['hfx_qe_hood'] ) ? sanitize_text_field( wp_unslash( $_POST['hfx_qe_hood'] ) ) : ''
	);

	update_post_meta(
		$post_id,
		'hfx_critic_pick',
		isset( $_POST['hfx_qe_pick'] ) ? 1 : 0
	);

	$moods = array();
	if ( isset( $_POST['hfx_qe_moods'] ) && is_array( $_POST['hfx_qe_moods'] ) ) {
		$moods = array_map( 'sanitize_key', array_map( 'wp_unslash', $_POST['hfx_qe_moods'] ) );
	}
	update_post_meta( $post_id, 'hfx_moods', $moods );
}
