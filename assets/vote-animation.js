(function () {
  function removeBuildBadge() {
    var badge = document.getElementById("app-build-badge");
    if (badge) {
      badge.remove();
    }
    document.querySelectorAll(".app-build-badge").forEach(function (node) {
      if (/^Build\s/i.test(node.textContent || "")) {
        node.remove();
      }
    });
  }

  removeBuildBadge();
  document.addEventListener("DOMContentLoaded", removeBuildBadge);
  if (window.MutationObserver) {
    new MutationObserver(removeBuildBadge).observe(document.documentElement, {
      childList: true,
      subtree: true,
    });
  }
})();

window.tcamsAnimateVote = function (choice) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  var btnId = {
    yes: "btn-vote-yes",
    no: "btn-vote-no",
    not_sure: "btn-vote-not-sure",
  }[choice];

  var barId = "bar-" + choice;
  var btn = document.getElementById(btnId);
  var bar = document.getElementById(barId);
  if (!btn || !bar) {
    return;
  }

  var btnRect = btn.getBoundingClientRect();
  var barRect = bar.getBoundingClientRect();

  var block = document.createElement("div");
  block.className = "vote-block vote-block--" + choice;
  block.style.left = btnRect.left + btnRect.width / 2 - 14 + "px";
  block.style.top = btnRect.top + btnRect.height / 2 - 14 + "px";
  document.body.appendChild(block);

  var startX = btnRect.left + btnRect.width / 2;
  var startY = btnRect.top + btnRect.height / 2;
  var endX = barRect.left + barRect.width / 2;
  var endY = barRect.top + barRect.height / 2;
  var duration = 700;
  var start = null;

  function easeOut(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function frame(ts) {
    if (!start) start = ts;
    var progress = Math.min((ts - start) / duration, 1);
    var eased = easeOut(progress);
    var x = startX + (endX - startX) * eased;
    var arc = Math.sin(Math.PI * eased) * -80;
    var y = startY + (endY - startY) * eased + arc;
    block.style.transform = "translate(" + (x - startX) + "px, " + (y - startY) + "px) rotate(" + eased * 360 + "deg)";

    if (progress < 1) {
      requestAnimationFrame(frame);
    } else {
      block.remove();
      bar.classList.add("pulse");
      setTimeout(function () {
        bar.classList.remove("pulse");
      }, 450);
    }
  }

  requestAnimationFrame(frame);
};

window.tcamsFireworks = function (anchorId) {
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    return;
  }

  var anchor = document.getElementById(anchorId || "vote-feedback");
  var rect = anchor
    ? anchor.getBoundingClientRect()
    : { left: window.innerWidth / 2, top: window.innerHeight / 3, width: 0, height: 0 };
  var cx = rect.left + rect.width / 2;
  var cy = rect.top + rect.height / 2;
  var colors = ["#40a247", "#c9a414", "#1f3a6e", "#6ab04c", "#ffffff"];

  function burst(originX, originY, count, spread, delayMs) {
    setTimeout(function () {
      var layer = document.createElement("div");
      layer.className = "tcams-fireworks";
      document.body.appendChild(layer);

      for (var i = 0; i < count; i++) {
        var particle = document.createElement("span");
        particle.className = "tcams-firework-particle";
        var angle = (Math.PI * 2 * i) / count + Math.random() * 0.5;
        var distance = spread * (0.55 + Math.random() * 0.45);
        particle.style.left = originX + "px";
        particle.style.top = originY + "px";
        particle.style.background = colors[i % colors.length];
        particle.style.setProperty("--fx-x", Math.cos(angle) * distance + "px");
        particle.style.setProperty("--fx-y", Math.sin(angle) * distance + "px");
        particle.style.animationDelay = Math.random() * 0.08 + "s";
        layer.appendChild(particle);
      }

      setTimeout(function () {
        layer.remove();
      }, 1100);
    }, delayMs);
  }

  burst(cx, cy, 22, 55, 0);
  burst(cx - 30, cy - 8, 14, 38, 180);
  burst(cx + 28, cy - 6, 14, 38, 320);
};

window.tcamsCelebrateVote = function (anchorId) {
  var attempts = 0;
  function tryFireworks() {
    var el = document.getElementById(anchorId || "vote-feedback");
    if (el && el.offsetParent !== null && el.getBoundingClientRect().height > 0) {
      window.tcamsFireworks(anchorId || "vote-feedback");
      return;
    }
    attempts += 1;
    if (attempts < 12) {
      setTimeout(tryFireworks, 50);
    }
  }
  tryFireworks();
};
