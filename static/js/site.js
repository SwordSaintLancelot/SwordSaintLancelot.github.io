(function () {
  "use strict";

  // ---------- Theme toggle ----------
  function currentResolvedTheme() {
    var explicit = document.documentElement.getAttribute("data-theme");
    if (explicit === "dark" || explicit === "light") return explicit;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  var toggle = document.querySelector("[data-theme-toggle]");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var next = currentResolvedTheme() === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      toggle.setAttribute("aria-label", "Switch to " + (next === "dark" ? "light" : "dark") + " theme");
    });
  }

  // ---------- Mobile nav ----------
  var nav = document.querySelector("[data-site-nav]");
  var menuToggle = nav && nav.querySelector(".site-nav__menu-toggle");
  if (nav && menuToggle) {
    menuToggle.addEventListener("click", function () {
      var open = nav.getAttribute("data-open") === "true";
      nav.setAttribute("data-open", open ? "false" : "true");
      menuToggle.setAttribute("aria-expanded", open ? "false" : "true");
    });
    nav.querySelectorAll(".site-nav__links a").forEach(function (a) {
      a.addEventListener("click", function () {
        nav.setAttribute("data-open", "false");
        menuToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  // ---------- Entrance animations ----------
  // Only run when .js-anim is set (pre-paint check in <head> already
  // confirmed JS is on and the user hasn't asked for reduced motion).
  if (document.documentElement.classList.contains("js-anim") && "IntersectionObserver" in window) {
    var targets = document.querySelectorAll(
      "main section:not(.hero), .card, .skill-panel, .timeline__item, .entry"
    );
    var revealIO = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          obs.unobserve(e.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    targets.forEach(function (t) { revealIO.observe(t); });
  }

  // ---------- Project subpage TOC active state ----------
  var toc = document.querySelector(".project-toc");
  if (toc && "IntersectionObserver" in window) {
    var links = Array.from(toc.querySelectorAll("a[data-toc-target]"));
    var linkById = {};
    links.forEach(function (a) { linkById[a.dataset.tocTarget] = a; });
    var setActive = function (id) {
      links.forEach(function (l) { l.classList.remove("is-active"); });
      if (linkById[id]) linkById[id].classList.add("is-active");
    };
    var tocIO = new IntersectionObserver(function (entries) {
      // Pick the entry whose heading is highest in the viewport.
      var visible = entries.filter(function (e) { return e.isIntersecting; });
      if (!visible.length) return;
      visible.sort(function (a, b) { return a.boundingClientRect.top - b.boundingClientRect.top; });
      setActive(visible[0].target.id);
    }, { rootMargin: "-25% 0px -65% 0px" });
    Object.keys(linkById).forEach(function (id) {
      var h = document.getElementById(id);
      if (h) tocIO.observe(h);
    });
  }
})();
