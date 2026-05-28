const $ = (id) => document.getElementById(id);

let currentState = {
  focusActive: false, sessionPhase: "", sessionRemaining: 0,
  todayFocusMin: 0, todayBlocked: 0, dailyGoal: 120,
  blocklist: [], categories: [],
};

function setConnected(ok) {
  const dot = $("status-dot");
  dot.className = "status-dot" + (ok ? " connected" : "");
  dot.title = ok ? "Terhubung ke AntiDistract" : "Tidak terhubung";
}

function setFocusState(active, phase, remaining) {
  const badge = $("focus-badge");
  badge.textContent = active ? "ON" : "OFF";
  badge.className = "badge " + (active ? "on" : "off");

  if (active && remaining > 0) {
    const m = Math.floor(remaining / 60);
    const s = remaining % 60;
    $("timer-text").textContent = `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  } else {
    $("timer-text").textContent = active ? "--:--" : "—";
  }

  $("phase-text").textContent = phase === "work"
    ? "Fase: Kerja"
    : phase === "long_break" ? "Fase: Istirahat Panjang"
    : phase ? "Fase: Istirahat" : "";

  const totalPhase = phase === "work" ? currentState.dailyGoal * 60 : 300;
  const pct = remaining > 0 && totalPhase > 0
    ? Math.min(100, Math.round((1 - remaining / totalPhase) * 100))
    : 0;
  $("progress-fill").style.width = active ? pct + "%" : "0%";

  // Enable/disable pause buttons
  const btns = [$("btn-pause-5"), $("btn-pause-15"), $("btn-pause-30")];
  btns.forEach(b => b.disabled = !active);
}

function setStats(todayFocusMin, todayBlocked, dailyGoal) {
  $("stat-focus").textContent = todayFocusMin + "m";
  $("stat-blocked").textContent = String(todayBlocked);
  const pct = dailyGoal > 0 ? Math.min(100, Math.round((todayFocusMin / dailyGoal) * 100)) : 0;
  $("stat-goal").textContent = pct + "%";
  $("goal-text").textContent = todayFocusMin + "/" + dailyGoal + " mnt";
  $("goal-fill").style.width = pct + "%";
}

function setBlocklist(blocklist, categories) {
  const count = (blocklist?.length || 0) + (categories?.length || 0);
  $("block-count").textContent = count > 0 ? `${count} domain/kategori aktif` : "Tidak ada";

  const tags = $("block-tags");
  tags.innerHTML = "";
  if (blocklist) {
    blocklist.slice(0, 8).forEach(d => {
      const span = document.createElement("span");
      span.className = "block-tag";
      span.textContent = d;
      tags.appendChild(span);
    });
  }
  if (blocklist && blocklist.length > 8) {
    const more = document.createElement("span");
    more.className = "block-tag";
    more.textContent = `+${blocklist.length - 8} lagi`;
    tags.appendChild(more);
  }
}

// Load state from background
chrome.runtime.sendMessage({ type: "getState" }, (res) => {
  if (!res) return;
  currentState = res;
  setConnected(res.connected);
  setFocusState(res.focusActive, res.sessionPhase, res.sessionRemaining);
  setStats(res.todayFocusMin || 0, res.todayBlocked || 0, res.dailyGoal || 120);
  setBlocklist(res.blocklist, res.categories);
});

// Listen for updates from background
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "state" || msg.type === "focus_state") {
    const d = msg;
    currentState = { ...currentState, ...d };
    setFocusState(d.focusActive ?? d.active,
                  d.sessionPhase ?? d.phase,
                  d.sessionRemaining ?? d.remaining_s);
    setStats(currentState.todayFocusMin || 0,
             currentState.todayBlocked || 0,
             currentState.dailyGoal || 120);
    setBlocklist(d.blocklist, d.categories ?? d.categories_blocked);
  } else if (msg.type === "connected") {
    setConnected(true);
  } else if (msg.type === "disconnected") {
    setConnected(false);
  }
});

// Pause buttons
function requestPause(mins) {
  chrome.runtime.sendMessage({ type: "requestPause", duration_m: mins });
  const btn = $(`btn-pause-${mins}`);
  const orig = btn.textContent;
  btn.textContent = "...";
  btn.disabled = true;
  setTimeout(() => {
    btn.textContent = orig;
    btn.disabled = !currentState.focusActive;
  }, 2000);
}

$("btn-pause-5").addEventListener("click", () => requestPause(5));
$("btn-pause-15").addEventListener("click", () => requestPause(15));
$("btn-pause-30").addEventListener("click", () => requestPause(30));
