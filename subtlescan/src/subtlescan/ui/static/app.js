(function () {
  "use strict";
  var root = document.documentElement;
  root.classList.add("js");

  function store(key, value) {
    try { if (value === undefined) return localStorage.getItem(key); localStorage.setItem(key, value); } catch (e) { return null; }
  }

  // Theme
  var saved = store("subtlescan-theme");
  if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved);
  else if (window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches) root.setAttribute("data-theme", "dark");
  document.querySelector("[data-theme-toggle]").addEventListener("click", function () {
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    store("subtlescan-theme", next);
  });

  // Findings: filters and drill-down
  var form = document.querySelector("[data-filters]");
  var rows = Array.prototype.slice.call(document.querySelectorAll("tbody.finding"));
  var countEl = document.querySelector("[data-count]");
  var emptyEl = document.querySelector("[data-empty]");

  function applyFilters() {
    var q = form.q.value.trim().toLowerCase();
    var sev = form.severity.value, dom = form.domain.value, fw = form.framework.value, st = form.status.value;
    var shown = 0;
    rows.forEach(function (tb) {
      var d = tb.dataset;
      var ok = (!q || d.text.indexOf(q) !== -1) && (!sev || d.severity === sev) && (!dom || d.domain === dom) &&
        (!fw || (" " + d.frameworks + " ").indexOf(" " + fw + " ") !== -1) && (!st || d.status === st);
      tb.hidden = !ok;
      if (ok) shown++;
    });
    countEl.textContent = "Showing " + shown + " of " + rows.length + " findings";
    emptyEl.hidden = shown !== 0;
  }
  form.addEventListener("input", applyFilters);
  form.addEventListener("reset", function () { setTimeout(applyFilters, 0); });

  function toggle(tb, open) {
    var row = tb.querySelector(".row"), detail = tb.querySelector(".detail");
    if (open === undefined) open = detail.hidden;
    detail.hidden = !open;
    row.setAttribute("aria-expanded", String(open));
  }
  rows.forEach(function (tb) {
    var row = tb.querySelector(".row");
    row.addEventListener("click", function () { toggle(tb); });
    row.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); toggle(tb); }
    });
  });

  document.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-copy]");
    if (!btn) return;
    e.stopPropagation();
    var text = document.getElementById(btn.dataset.copy).textContent;
    var done = function () { btn.textContent = "Copied"; setTimeout(function () { btn.textContent = "Copy"; }, 1500); };
    if (navigator.clipboard) navigator.clipboard.writeText(text).then(done, function () {});
  });

  // Tiles and bars on Overview pre-filter the findings table.
  document.addEventListener("click", function (e) {
    var a = e.target.closest("[data-filter-severity],[data-filter-domain]");
    if (!a) return;
    form.reset();
    form.status.value = "open";
    if (a.dataset.filterSeverity) form.severity.value = a.dataset.filterSeverity;
    if (a.dataset.filterDomain) form.domain.value = a.dataset.filterDomain;
    applyFilters();
  });

  // Hash routing: #overview, #findings, #findings/<finding-id>
  var pages = document.querySelectorAll(".page");
  var tabs = document.querySelectorAll("[data-tab]");
  function route() {
    var parts = (location.hash.slice(1) || "overview").split("/");
    var page = document.getElementById("page-" + parts[0]) ? parts[0] : "overview";
    pages.forEach(function (p) { p.classList.toggle("active", p.id === "page-" + page); });
    tabs.forEach(function (t) {
      if (t.dataset.tab === page) t.setAttribute("aria-current", "page"); else t.removeAttribute("aria-current");
    });
    if (page === "findings" && parts[1]) {
      var tb = document.getElementById("f-" + parts[1]);
      if (tb) {
        if (tb.hidden) { form.reset(); form.status.value = ""; applyFilters(); }
        toggle(tb, true);
        tb.scrollIntoView({ block: "start" });
        window.scrollBy(0, -120);
        return;
      }
    }
    window.scrollTo(0, 0);
  }
  window.addEventListener("hashchange", route);
  applyFilters();
  route();
})();
