/**
 * Halifax Now — Flavor 2 theme scripts
 */
(function () {
  'use strict';

  /* ── Filter chip toggle ── */
  document.querySelectorAll('.chip').forEach(function (chip) {
    chip.addEventListener('click', function () {
      document.querySelectorAll('.chip').forEach(function (c) {
        c.classList.remove('on');
      });
      this.classList.add('on');
    });
  });

  /* ── View toggle (Grid / List / Calendar) ── */
  document.querySelectorAll('.vt').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.vt').forEach(function (b) {
        b.classList.remove('on');
      });
      this.classList.add('on');
    });
  });
})();
