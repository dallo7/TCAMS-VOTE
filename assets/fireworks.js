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
