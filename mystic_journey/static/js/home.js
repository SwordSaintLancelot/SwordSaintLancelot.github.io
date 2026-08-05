/* The Traveler's Atlas — homepage scene.
 * Progressive enhancement over server-rendered islands: everything below is
 * decoration. Without JS the page is a complete, clickable static scene.
 */
(function () {
  "use strict";

  var dataEl = document.getElementById("atlas-data");
  if (!dataEl) return;
  var DATA = JSON.parse(dataEl.textContent);

  var scene = document.getElementById("scene");
  var guide = document.getElementById("guide");
  var bubble = document.getElementById("bubble");
  var bubbleText = document.getElementById("bubble-text");
  var hint = document.getElementById("hint");
  var caption = document.getElementById("wander-caption");
  var islands = Array.prototype.slice.call(document.querySelectorAll(".island"));

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var mobile = window.matchMedia("(max-width: 767px)").matches;
  var introPending = document.documentElement.classList.contains("intro");

  function markIntroDone() {
    try { sessionStorage.setItem("mj_intro", "1"); } catch (e) {}
    document.documentElement.classList.remove("intro");
  }

  /* ---------------------------------------------------------- guide anchor */
  var anchors = DATA.guide.anchors || [];
  var anchor = anchors[Math.floor(Math.random() * anchors.length)] || { x: 50, y: 62 };
  guide.style.setProperty("--gx", anchor.x);
  guide.style.setProperty("--gy", anchor.y);

  // Idle line: greeting on the first (choreographed) visit, the anchor's own
  // remark on repeat visits. Hover teasers temporarily replace it.
  var idleText = introPending ? DATA.guide.greeting : (anchor.remark || DATA.guide.greeting);

  /* Accessible bubble: full text in a visually-hidden span (announced via
     aria-live), typed/visible text hidden from the tree. */
  var srSpan = document.createElement("span");
  srSpan.className = "sr-only";
  var visSpan = document.createElement("span");
  visSpan.setAttribute("aria-hidden", "true");
  bubbleText.textContent = "";
  bubbleText.appendChild(srSpan);
  bubbleText.appendChild(visSpan);

  function setBubble(text) {
    srSpan.textContent = text;
    visSpan.textContent = text;
    placeBubble();
  }

  var typeTimer = null;
  function typeBubble(text, done) {
    clearInterval(typeTimer);
    srSpan.textContent = text;
    visSpan.textContent = "";
    placeBubble(text);
    var i = 0;
    typeTimer = setInterval(function () {
      i += 1;
      visSpan.textContent = text.slice(0, i);
      if (i >= text.length) {
        clearInterval(typeTimer);
        if (done) done();
      }
    }, 26);
  }

  /* Edge-aware placement beside the guide (desktop; CSS pins it on mobile). */
  function placeBubble(measureText) {
    if (mobile) return;
    var g = guide.getBoundingClientRect();
    var vw = window.innerWidth, vh = window.innerHeight;
    if (measureText) visSpan.textContent = measureText; // measure at full size
    var b = bubble.getBoundingClientRect();
    var side = g.left + g.width / 2 > vw * 0.66 ? "left" : "right";
    var x, y = g.top + g.height * 0.12;
    if (side === "right") x = g.right + 14; else x = g.left - b.width - 14;
    bubble.classList.remove("bubble--left", "bubble--right", "bubble--below");
    if (g.top < vh * 0.16) { // too high: drop below the guide
      bubble.classList.add("bubble--below");
      x = Math.min(Math.max(12, g.left + g.width / 2 - b.width / 2), vw - b.width - 12);
      y = g.bottom + 14;
    } else {
      bubble.classList.add(side === "right" ? "bubble--right" : "bubble--left");
      y = Math.min(Math.max(64, y), vh - b.height - 12);
      x = Math.min(Math.max(12, x), vw - b.width - 12);
    }
    bubble.style.left = x + "px";
    bubble.style.top = y + "px";
    if (measureText) visSpan.textContent = "";
  }

  /* -------------------------------------------- jitter + minimum distance */
  /* Base positions come from the data file; each load nudges them ±2.5% and
     then relaxes collisions so islands never overlap each other, the guide,
     or the screen edges. Desktop only — mobile flows in-document. */
  function layoutIslands() {
    if (mobile) return;
    var vw = window.innerWidth, vh = window.innerHeight;
    var bodies = islands.map(function (el) {
      var meta = DATA.realms.filter(function (r) { return r.slug === el.dataset.slug; })[0];
      var jx = (Math.random() * 5 - 2.5), jy = (Math.random() * 5 - 2.5);
      var w = el.offsetWidth || 220;
      return {
        el: el, meta: meta,
        x: (meta.x + jx) / 100 * vw,
        y: (meta.y + jy) / 100 * vh,
        r: Math.max(w, w * 9 / 16 + 30) / 2 * 0.78
      };
    });
    // the guide + the space its speech bubble occupies are both no-fly zones
    var ax = anchor.x / 100 * vw, ay = anchor.y / 100 * vh;
    var bubbleSide = anchor.x > 66 ? -1 : 1;
    var obstacles = bodies.concat([
      { x: ax, y: ay, r: 85, fixed: true },
      { x: ax + bubbleSide * 190, y: ay - 20, r: 110, fixed: true }
    ]);

    for (var iter = 0; iter < 40; iter++) {
      var moved = false;
      for (var i = 0; i < obstacles.length; i++) {
        for (var j = i + 1; j < obstacles.length; j++) {
          var a = obstacles[i], b = obstacles[j];
          var dx = b.x - a.x, dy = b.y - a.y;
          var dist = Math.sqrt(dx * dx + dy * dy) || 1;
          var min = a.r + b.r + 24;
          if (dist < min) {
            var push = (min - dist) / 2;
            var ux = dx / dist, uy = dy / dist;
            if (!a.fixed) { a.x -= ux * push; a.y -= uy * push; }
            if (!b.fixed) { b.x += ux * push; b.y += uy * push; }
            moved = true;
          }
        }
      }
      // clamp to cluster bounds + viewport margins
      bodies.forEach(function (p) {
        var bounds = DATA.clusters[p.meta.cluster].bounds;
        var mx = Math.max(p.r * 0.75, 30);
        p.x = Math.min(Math.max(p.x, Math.max(bounds.x_min / 100 * vw, mx)),
                       Math.min(bounds.x_max / 100 * vw, vw - mx));
        p.y = Math.min(Math.max(p.y, Math.max(bounds.y_min / 100 * vh, 84)),
                       Math.min(bounds.y_max / 100 * vh, vh - mx));
      });
      if (!moved) break;
    }

    bodies.forEach(function (p) {
      p.el.style.setProperty("--x", (p.x / vw * 100).toFixed(2));
      p.el.style.setProperty("--y", (p.y / vh * 100).toFixed(2));
    });
  }

  /* ----------------------------------------------------- pointer parallax */
  function initParallax() {
    if (reduced || mobile || !window.matchMedia("(pointer: fine)").matches) return;
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
    var bgImgs = document.querySelectorAll(".sky-bg img");
    function frame() {
      cx += (tx - cx) * 0.045;             // slow, calm easing
      cy += (ty - cy) * 0.045;
      scene.style.setProperty("--mx", cx.toFixed(4));
      scene.style.setProperty("--my", cy.toFixed(4));
      for (var i = 0; i < bgImgs.length; i++) {   // nebula: slowest response
        bgImgs[i].style.setProperty("--bgx", (cx * -5).toFixed(2) + "px");
        bgImgs[i].style.setProperty("--bgy", (cy * -5).toFixed(2) + "px");
      }
      if (Math.abs(tx - cx) + Math.abs(ty - cy) > 0.001) raf = requestAnimationFrame(frame);
      else raf = null;
    }
    window.addEventListener("pointermove", function (e) {
      tx = (e.clientX / window.innerWidth) * 2 - 1;
      ty = (e.clientY / window.innerHeight) * 2 - 1;
      if (!raf) raf = requestAnimationFrame(frame);
    }, { passive: true });
  }

  /* ------------------------------------------------ preloads on intention */
  /* A hidden <picture> mirroring the realm page's keyart markup, so the
     browser fetches exactly the format+size it will use on arrival. */
  var preloaded = {};
  function preloadKeyart(meta) {
    var ka = meta.keyart;
    if (!ka || preloaded[meta.slug]) return;
    preloaded[meta.slug] = true;
    var pic = document.createElement("picture");
    var sizes = "(max-width: 767px) 100vw, 30vw";
    if (ka.small_avif && ka.full_avif) {
      var sa = document.createElement("source");
      sa.srcset = ka.small_avif + " 800w, " + ka.full_avif + " 1672w";
      sa.sizes = sizes; sa.type = "image/avif";
      pic.appendChild(sa);
    }
    var sw = document.createElement("source");
    sw.srcset = ka.small_webp + " 800w, " + ka.full_webp + " 1672w";
    sw.sizes = sizes; sw.type = "image/webp";
    pic.appendChild(sw);
    var img = document.createElement("img");
    img.src = ka.small_webp;
    img.alt = "";
    pic.setAttribute("aria-hidden", "true");
    pic.style.cssText = "position:absolute;width:1px;height:1px;opacity:0;pointer-events:none";
    document.body.appendChild(pic);
    img.addEventListener("load", function () { pic.remove(); });
    pic.appendChild(img);
  }

  function preloadBlur() {
    if (preloaded.__blur) return;
    preloaded.__blur = true;
    var l = document.createElement("link");
    l.rel = "preload"; l.as = "image";
    l.href = DATA.blur.avif || DATA.blur.webp;
    document.head.appendChild(l);
  }

  /* ------------------------------------------------------- hover teasers */
  islands.forEach(function (el) {
    var meta = DATA.realms.filter(function (r) { return r.slug === el.dataset.slug; })[0];
    if (!meta) return;
    function tease() {
      if (introRunning) return;
      setBubble(meta.teaser);
      preloadKeyart(meta);
      preloadBlur();
    }
    function untease() {
      if (introRunning) return;
      setBubble(idleText);
    }
    el.addEventListener("mouseenter", tease);
    el.addEventListener("focus", tease);
    el.addEventListener("mouseleave", untease);
    el.addEventListener("blur", untease);
  });

  /* -------------------------------------------------- arrival choreography */
  var introRunning = false;

  function endState() {
    introRunning = false;
    markIntroDone();
    [guide, bubble, hint, caption].forEach(function (el) { el.style.opacity = 1; });
    islands.forEach(function (el) { el.style.opacity = 1; });
    clearInterval(typeTimer);
    setBubble(idleText);
  }

  function runIntro() {
    if (!introPending || reduced || mobile || typeof gsap === "undefined") {
      if (introPending) markIntroDone();
      setBubble(idleText);
      return;
    }
    introRunning = true;
    bubble.style.opacity = 0;
    var tl = gsap.timeline({
      defaults: { ease: "power2.out" },
      onComplete: function () {
        if (!introRunning) return;
        endState();
      }
    });
    // scene fades in — islands already drifting
    tl.to(islands, { opacity: 1, duration: 1.0, stagger: 0.07 }, 0);
    // the Wayfinder appears and gives a small wave (gentle rock)
    tl.to(guide, { opacity: 1, duration: 0.7 }, 0.9);
    tl.fromTo(guide.querySelector("picture"),
      { rotation: -6, transformOrigin: "50% 80%" },
      { rotation: 0, duration: 0.9, ease: "elastic.out(1, 0.6)" }, 1.1);
    // the bubble types its greeting
    tl.to(bubble, { opacity: 1, duration: 0.4 }, 1.5);
    tl.call(function () { typeBubble(DATA.guide.greeting); }, null, 1.6);
    // ~2s later the hint + wanderings caption breathe in
    tl.to(hint, { opacity: 1, duration: 0.9 }, 3.6);
    tl.to(caption, { opacity: 1, duration: 1.2 }, 3.6);
    tl.to({}, { duration: 0.1 }, 4.4); // hold the timeline open till ~4.5s

    // any click or keypress skips to the end state
    function skip(e) {
      if (e.type === "pointerdown" && e.target.closest(".island")) { /* island clicks always work */ }
      if (!introRunning) return;
      tl.progress(1).kill();
      endState();
      window.removeEventListener("pointerdown", skip, true);
      window.removeEventListener("keydown", skip, true);
    }
    window.addEventListener("pointerdown", skip, true);
    window.addEventListener("keydown", skip, true);
  }

  /* ------------------------------------------------- the suck-in transition */
  function initTransitions() {
    islands.forEach(function (el) {
      el.addEventListener("click", function (e) {
        // let modified clicks (new tab etc.) behave natively
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        e.preventDefault();
        markIntroDone();
        var href = el.getAttribute("href");
        var blurLayer = document.querySelector(".sky-bg__blur");

        if (reduced || typeof gsap === "undefined") {
          // plain fade, no zoom or blur animation
          var veil = document.createElement("div");
          veil.style.cssText = "position:fixed;inset:0;background:#050508;opacity:0;transition:opacity .25s ease;z-index:60";
          document.body.appendChild(veil);
          requestAnimationFrame(function () {
            requestAnimationFrame(function () { veil.style.opacity = 1; });
          });
          setTimeout(function () { window.location.href = href; }, 280);
          return;
        }

        var rect = el.getBoundingClientRect();
        var cx = rect.left + rect.width / 2, cy = rect.top + rect.height / 2;
        var vw = window.innerWidth, vh = window.innerHeight;
        var chosenBob = el.querySelector(".island__bob");

        // stop CSS bobbing so GSAP owns these transforms
        islands.forEach(function (o) {
          var b = o.querySelector(".island__bob");
          if (b) b.style.animation = "none";
        });

        var tl = gsap.timeline({
          defaults: { duration: 0.7, ease: "power2.in" },
          onComplete: function () { window.location.href = href; }
        });

        // everything else releases outward and fades
        islands.forEach(function (o) {
          if (o === el) return;
          var r = o.getBoundingClientRect();
          var dx = (r.left + r.width / 2) - cx, dy = (r.top + r.height / 2) - cy;
          var d = Math.sqrt(dx * dx + dy * dy) || 1;
          tl.to(o.querySelector(".island__bob"),
            { x: dx / d * 90, y: dy / d * 90, opacity: 0, duration: 0.55 }, 0);
        });
        tl.to([guide, bubble, hint, caption], { opacity: 0, duration: 0.45 }, 0);

        // the chosen realm rushes toward the camera…
        tl.to(chosenBob, {
          scale: 2.6,
          x: (vw / 2 - cx) * 0.4,
          y: (vh / 2 - cy) * 0.4,
          opacity: 0.98,
          duration: 0.75
        }, 0);
        // …while the nebula radial-blurs and darkens (precomputed twin fades in)
        tl.to(blurLayer, { opacity: 1, duration: 0.75, ease: "power2.inOut" }, 0);
        // navigation fires at the peak of the blur (timeline end ≈ 750ms)
      });
    });
  }

  /* -------------------------------------------------------------- run it */
  layoutIslands();
  placeBubble();
  initParallax();
  initTransitions();

  if (introPending && !reduced && !mobile) {
    if (typeof gsap === "undefined") {
      // GSAP CDN unavailable — settle instantly into the end state
      window.addEventListener("load", function () { markIntroDone(); setBubble(idleText); });
      markIntroDone();
      setBubble(idleText);
    } else {
      runIntro();
    }
  } else {
    if (introPending) markIntroDone();
    setBubble(idleText);
  }

  var relayout;
  window.addEventListener("resize", function () {
    clearTimeout(relayout);
    relayout = setTimeout(function () {
      mobile = window.matchMedia("(max-width: 767px)").matches;
      placeBubble();
    }, 150);
  });
})();
