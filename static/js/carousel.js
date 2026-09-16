/**
 * 3D circular photo carousel for the "Step Inside" gallery section.
 * Plain CSS transforms + vanilla JS, per the design handoff's
 * "Interactions & Behavior" spec: auto-rotating oval ring of cards,
 * drag-to-spin, hover-to-pause/enlarge, and prev/next stepping.
 */
(function () {
  const stage = document.getElementById("carousel-stage");
  if (!stage) return;

  const cards = Array.from(stage.querySelectorAll(".carousel-card"));
  const count = cards.length;
  if (count === 0) return;

  const AUTOPLAY_SPEED = 0.06; // degrees per frame
  const DRAG_SENSITIVITY = 0.3;
  const OVAL_DEPTH_RATIO = 0.42; // radiusZ = radiusX * this
  const MIN_SCALE = 0.68;
  const MAX_SCALE = 1.0;
  const MIN_OPACITY = 0.45;
  const MAX_OPACITY = 1.0;
  const MAX_LIFT = 110; // px a back-row card shifts upward vs. the front row

  let stageWidth = stage.getBoundingClientRect().width;
  let radiusX = stageWidth * 0.32;

  let rotation = 0;
  let targetRotation = null; // used to ease prev/next steps
  let dragging = false;
  let startX = 0;
  let startRotation = 0;
  let hoveredIndex = null;

  function recalcRadius() {
    stageWidth = stage.getBoundingClientRect().width;
    radiusX = stageWidth * 0.32;
  }
  window.addEventListener("resize", recalcRadius);

  function render() {
    const radiusZ = radiusX * OVAL_DEPTH_RATIO;
    const step = 360 / count;

    cards.forEach((card, i) => {
      const theta = i * step + rotation;
      const rad = (theta * Math.PI) / 180;
      const x = radiusX * Math.sin(rad);
      const z = radiusZ * Math.cos(rad);
      const depth = (z + radiusZ) / (2 * radiusZ); // 0 = back, 1 = front

      let scale = MIN_SCALE + depth * (MAX_SCALE - MIN_SCALE);
      let opacity = MIN_OPACITY + depth * (MAX_OPACITY - MIN_OPACITY);
      const lift = -MAX_LIFT * (1 - depth);
      let zIndex = Math.round(depth * 1000);

      const isHovered = i === hoveredIndex;
      card.classList.toggle("is-hovered", isHovered);
      if (isHovered) {
        scale = 1.35;
        opacity = 1;
        zIndex = 9999;
      }

      card.style.transform =
        `translate3d(${x.toFixed(2)}px, ${lift.toFixed(2)}px, ${z.toFixed(2)}px) ` +
        `rotateY(${theta.toFixed(2)}deg) scale(${scale.toFixed(3)})`;
      card.style.opacity = opacity.toFixed(3);
      card.style.zIndex = zIndex;
    });
  }

  function tick() {
    if (targetRotation !== null) {
      const diff = targetRotation - rotation;
      if (Math.abs(diff) < 0.05) {
        rotation = targetRotation;
        targetRotation = null;
      } else {
        rotation += diff * 0.18;
      }
    } else if (!dragging && hoveredIndex === null) {
      rotation += AUTOPLAY_SPEED;
    }
    render();
    requestAnimationFrame(tick);
  }

  // Drag to spin
  stage.addEventListener("pointerdown", (e) => {
    dragging = true;
    targetRotation = null;
    startX = e.clientX;
    startRotation = rotation;
    stage.style.cursor = "grabbing";
    stage.setPointerCapture(e.pointerId);
  });

  stage.addEventListener("pointermove", (e) => {
    if (!dragging) return;
    rotation = startRotation + (e.clientX - startX) * DRAG_SENSITIVITY;
  });

  function endDrag() {
    dragging = false;
    stage.style.cursor = "grab";
  }
  stage.addEventListener("pointerup", endDrag);
  stage.addEventListener("pointerleave", endDrag);
  stage.style.cursor = "grab";

  // Hover to pause + enlarge
  cards.forEach((card, i) => {
    card.addEventListener("mouseenter", () => { hoveredIndex = i; });
    card.addEventListener("mouseleave", () => {
      if (hoveredIndex === i) hoveredIndex = null;
    });
  });

  // Prev / next buttons step exactly one card's angle
  const step = 360 / count;
  const prevBtn = document.getElementById("carousel-prev");
  const nextBtn = document.getElementById("carousel-next");
  const base = () => (targetRotation !== null ? targetRotation : rotation);
  if (prevBtn) prevBtn.addEventListener("click", () => { targetRotation = base() - step; });
  if (nextBtn) nextBtn.addEventListener("click", () => { targetRotation = base() + step; });

  requestAnimationFrame(tick);
})();
