/*----https://dev.to/iscorekin/how-to-draw-beautiful-connections-with-svg-17ii-----*/
/*----https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector----*/

const canvas = document.getElementById("canvas");
const stage = document.getElementById("stage");
const svg = document.getElementById("connections");
/* =========================================================
   SVG EDGES
========================================================= */

function center(el) {
    const r = el.getBoundingClientRect();
    const c = stage.getBoundingClientRect();

    return {
        x: r.left + r.width / 2 - c.left,
        y: r.top + r.height / 2 - c.top
    };
}

EDGES.forEach(edge => {
    const from = document.querySelector(`[data-id="${edge.from}"]`);
    const to = document.querySelector(`[data-id="${edge.to}"]`);
    if (!from || !to) return;

    const a = center(from);
    const b = center(to);

    const dx = (b.x - a.x) * 0.5;

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute(
        "d",
        `
        M ${a.x} ${a.y}
        C ${a.x + dx} ${a.y},
          ${b.x - dx} ${b.y},
          ${b.x} ${b.y}
        `
    );

    path.setAttribute("stroke", "#444444");
    path.setAttribute("stroke-width", "2");
    path.setAttribute("fill", "none");
    path.setAttribute("marker-end", "url(#arrow)");

    svg.appendChild(path);
});



/* =========================================================
   PAN (DRAG)
========================================================= */

let isPanning = false;
let startX = 0;
let startY = 0;
let panX = 0;
let panY = 0;

canvas.style.cursor = "grab";

canvas.addEventListener("mousedown", e => {
    isPanning = true;
    startX = e.clientX - panX;
    startY = e.clientY - panY;
    canvas.style.cursor = "grabbing";
});

window.addEventListener("mousemove", e => {
    if (!isPanning) return;

    panX = e.clientX - startX;
    panY = e.clientY - startY;

    applyTransform();
});

window.addEventListener("mouseup", () => {
    isPanning = false;
    canvas.style.cursor = "grab";
});

/* =========================================================
   ZOOM
========================================================= */

let scale = 1;
const MIN_ZOOM = 0.3;
const MAX_ZOOM = 2.5;

function applyTransform() {
    stage.style.transform =
        `translate(${panX}px, ${panY}px) scale(${scale})`;
}

canvas.addEventListener("wheel", e => {
    e.preventDefault();

    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    scale = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, scale + delta));

    applyTransform();
}, { passive: false });

/* Buttons */
document.getElementById("zoom-in").onclick = () => {
    scale = Math.min(scale + 0.1, MAX_ZOOM);
    applyTransform();
};

document.getElementById("zoom-out").onclick = () => {
    scale = Math.max(scale - 0.1, MIN_ZOOM);
    applyTransform();
};

document.getElementById("zoom-reset").onclick = () => {
    scale = fitToScreen();
    panX = 0;
    panY = 0;
    applyTransform();
};

/* =========================================================
   FIT TO SCREEN (on load)
========================================================= */

function fitToScreen() {
    const canvasRect = canvas.getBoundingClientRect();
    const stageRect = stage.getBoundingClientRect();

    const scaleX = canvasRect.width / stageRect.width;
    const scaleY = canvasRect.height / stageRect.height;

    return Math.min(scaleX, scaleY, 1);
}

window.addEventListener("load", () => {
    scale = fitToScreen();
    applyTransform();
});

/* =========================================================
   NODE CLICK NAVIGATION
========================================================= */

document.querySelectorAll(".food-node").forEach(node => {
    node.addEventListener("click", e => {
        e.stopPropagation();

        const rawId = node.dataset.id;
        const type = node.dataset.type;
        if (!rawId || !type) return;

        if (type === "animal") {
            window.location.href = `/food-web/${rawId}`;
        } else {
            const mealId = rawId.includes("__")
                ? rawId.split("__")[1]
                : rawId;

            window.location.href = `/meal/${mealId}`;
        }
    });
});
