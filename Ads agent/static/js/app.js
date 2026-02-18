/* ═══════════════════════════════════════════════════════════════
   AdGenius AI — Frontend Application Logic
   ═══════════════════════════════════════════════════════════════ */

// ── State ──
let currentBrief = null;
let currentResult = null;
let selectedTone = "professional";

// ── Init ──
document.addEventListener("DOMContentLoaded", () => {
    initToneButtons();
    initForm();
    initScrollReveal();
    initChatEnter();
});

// ── Tone Selector ──
function initToneButtons() {
    document.querySelectorAll(".tone-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            document.querySelectorAll(".tone-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedTone = btn.dataset.tone;
        });
    });
}

// ── Form Submit ──
function initForm() {
    document.getElementById("briefForm").addEventListener("submit", async (e) => {
        e.preventDefault();
        await runGeneration();
    });
}

async function runGeneration() {
    const productName = document.getElementById("productName").value.trim();
    const description = document.getElementById("description").value.trim();
    const audience = document.getElementById("audience").value.trim();

    const platforms = Array.from(
        document.querySelectorAll("#platformChecks input:checked")
    ).map(cb => cb.value);

    if (!productName || !description || !audience) return;
    if (platforms.length === 0) {
        alert("Please select at least one platform.");
        return;
    }

    currentBrief = { product_name: productName, description, audience, tone: selectedTone, platforms };

    // Show pipeline, hide results
    setVisible("pipeline", true);
    setVisible("results", false);
    setVisible("platforms", false);
    setVisible("chat", false);

    // Scroll to pipeline
    document.getElementById("pipeline").scrollIntoView({ behavior: "smooth", block: "center" });

    // Disable button
    const btn = document.getElementById("generateBtn");
    const btnText = btn.querySelector(".btn-text");
    const btnLoader = document.getElementById("btnLoader");
    btn.disabled = true;
    btnText.style.display = "none";
    btnLoader.style.display = "inline-flex";

    // Animate pipeline
    await animatePipeline();

    try {
        const response = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(currentBrief)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.error || "Generation failed");
        }

        currentResult = await response.json();
        renderResults(currentResult);

    } catch (err) {
        console.error("Generation error:", err);
        alert(`Error: ${err.message}`);
        resetPipeline();
    } finally {
        btn.disabled = false;
        btnText.style.display = "inline";
        btnLoader.style.display = "none";
    }
}

// ── Pipeline Animation ──
async function animatePipeline() {
    const agents = ["creative", "design", "variation", "platform"];
    resetPipeline();

    for (const agentKey of agents) {
        const el = document.getElementById(`agent-${agentKey}`);
        el.classList.add("active");
        el.querySelector(".agent-status-icon").textContent = "⚙️";
        await sleep(700);
    }
}

function resetPipeline() {
    ["creative", "design", "variation", "platform"].forEach(key => {
        const el = document.getElementById(`agent-${key}`);
        el.classList.remove("active", "done");
        el.querySelector(".agent-status-icon").textContent = "⏳";
    });
}

function completePipeline() {
    ["creative", "design", "variation", "platform"].forEach(key => {
        const el = document.getElementById(`agent-${key}`);
        el.classList.remove("active");
        el.classList.add("done");
        el.querySelector(".agent-status-icon").textContent = "✅";
    });
}

// ── Render Results ──
function renderResults(data) {
    completePipeline();

    // Copy
    document.getElementById("copyHeadline").textContent = data.copy.headline;
    document.getElementById("copyBody").textContent = data.copy.body;
    document.getElementById("copyCta").textContent = data.copy.cta;

    // Images
    const imageGrid = document.getElementById("imageGrid");
    imageGrid.innerHTML = "";
    const productName = data.brief?.product_name || "ad-visual";
    data.images.forEach((img, i) => {
        const card = document.createElement("div");
        card.className = "image-card";
        const filename = `${productName.replace(/\s+/g, "-").toLowerCase()}-${i + 1}.jpg`;
        card.innerHTML = `
      <img src="${img.url}" alt="Ad visual ${i + 1}" loading="lazy" />
      <div class="image-overlay">
        <button class="download-btn" onclick="downloadImage('${img.url}', '${filename}')" title="Download image">
          ⬇ Download
        </button>
      </div>
    `;
        imageGrid.appendChild(card);
    });

    // Variations
    renderVariations(data.variations);

    // Platforms
    renderPlatforms(data.platforms);

    // Show sections
    setVisible("results", true);
    setVisible("platforms", true);
    setVisible("chat", true);

    // Scroll to results
    setTimeout(() => {
        document.getElementById("results").scrollIntoView({ behavior: "smooth", block: "start" });
    }, 300);
}

// ── Variations ──
function renderVariations(variations) {
    const tabsEl = document.getElementById("variationTabs");
    const contentEl = document.getElementById("variationContent");
    tabsEl.innerHTML = "";
    contentEl.innerHTML = "";

    variations.forEach((v, i) => {
        // Tab
        const tab = document.createElement("button");
        tab.className = `var-tab${i === 0 ? " active" : ""}`;
        tab.textContent = `${v.performance_hint.icon} ${capitalize(v.tone)}${v.is_primary ? " ★" : ""}`;
        tab.onclick = () => switchVariation(i);
        tabsEl.appendChild(tab);

        // Content
        const card = document.createElement("div");
        card.className = `variation-card${i === 0 ? " active" : ""}`;
        card.id = `var-card-${i}`;
        card.innerHTML = `
      <div class="var-copy">
        <div class="copy-field">
          <div class="copy-label">Headline</div>
          <div class="copy-value">${escHtml(v.headline)}</div>
        </div>
        <div class="copy-field">
          <div class="copy-label">Body Copy</div>
          <div class="copy-value">${escHtml(v.body)}</div>
        </div>
        <div class="copy-field">
          <div class="copy-label">Call to Action</div>
          <div class="copy-value cta-value">${escHtml(v.cta)}</div>
        </div>
      </div>
      <div class="var-perf">
        <div class="perf-title">📊 Performance Insights</div>
        <div class="perf-row"><span class="perf-key">Best For</span><span class="perf-val">${v.performance_hint.best_for}</span></div>
        <div class="perf-row"><span class="perf-key">Avg. CTR</span><span class="perf-val">${v.performance_hint.avg_ctr}</span></div>
        <div class="perf-row"><span class="perf-key">Conversion</span><span class="perf-val">${v.performance_hint.conversion}</span></div>
      </div>
    `;
        contentEl.appendChild(card);
    });
}

function switchVariation(idx) {
    document.querySelectorAll(".var-tab").forEach((t, i) => t.classList.toggle("active", i === idx));
    document.querySelectorAll(".variation-card").forEach((c, i) => c.classList.toggle("active", i === idx));
}

// ── Platforms ──
function renderPlatforms(platforms) {
    const tabsBar = document.getElementById("platformTabsBar");
    const previewArea = document.getElementById("platformPreviewArea");
    tabsBar.innerHTML = "";
    previewArea.innerHTML = "";

    const keys = Object.keys(platforms);
    keys.forEach((key, i) => {
        const p = platforms[key];

        // Tab
        const tab = document.createElement("button");
        tab.className = `plat-tab${i === 0 ? " active" : ""}`;
        tab.innerHTML = `${p.icon} ${p.name}`;
        tab.onclick = () => switchPlatform(i);
        tabsBar.appendChild(tab);

        // Preview
        const preview = document.createElement("div");
        preview.className = `plat-preview${i === 0 ? " active" : ""}`;
        const formats = p.formats.map(f =>
            `<span class="format-chip">${f.name} (${f.ratio})</span>`
        ).join("");

        const imgSrc = p.primary_image || "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=600&q=80";

        preview.innerHTML = `
      <div class="plat-info glass-card">
        <div class="plat-name-row">
          <span class="plat-icon-big">${p.icon}</span>
          <div>
            <div class="plat-name">${p.name}</div>
            <div class="plat-reach">${p.audience_reach}</div>
          </div>
        </div>
        <div class="plat-formats">
          <div class="plat-formats-title">Ad Formats</div>
          ${formats}
        </div>
        <div class="plat-tip">💡 ${p.tips}</div>
      </div>
      <div class="plat-mockup glass-card">
        <div class="mockup-label">${p.primary_format.name} Preview (${p.primary_format.ratio})</div>
        <div class="mockup-frame">
          <img class="mockup-img" src="${imgSrc}" alt="${p.name} ad preview" loading="lazy"
            style="max-height:220px;" />
          <div class="mockup-copy">
            <div class="mockup-headline">${escHtml(p.adapted_copy.headline)}</div>
            <div class="mockup-body">${escHtml(p.adapted_copy.body)}</div>
            <div class="mockup-cta">${escHtml(p.adapted_copy.cta)}</div>
          </div>
        </div>
      </div>
    `;
        previewArea.appendChild(preview);
    });
}

function switchPlatform(idx) {
    document.querySelectorAll(".plat-tab").forEach((t, i) => t.classList.toggle("active", i === idx));
    document.querySelectorAll(".plat-preview").forEach((p, i) => p.classList.toggle("active", i === idx));
}

// ── Chat Refinement ──
function initChatEnter() {
    document.getElementById("chatInput").addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendRefinement();
        }
    });
}

function setChat(text) {
    document.getElementById("chatInput").value = text;
    document.getElementById("chatInput").focus();
}

async function sendRefinement() {
    const input = document.getElementById("chatInput");
    const message = input.value.trim();
    if (!message || !currentBrief) return;

    input.value = "";
    addChatMessage(message, "user");

    // Typing indicator
    const typingId = addTypingIndicator();

    try {
        const response = await fetch("/api/refine", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                brief: currentBrief,
                current_copy: currentResult?.copy || {}
            })
        });

        const data = await response.json();
        removeTypingIndicator(typingId);

        if (data.copy) {
            // Update copy display
            document.getElementById("copyHeadline").textContent = data.copy.headline;
            document.getElementById("copyBody").textContent = data.copy.body;
            document.getElementById("copyCta").textContent = data.copy.cta;

            // Update variations
            if (data.variations) renderVariations(data.variations);

            // Update stored result
            if (currentResult) {
                currentResult.copy = data.copy;
                currentResult.variations = data.variations;
            }

            addChatMessage(data.message, "agent");
        }
    } catch (err) {
        removeTypingIndicator(typingId);
        addChatMessage("Sorry, I had trouble processing that. Please try again.", "agent");
    }
}

function addChatMessage(text, role) {
    const msgs = document.getElementById("chatMessages");
    const div = document.createElement("div");
    div.className = `chat-msg ${role === "agent" ? "agent-msg" : "user-msg"}`;
    div.innerHTML = `
    <div class="msg-avatar">${role === "agent" ? "⚡" : "👤"}</div>
    <div class="msg-bubble">${escHtml(text)}</div>
  `;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return div;
}

function addTypingIndicator() {
    const id = "typing-" + Date.now();
    const msgs = document.getElementById("chatMessages");
    const div = document.createElement("div");
    div.className = "chat-msg agent-msg";
    div.id = id;
    div.innerHTML = `
    <div class="msg-avatar">⚡</div>
    <div class="msg-bubble" style="color:var(--text-muted)">✍️ Refining your creatives...</div>
  `;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// ── Scroll Reveal ──
function initScrollReveal() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(e => { if (e.isIntersecting) e.target.classList.add("visible"); });
    }, { threshold: 0.1 });

    document.querySelectorAll(".glass-card, .pipeline-agent").forEach(el => {
        el.classList.add("reveal");
        observer.observe(el);
    });
}

// ── Helpers ──
function setVisible(id, visible) {
    const el = document.getElementById(id);
    if (el) el.style.display = visible ? "block" : "none";
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function escHtml(str) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(str || ""));
    return div.innerHTML;
}

// ── Image Download ──
async function downloadImage(url, filename) {
    try {
        // Use backend proxy to avoid cross-origin download restrictions
        const proxyUrl = `/api/download-image?url=${encodeURIComponent(url)}&filename=${encodeURIComponent(filename)}`;
        const a = document.createElement("a");
        a.href = proxyUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    } catch (err) {
        console.error("Download failed:", err);
        // Fallback: open image in new tab
        window.open(url, "_blank");
    }
}
