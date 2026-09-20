(() => {
    "use strict";

    const canvas = document.getElementById("live-network-topology");
    if (!canvas) return;

    const ctx = canvas.getContext("2d", { alpha: true });
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const sectionMap = [
        { selector: "#home", labels: ["CORE-01", "BGP", "EDGE-02", "UPLINK", "NOC"], accent: [56, 189, 248] },
        { selector: "#about", labels: ["DISCOVERY", "PROFILE", "SKILLS", "LANG", "NOC"], accent: [45, 212, 191] },
        { selector: "#expertise", labels: ["OSPF", "BGP", "MPLS", "VLAN", "NAT"], accent: [34, 211, 238] },
        { selector: "#technology", labels: ["CISCO", "MIKROTIK", "HUAWEI", "LINUX", "SNMP"], accent: [56, 189, 248] },
        { selector: "#experience", labels: ["CORE", "DISTRIBUTION", "ACCESS", "OLT", "NMS"], accent: [20, 184, 166] },
        { selector: "#projects", labels: ["VPN", "MONITOR", "ISP", "DJANGO", "LAB"], accent: [103, 232, 249] },
        { selector: ".certifications-section", labels: ["CCNA", "MTCNA", "LINUX", "ROUTING", "SECURITY"], accent: [45, 212, 191] },
        { selector: "#lessons", labels: ["LAB-01", "DHCP", "NAT", "BRIDGE", "CLI"], accent: [94, 234, 212] },
        { selector: "#contact", labels: ["CONNECT", "SMTP", "LINK-UP", "READY", "HASAN.NET"], accent: [34, 211, 238] }
    ];

    const sections = sectionMap
        .map(item => ({ ...item, element: document.querySelector(item.selector) }))
        .filter(item => item.element);

    const nodeSeeds = [
        [0.07, 0.18], [0.19, 0.34], [0.34, 0.16], [0.49, 0.31],
        [0.64, 0.14], [0.81, 0.28], [0.94, 0.12], [0.12, 0.72],
        [0.28, 0.58], [0.44, 0.76], [0.59, 0.57], [0.74, 0.73],
        [0.90, 0.59], [0.52, 0.91]
    ];
    const edgePairs = [
        [0,1], [0,2], [1,2], [1,8], [2,3], [2,4], [3,4], [3,8],
        [3,10], [4,5], [4,6], [5,6], [5,10], [5,12], [7,8], [7,9],
        [8,9], [8,10], [9,10], [9,13], [10,11], [10,12], [10,13],
        [11,12], [11,13]
    ];

    let width = 0;
    let height = 0;
    let dpr = 1;
    let active = 0;
    let animationFrame = 0;
    let lastTime = 0;
    let mouseX = 0.5;
    let mouseY = 0.5;
    let targetMouseX = 0.5;
    let targetMouseY = 0.5;
    let scrollRatio = 0;
    let particles = [];

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);
        canvas.style.width = width + "px";
        canvas.style.height = height + "px";
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        const particleCount = width < 768 ? 10 : 22;
        particles = Array.from({ length: particleCount }, (_, index) => ({
            edge: index % edgePairs.length,
            progress: (index * 0.137) % 1,
            speed: 0.035 + (index % 5) * 0.009,
            reverse: index % 4 === 0
        }));
    }

    function updateActiveSection() {
        const focusLine = window.innerHeight * 0.48;
        let best = 0;
        let bestDistance = Infinity;

        sections.forEach((section, index) => {
            const rect = section.element.getBoundingClientRect();
            const center = rect.top + rect.height / 2;
            const distance = Math.abs(center - focusLine);
            if (rect.bottom > 0 && rect.top < window.innerHeight && distance < bestDistance) {
                best = index;
                bestDistance = distance;
            }
        });

        active = best;
        const maxScroll = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
        scrollRatio = window.scrollY / maxScroll;
    }

    function nodePosition(seed, index, time) {
        const drift = reduceMotion.matches ? 0 : Math.sin(time * 0.00035 + index * 1.7) * 9;
        const parallaxX = (mouseX - 0.5) * (12 + (index % 3) * 5);
        const parallaxY = (mouseY - 0.5) * (8 + (index % 4) * 3);
        return {
            x: seed[0] * width + drift + parallaxX,
            y: seed[1] * height + Math.cos(time * 0.0003 + index) * (reduceMotion.matches ? 0 : 7) + parallaxY
        };
    }

    function rgba(rgb, alpha) {
        return `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${alpha})`;
    }

    function drawGrid(accent) {
        const spacing = width < 768 ? 74 : 92;
        const offsetX = ((scrollRatio * 130) + (mouseX - 0.5) * 18) % spacing;
        const offsetY = ((scrollRatio * 220) + (mouseY - 0.5) * 12) % spacing;

        ctx.lineWidth = 1;
        ctx.strokeStyle = rgba(accent, 0.045);
        ctx.beginPath();
        for (let x = offsetX; x < width; x += spacing) {
            ctx.moveTo(x, 0);
            ctx.lineTo(x, height);
        }
        for (let y = offsetY; y < height; y += spacing) {
            ctx.moveTo(0, y);
            ctx.lineTo(width, y);
        }
        ctx.stroke();
    }

    function draw(time) {
        const delta = Math.min(50, time - lastTime || 16);
        lastTime = time;
        mouseX += (targetMouseX - mouseX) * 0.035;
        mouseY += (targetMouseY - mouseY) * 0.035;

        ctx.clearRect(0, 0, width, height);
        const config = sections[active] || sectionMap[0];
        const accent = config.accent;
        const nodes = nodeSeeds.map((seed, index) => nodePosition(seed, index, time));

        drawGrid(accent);

        const glow = ctx.createRadialGradient(
            width * (0.25 + active * 0.055),
            height * 0.5,
            0,
            width * 0.5,
            height * 0.5,
            Math.max(width, height) * 0.72
        );
        glow.addColorStop(0, rgba(accent, 0.075));
        glow.addColorStop(0.55, rgba(accent, 0.018));
        glow.addColorStop(1, "rgba(15,23,42,0)");
        ctx.fillStyle = glow;
        ctx.fillRect(0, 0, width, height);

        edgePairs.forEach((pair, index) => {
            const a = nodes[pair[0]];
            const b = nodes[pair[1]];
            const highlighted = index % Math.max(2, 5 - (active % 3)) === 0;

            ctx.beginPath();
            ctx.moveTo(a.x, a.y);
            const curve = (index % 2 ? 1 : -1) * (18 + active * 2);
            const midX = (a.x + b.x) / 2;
            const midY = (a.y + b.y) / 2 + curve;
            ctx.quadraticCurveTo(midX, midY, b.x, b.y);
            ctx.lineWidth = highlighted ? 1.35 : 0.75;
            ctx.strokeStyle = rgba(accent, highlighted ? 0.28 : 0.11);
            ctx.setLineDash(highlighted ? [8, 10] : []);
            ctx.lineDashOffset = reduceMotion.matches ? 0 : -time * 0.018;
            ctx.stroke();
        });
        ctx.setLineDash([]);

        if (!reduceMotion.matches) {
            particles.forEach((packet, index) => {
                packet.progress = (packet.progress + packet.speed * delta / 1000) % 1;
                const t = packet.reverse ? 1 - packet.progress : packet.progress;
                const pair = edgePairs[packet.edge];
                const a = nodes[pair[0]];
                const b = nodes[pair[1]];
                const curve = (packet.edge % 2 ? 1 : -1) * (18 + active * 2);
                const control = { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 + curve };
                const inv = 1 - t;
                const x = inv * inv * a.x + 2 * inv * t * control.x + t * t * b.x;
                const y = inv * inv * a.y + 2 * inv * t * control.y + t * t * b.y;

                ctx.shadowBlur = 12;
                ctx.shadowColor = rgba(accent, 0.9);
                ctx.fillStyle = index % 3 === 0 ? "#5eead4" : "#7dd3fc";
                ctx.beginPath();
                ctx.arc(x, y, index % 4 === 0 ? 2.8 : 2, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.shadowBlur = 0;
        }

        nodes.forEach((node, index) => {
            const major = index % 3 === active % 3;
            const radius = major ? 5.2 : 3.1;
            const pulse = reduceMotion.matches ? 0 : (Math.sin(time * 0.002 + index) + 1) * 0.5;

            ctx.strokeStyle = rgba(accent, major ? 0.62 : 0.28);
            ctx.lineWidth = major ? 1.3 : 0.8;
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius + 6 + pulse * 4, 0, Math.PI * 2);
            ctx.stroke();

            ctx.shadowBlur = major ? 16 : 8;
            ctx.shadowColor = rgba(accent, 0.85);
            ctx.fillStyle = major ? rgba(accent, 0.95) : rgba(accent, 0.58);
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            if (major && width >= 768) {
                const label = config.labels[index % config.labels.length];
                ctx.font = "600 10px Inter, system-ui, sans-serif";
                ctx.letterSpacing = "1px";
                const textWidth = ctx.measureText(label).width;
                const boxX = node.x + 13;
                const boxY = node.y - 13;
                ctx.fillStyle = "rgba(15, 23, 42, 0.78)";
                ctx.strokeStyle = rgba(accent, 0.28);
                ctx.lineWidth = 1;
                ctx.beginPath();
                ctx.roundRect(boxX, boxY, textWidth + 18, 24, 6);
                ctx.fill();
                ctx.stroke();
                ctx.fillStyle = rgba(accent, 0.88);
                ctx.fillText(label, boxX + 9, boxY + 16);
            }
        });

        if (!document.hidden && !reduceMotion.matches) {
            animationFrame = requestAnimationFrame(draw);
        }
    }

    function start() {
        cancelAnimationFrame(animationFrame);
        lastTime = 0;
        animationFrame = requestAnimationFrame(draw);
    }

    window.addEventListener("resize", resize, { passive: true });
    window.addEventListener("scroll", updateActiveSection, { passive: true });
    window.addEventListener("pointermove", event => {
        targetMouseX = event.clientX / Math.max(1, width);
        targetMouseY = event.clientY / Math.max(1, height);
    }, { passive: true });
    document.addEventListener("visibilitychange", () => {
        if (!document.hidden) start();
    });
    reduceMotion.addEventListener?.("change", () => {
        resize();
        draw(performance.now());
        if (!reduceMotion.matches) start();
    });

    resize();
    updateActiveSection();
    if (reduceMotion.matches) {
        draw(performance.now());
    } else {
        start();
    }
})();