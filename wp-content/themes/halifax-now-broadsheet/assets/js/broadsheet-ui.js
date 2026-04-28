(function () {
  "use strict";

  const data = window.HFXThemeData || {};
  const events = Array.isArray(data.events) ? data.events : [];
  const HALIFAX_TZ = "America/Halifax";

  function ymdInTimeZone(date, timeZone) {
    const parts = new Intl.DateTimeFormat("en-US", {
      timeZone,
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
    }).formatToParts(date);
    const year = parts.find((p) => p.type === "year")?.value || "1970";
    const month = parts.find((p) => p.type === "month")?.value || "01";
    const day = parts.find((p) => p.type === "day")?.value || "01";
    return `${year}-${month}-${day}`;
  }

  function addDaysYmd(ymd, days) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd);
    if (!m) return ymd;
    const dt = new Date(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3])));
    dt.setUTCDate(dt.getUTCDate() + days);
    return dt.toISOString().slice(0, 10);
  }

  function weekdayFromYmd(ymd) {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(ymd);
    if (!m) return NaN;
    const noonUtc = new Date(Date.UTC(Number(m[1]), Number(m[2]) - 1, Number(m[3]), 12, 0, 0));
    return noonUtc.getUTCDay();
  }

  function nowDate() {
    const now = data.now ? new Date(data.now.replace(" ", "T")) : new Date();
    return Number.isNaN(now.getTime()) ? new Date() : now;
  }

  function matchesQuickFilter(row, quick, now) {
    if (!quick) return true;
    const rowDate = row.dataset.date || "";
    if (!rowDate) return false;

    const todayYmdHalifax = ymdInTimeZone(now, HALIFAX_TZ);
    if (quick === "tonight") return rowDate === todayYmdHalifax;
    if (quick === "tomorrow") {
      return rowDate === addDaysYmd(todayYmdHalifax, 1);
    }
    if (quick === "weekend") {
      const day = weekdayFromYmd(rowDate);
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
    const filterButtons = Array.from(
      browseRoot.querySelectorAll("[data-hfx-filter]")
    );

    let activeQuick = browseRoot.dataset.quick || "";
    let activeDate = browseRoot.dataset.dateFilter || "";
    let searchTerm = (browseRoot.dataset.search || "").trim().toLowerCase();
    const selected = {
      category: new Set(
        filterButtons
          .filter((btn) => btn.classList.contains("on") && btn.dataset.hfxFilter === "category")
          .map((btn) => (btn.dataset.value || "").toLowerCase())
      ),
      mood: new Set(
        filterButtons
          .filter((btn) => btn.classList.contains("on") && btn.dataset.hfxFilter === "mood")
          .map((btn) => (btn.dataset.value || "").toLowerCase())
      ),
      hood: new Set(
        filterButtons
          .filter((btn) => btn.classList.contains("on") && btn.dataset.hfxFilter === "hood")
          .map((btn) => btn.dataset.value || "")
      ),
    };

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
        const cat = (row.dataset.category || "").toLowerCase();
        const hood = row.dataset.hood || "";
        const rowMoods = (row.dataset.moods || "")
          .split(",")
          .map((m) => m.trim().toLowerCase())
          .filter(Boolean);
        const categoryMatch =
          selected.category.size === 0 || selected.category.has(cat);
        const hoodMatch =
          selected.hood.size === 0 || selected.hood.has(hood);
        const moodMatch =
          selected.mood.size === 0 ||
          rowMoods.some((m) => selected.mood.has(m));
        const visible =
          quickMatch &&
          dateMatch &&
          searchMatch &&
          categoryMatch &&
          hoodMatch &&
          moodMatch;
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
        selected.category.clear();
        selected.mood.clear();
        selected.hood.clear();
        filterButtons.forEach((btn) => btn.classList.remove("on"));
        if (searchInput) searchInput.value = "";
        render();
      });
    }

    if (searchInput) {
      if (searchTerm && !searchInput.value) {
        searchInput.value = browseRoot.dataset.search || "";
      }
      searchInput.addEventListener("input", () => {
        searchTerm = searchInput.value.trim().toLowerCase();
        render();
      });
      searchInput.addEventListener("keydown", (event) => {
        if (event.key !== "Enter") return;
        event.preventDefault();
        searchTerm = searchInput.value.trim().toLowerCase();
        render();
      });
    }

    filterButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const group = button.dataset.hfxFilter;
        const value = (button.dataset.value || "").trim();
        if (!group || !value || !selected[group]) return;
        if (selected[group].has(value)) {
          selected[group].delete(value);
          button.classList.remove("on");
        } else {
          selected[group].add(value);
          button.classList.add("on");
        }
        render();
      });
    });

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
        data.browseUrl || `${window.location.origin}/events/`;
      if (!q) {
        window.location.href = base;
        return;
      }
      window.location.href = `${base}?s=${encodeURIComponent(q)}`;
    });
  }

  function renderMapPins() {
    const mapRoot = document.querySelector("[data-hfx-map-canvas]");
    if (!mapRoot || typeof window.L === "undefined") return;

    const withCoords = events
      .map((event) => {
        const lat = Number(event.lat);
        const lng = Number(event.lng);
        if (
          !Number.isFinite(lat) ||
          !Number.isFinite(lng) ||
          (Math.abs(lat) < 0.0001 && Math.abs(lng) < 0.0001)
        ) {
          return null;
        }
        return { ...event, lat, lng };
      })
      .filter(Boolean);

    const map = window.L.map(mapRoot, {
      center: [44.649, -63.575],
      zoom: 13,
      scrollWheelZoom: false,
    });

    window.L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      { subdomains: "abcd", maxZoom: 19 }
    ).addTo(map);

    if (!withCoords.length) {
      return;
    }

    const bounds = [];
    withCoords.forEach((event) => {
      const hue = Number.isFinite(event.hue) ? event.hue : 210;
      const isPick = Boolean(event.critic);
      const markerHtml = `<div class="hfx-leaflet-pin${
        isPick ? " pick" : ""
      }" style="${isPick ? "" : `--pin-hue:${Math.round(hue)};`}">${
        isPick ? "★" : ""
      }</div>`;
      const marker = window.L.marker([event.lat, event.lng], {
        icon: window.L.divIcon({
          className: "hfx-leaflet-icon",
          html: markerHtml,
          iconSize: isPick ? [28, 28] : [22, 22],
          iconAnchor: isPick ? [14, 14] : [11, 11],
        }),
      });
      marker.bindPopup(
        `<strong>${event.title || "Event"}</strong><br>${event.venue || ""}<br>${
          event.time || ""
        } · ${event.priceLabel || ""}`
      );
      marker.addTo(map);
      bounds.push([event.lat, event.lng]);
    });

    if (bounds.length > 1) {
      map.fitBounds(bounds, { padding: [24, 24] });
    }
  }

  document.addEventListener("DOMContentLoaded", function () {
    bindSurpriseButtons();
    bindHeroSearch();
    applyBrowseFilters();
    renderMapPins();
  });
})();
