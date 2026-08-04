/* Realm pages: arrival settle, ambient keyart parallax, and the release
 * back to the journey. Pure enhancement — the page is complete without it. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Arrival: keyart settles 110% -> ~100%, content fades up staggered (CSS). */
  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      document.body.classList.add("arrived");
    });
  });

  /* Scroll-revealed passages + artifacts. */
  var revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length && "IntersectionObserver" in window && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.15 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* Gentle pointer parallax on the keyart panel. */
  var keyart = document.querySelector(".keyart");
  if (keyart && !reduced && window.matchMedia("(pointer: fine)").matches) {
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = null;
    function frame() {
      cx += (tx - cx) * 0.05;
      cy += (ty - cy) * 0.05;
      keyart.style.setProperty("--kx", cx.toFixed(4));
      keyart.style.setProperty("--ky", cy.toFixed(4));
      if (Math.abs(tx - cx) + Math.abs(ty - cy) > 0.001) raf = requestAnimationFrame(frame);
      else raf = null;
    }
    window.addEventListener("pointermove", function (e) {
      tx = (e.clientX / window.innerWidth) * 2 - 1;
      ty = (e.clientY / window.innerHeight) * 2 - 1;
      if (!raf) raf = requestAnimationFrame(frame);
    }, { passive: true });
  }

  /* Return to the journey: quick release (~350ms fade/lift), landing on the
     homepage end state — the intro never replays (sessionStorage). */
  var ret = document.getElementById("return");
  if (ret) {
    ret.addEventListener("click", function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      e.preventDefault();
      try { sessionStorage.setItem("mj_intro", "1"); } catch (err) {}
      var href = ret.getAttribute("href");
      if (reduced) { window.location.href = href; return; }
      var veil = document.createElement("div");
      veil.className = "page-veil";
      document.body.appendChild(veil);
      requestAnimationFrame(function () {
        requestAnimationFrame(function () { document.body.classList.add("leaving"); });
      });
      setTimeout(function () { window.location.href = href; }, 380);
    });
  }
})();
