(function () {
  "use strict";

  const data = window.HFXThemeData || {};
  const events = Array.isArray(data.events) ? data.events : [];

  function parseDateTime(dateStr, timeStr) {
    if (!dateStr) return null;
    const t = timeStr || "00:00";
    const d = new Date(`${dateStr}T${t}:00`);
    return Number.isNaN(d.getTime()) ? null : d;
  }

  function isSameDay(a, b) {
    return (
      a.getFullYear() === b.getFullYear() &&
      a.getMonth() === b.getMonth() &&
      a.getDate() === b.getDate()
    );
  }

  function nowDate() {
    const now = data.now ? new Date(data.now.replace(" ", "T")) : new Date();
    return Number.isNaN(now.getTime()) ? new Date() : now;
  }

  function matchesQuickFilter(row, quick, now) {
    if (!quick) return true;
    const rowDate = row.dataset.date || "";
    const rowTime = row.dataset.time || "00:00";
    const d = parseDateTime(rowDate, rowTime);
    if (!d) return false;

    if (quick === "tonight") return isSameDay(d, now);
    if (quick === "tomorrow") {
      const tomorrow = new Date(now);
      tomorrow.setDate(now.getDate() + 1);
      return isSameDay(d, tomorrow);
    }
    if (quick === "weekend") {
      const day = d.getDay();
      return day === 5 || day === 6 || day === 0;
    }
    if (quick === "free") return row.dataset.price === "free";
    return true;
  }

  function applyBrowseFilters() {
    const browseRoot = document.querySelector("[data-hfx-browse]");
    if (!browseRoot) return;

    const list = browseRoot.querySelector("[data-hfx-list]");
    const rows = list ? Array.from(list.querySelectorAll(".hfx-event-row")) : [];
    const emptyState = browseRoot.querySelector("[data-hfx-empty]");
    const countRoot = browseRoot.querySelector("[data-hfx-count]");
    const searchInput = browseRoot.querySelector("[data-hfx-live-search]");
    const quickButtons = Array.from(
      browseRoot.querySelectorAll("[data-hfx-quick]")
    );
    const clearButton = browseRoot.querySelector("[data-hfx-clear]");

    let activeQuick = browseRoot.dataset.quick || "";
    let activeDate = browseRoot.dataset.dateFilter || "";
    let searchTerm = "";

    const render = function () {
      const now = nowDate();
      let visibleCount = 0;
      rows.forEach((row) => {
        const title = row.dataset.title || "";
        const venue = row.dataset.venue || "";
        const searchable = `${title} ${venue}`;
        const quickMatch = matchesQuickFilter(row, activeQuick, now);
        const dateMatch = !activeDate || row.dataset.date === activeDate;
        const searchMatch = !searchTerm || searchable.includes(searchTerm);
        const visible = quickMatch && dateMatch && searchMatch;
        row.hidden = !visible;
        if (visible) visibleCount += 1;
      });

      quickButtons.forEach((btn) => {
        btn.classList.toggle("on", btn.dataset.hfxQuick === activeQuick);
      });

      if (emptyState) emptyState.hidden = visibleCount > 0;
      if (countRoot) {
        countRoot.innerHTML = `<em>${visibleCount}</em><span class="sub">events · sorted by date</span>`;
      }
    };

    quickButtons.forEach((button) => {
      button.addEventListener("click", () => {
        activeQuick = activeQuick === button.dataset.hfxQuick ? "" : button.dataset.hfxQuick;
        render();
      });
    });

    if (clearButton) {
      clearButton.addEventListener("click", () => {
        activeQuick = "";
        activeDate = "";
        searchTerm = "";
        if (searchInput) searchInput.value = "";
        render();
      });
    }

    if (searchInput) {
      searchInput.addEventListener("input", () => {
        searchTerm = searchInput.value.trim().toLowerCase();
        render();
      });
    }

    render();
  }

  function bindSurpriseButtons() {
    const buttons = Array.from(document.querySelectorAll("[data-hfx-surprise]"));
    if (!buttons.length || !events.length) return;

    buttons.forEach((button) => {
      button.addEventListener("click", (ev) => {
        ev.preventDefault();
        const event = events[Math.floor(Math.random() * events.length)];
        if (event && event.url) window.location.href = event.url;
      });
    });
  }

  function bindHeroSearch() {
    const input = document.querySelector("[data-hfx-search]");
    const button = document.querySelector("[data-hfx-search-submit]");
    if (!input || !button) return;

    button.addEventListener("click", function () {
      const q = input.value.trim();
      const base =
        data.browseUrl || `${window.location.origin}/browse/`;
      if (!q) {
        window.location.href = base;
        return;
      }
      window.location.href = `${base}?s=${encodeURIComponent(q)}`;
    });
  }

  function renderMapPins() {
    const mapRoot = document.querySelector("[data-hfx-map-canvas]");
    if (!mapRoot || !events.length) return;

    // Relative pseudo coordinates for Halifax neighborhoods.
    const hoodCoords = {
      Halifax: { x: 55, y: 45 },
      Downtown: { x: 60, y: 55 },
      Dartmouth: { x: 75, y: 50 },
      "North End": { x: 45, y: 35 },
      "South End": { x: 58, y: 70 },
      Bedford: { x: 32, y: 20 },
    };

    events.slice(0, 80).forEach((event, index) => {
      const point = hoodCoords[event.hood] || hoodCoords.Halifax;
      const jitter = (index % 7) - 3;
      const pin = document.createElement("a");
      pin.className = "hfx-map-pin";
      pin.href = event.url || "#";
      pin.title = event.title || "Event";
      pin.style.left = `calc(${point.x}% + ${jitter * 2}px)`;
      pin.style.top = `calc(${point.y}% + ${jitter * 2}px)`;
      mapRoot.appendChild(pin);
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindSurpriseButtons();
    bindHeroSearch();
    applyBrowseFilters();
    renderMapPins();
  });
})();
