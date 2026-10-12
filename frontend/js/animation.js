export function animateCount(element, targetValue, duration = 600) {
    const startValue = Number(element.textContent) || 0;
    const start = performance.now();

    function tick(now) {
        const progress = Math.min((now - start) / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(startValue + (targetValue - startValue) * eased);

        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(tick);
        }
    }

    requestAnimationFrame(tick);
}

export function animateWidth(element, targetPercent, duration = 600) {
    element.style.transition = "none";
    element.style.width = "0";

    requestAnimationFrame(() => {
        element.style.transition = `width ${duration}ms cubic-bezier(0.4, 0, 0.2, 1)`;
        requestAnimationFrame(() => {
            element.style.width = `${targetPercent}%`;
        });
    });
}

export function staggerReveal(container, selector) {
    const children = container.querySelectorAll(selector);

    children.forEach((child, index) => {
        child.style.animation = "none";
        // Force a reflow so re-assigning the animation below actually restarts
        // it, instead of the browser treating it as a no-op on an unchanged value.
        void child.offsetWidth;
        child.style.animation = "";
        child.style.animationDelay = `${index * 60}ms`;
    });
}

const CONFETTI_COLORS = ["#2563eb", "#0f3381", "#15803d", "#f59e0b", "#ef4444"];

export function celebrate(originElement) {
    const rect = originElement.getBoundingClientRect();
    const originX = rect.left + rect.width / 2;
    const originY = rect.top + rect.height / 2;

    for (let i = 0; i < 24; i++) {
        const piece = document.createElement("div");
        piece.className = "confetti-piece";
        piece.style.left = `${originX}px`;
        piece.style.top = `${originY}px`;
        piece.style.backgroundColor = CONFETTI_COLORS[i % CONFETTI_COLORS.length];

        const angle = Math.random() * Math.PI * 2;
        const distance = 80 + Math.random() * 120;
        piece.style.setProperty("--tx", `${Math.cos(angle) * distance}px`);
        piece.style.setProperty("--ty", `${Math.sin(angle) * distance}px`);
        piece.style.setProperty("--rot", `${Math.random() * 720 - 360}deg`);
        piece.style.animationDelay = `${Math.random() * 80}ms`;

        document.body.appendChild(piece);
        piece.addEventListener("animationend", () => piece.remove());
    }
}

export function rippleOnClick(event) {
    const button = event.currentTarget;

    if (button.disabled) {
        return;
    }

    const rect = button.getBoundingClientRect();
    const ripple = document.createElement("span");
    const size = Math.max(rect.width, rect.height) * 2;

    ripple.className = "button-ripple";
    ripple.style.width = `${size}px`;
    ripple.style.height = `${size}px`;
    ripple.style.left = `${event.clientX - rect.left - size / 2}px`;
    ripple.style.top = `${event.clientY - rect.top - size / 2}px`;

    button.appendChild(ripple);
    ripple.addEventListener("animationend", () => ripple.remove());
}

export function typewriter(element, text, speed = 12) {
    element.textContent = "";
    let index = 0;

    function tick() {
        if (index >= text.length) {
            return;
        }

        // Type in small chunks rather than one character at a time so long
        // cover letters finish revealing in a reasonable, non-tedious time.
        const chunkSize = 3;
        element.textContent += text.slice(index, index + chunkSize);
        index += chunkSize;

        setTimeout(tick, speed);
    }

    tick();
}

export function spotlightFollow(element) {
    element.addEventListener("mousemove", (event) => {
        const rect = element.getBoundingClientRect();
        element.style.setProperty("--spotlight-x", `${event.clientX - rect.left}px`);
        element.style.setProperty("--spotlight-y", `${event.clientY - rect.top}px`);
    });
}
