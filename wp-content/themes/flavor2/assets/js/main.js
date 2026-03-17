/**
 * Halifax Now — Flavor 2 theme scripts
 */
(function () {
  'use strict';

  /* ── Mobile nav toggle ── */
  var toggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('.nav-links');

  if (toggle && navLinks) {
    toggle.addEventListener('click', function () {
      var isOpen = navLinks.classList.toggle('open');
      toggle.classList.toggle('open', isOpen);
      toggle.setAttribute('aria-expanded', isOpen);
    });
  }

  /* ── Category filter chips ── */
  var chips = document.querySelectorAll('.chip');
  var activeFilter = 'all';

  // Map chip labels to data-category values
  var chipCategoryMap = {
    'all':             null,
    'this weekend':    '__weekend__',
    'free':            '__free__',
    'music':           'music',
    'arts & culture':  'arts & culture',
    'comedy':          'comedy',
    'community':       'community',
    'food & drink':    'food & drink',
    'outdoors':        'outdoors',
    'sports':          'sports',
    'family':          'family',
    'film':            'film'
  };

  // Aliases: some events use shorter category names
  function categoryMatches(itemCat, filterKey) {
    if (!filterKey) return true;
    var cat = (itemCat || '').toLowerCase();
    // Music can appear as "live music" or "music"
    if (filterKey === 'music') return cat.indexOf('music') !== -1;
    // Arts can appear as "arts", "arts & culture"
    if (filterKey === 'arts & culture') return cat.indexOf('art') !== -1;
    return cat.indexOf(filterKey) !== -1;
  }

  function applyFilter(filterLabel) {
    var key = filterLabel.toLowerCase();
    activeFilter = key;
    var mapValue = chipCategoryMap[key];

    // Get all filterable items (both grid cards and list items)
    var items = document.querySelectorAll('.ec[data-category], .eli[data-category]');

    items.forEach(function (item) {
      var show = true;

      if (key === 'free') {
        show = item.getAttribute('data-cost') === 'free';
      } else if (key === 'this weekend') {
        // Show all for "this weekend" — the query already scopes to this week
        show = true;
      } else if (mapValue) {
        show = categoryMatches(item.getAttribute('data-category'), mapValue);
      }
      // key === 'all' → show everything

      item.style.display = show ? '' : 'none';
    });
  }

  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      chips.forEach(function (c) { c.classList.remove('on'); });
      this.classList.add('on');
      applyFilter(this.textContent.trim());
    });
  });

  /* ── View toggle (Grid / List) ── */
  var viewButtons = document.querySelectorAll('.vt[data-view]');
  var gridView = document.querySelector('[data-view-target="grid"]');
  var listView = document.querySelector('[data-view-target="list"]');

  viewButtons.forEach(function (btn) {
    btn.addEventListener('click', function () {
      viewButtons.forEach(function (b) { b.classList.remove('on'); });
      this.classList.add('on');

      var view = this.getAttribute('data-view');

      if (gridView) gridView.style.display = (view === 'grid') ? '' : 'none';
      if (listView) listView.style.display = (view === 'list') ? '' : 'none';
    });
  });

  /* ── Search bar focus UX ── */
  var searchInput = document.querySelector('.search-bar input');
  if (searchInput) {
    searchInput.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        this.blur();
      }
    });
  }
})();
