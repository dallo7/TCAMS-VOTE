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
