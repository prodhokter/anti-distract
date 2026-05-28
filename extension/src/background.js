import { connect, send, on, isConnected } from "./utils/ws-client.js";
import { loadState, saveState } from "./utils/storage.js";

const BLOCKED_PAGE = chrome.runtime.getURL("src/blocked/blocked.html");

let state = {
  focusActive: false, blocklist: [], categories: [],
  deepFocus: false, sessionRemaining: 0, sessionPhase: "",
  // Today stats
  todayFocusMin: 0, todayBlocked: 0, dailyGoal: 120,
};

// Load persisted state
loadState().then(s => {
  state = { ...state, ...s };
  connect();
  setupContextMenu();
});

chrome.runtime.onStartup.addListener(() => {
  loadState().then(s => {
    state = { ...state, ...s };
    connect();
    setupContextMenu();
  });
});

// ── WS message handling ──

on("message", (msg) => {
  if (msg.type === "focus_state") {
    state.focusActive = msg.active;
    state.blocklist = msg.blocklist || [];
    state.categories = msg.categories_blocked || [];
    state.deepFocus = msg.deep_focus || false;
    state.sessionRemaining = msg.remaining_s || 0;
    state.sessionPhase = msg.phase || "";
    state.dailyGoal = msg.daily_goal || 120;
    saveState(state);
    updateBadge();
    updateContextMenu();
    notifyPopup(msg);
  } else if (msg.type === "blocklist_update") {
    state.blocklist = msg.blocklist || [];
    state.categories = msg.categories || [];
    saveState(state);
    updateContextMenu();
    notifyPopup({ type: "state", ...state });
  }
});

// ── Popup communication ──

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === "getState") {
    sendResponse({
      ...state,
      connected: isConnected(),
      todayFocusMin: state.todayFocusMin,
      todayBlocked: state.todayBlocked,
    });
  } else if (msg.type === "ping") {
    sendResponse({ connected: isConnected() });
  } else if (msg.type === "requestPause") {
    send({ type: "pause_request", duration_m: msg.duration_m || 5 });
    sendResponse({ ok: true });
  } else if (msg.type === "requestStart") {
    send({ type: "start_request", category: msg.category || "umum", deep_focus: msg.deep_focus || false });
    sendResponse({ ok: true });
  } else if (msg.type === "requestStop") {
    send({ type: "stop_request" });
    sendResponse({ ok: true });
  } else if (msg.type === "addBlockDomain") {
    send({ type: "add_block_domain", domain: msg.domain });
    sendResponse({ ok: true });
  }
  return true;
});

// ── Tab blocking ──

function isBlocked(url) {
  if (!state.focusActive || (!state.blocklist.length && !state.categories.length)) return false;
  try {
    const hostname = new URL(url).hostname.replace(/^www\./, "");
    const allDomains = [...state.blocklist];
    const catDomains = getCategoryDomains(state.categories);
    const checkList = [...allDomains, ...catDomains];

    for (const domain of checkList) {
      if (hostname === domain || hostname.endsWith("." + domain)) {
        return domain;
      }
    }
  } catch { /* ignore */ }
  return null;
}

function getCategoryDomains(categories) {
  const map = {
    social_media: ["facebook.com", "twitter.com", "x.com", "instagram.com", "tiktok.com", "reddit.com", "linkedin.com", "snapchat.com", "pinterest.com", "threads.net"],
    entertainment: ["youtube.com", "netflix.com", "disneyplus.com", "hulu.com", "twitch.tv", "vimeo.com", "dailymotion.com", "bilibili.com"],
    gaming: ["steampowered.com", "epicgames.com", "roblox.com", "minecraft.net", "discord.com"],
    news: ["cnn.com", "bbc.com", "nytimes.com", "detik.com", "kompas.com", "tribunnews.com", "liputan6.com", "cnbcindonesia.com", "tempo.co"],
    shopping: ["shopee.co.id", "tokopedia.com", "lazada.co.id", "bukalapak.com", "blibli.com", "amazon.com", "zalora.co.id"],
  };
  const domains = [];
  for (const cat of categories) {
    if (map[cat]) domains.push(...map[cat]);
  }
  return domains;
}

chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId !== 0) return;
  const blocked = isBlocked(details.url);
  if (!blocked) return;

  state.todayBlocked++;
  saveState(state);

  send({ type: "blocked_tab", url: details.url, hostname: new URL(details.url).hostname, category: "unknown" });

  const remainingParam = state.sessionRemaining > 0
    ? `&remaining=${state.sessionRemaining}&ts=${Math.floor(Date.now() / 1000)}`
    : "";
  await chrome.tabs.update(details.tabId, {
    url: `${BLOCKED_PAGE}?site=${encodeURIComponent(details.url)}${remainingParam}`
  });

  try {
    chrome.notifications.create({
      type: "basic",
      iconUrl: "icons/icon48.png",
      title: "Tab Diblokir",
      message: `Akses ke ${new URL(details.url).hostname} diblokir saat Focus Mode.`,
    });
  } catch { /* may not have permission */ }
});

// ── Badge ──

function updateBadge() {
  if (state.focusActive && state.sessionRemaining > 0) {
    const mins = Math.ceil(state.sessionRemaining / 60);
    chrome.action.setBadgeText({ text: `${mins}m` });
    chrome.action.setBadgeBackgroundColor({ color: "#6c63ff" });
  } else if (state.focusActive) {
    chrome.action.setBadgeText({ text: "ON" });
    chrome.action.setBadgeBackgroundColor({ color: "#6c63ff" });
  } else {
    chrome.action.setBadgeText({ text: "" });
  }
}

// ── Keyboard shortcuts ──

chrome.commands.onCommand.addListener((command) => {
  switch (command) {
    case "start-focus":
      send({ type: "start_request", category: "umum", deep_focus: false });
      break;
    case "toggle-pause":
      if (state.focusActive) {
        send({ type: "pause_request", duration_m: 5 });
      } else {
        send({ type: "start_request", category: "umum" });
      }
      break;
    case "toggle-blocking":
      if (state.focusActive) {
        send({ type: "stop_request" });
      } else {
        send({ type: "start_request", category: "umum" });
      }
      break;
  }
});

// ── Context menu ──

function setupContextMenu() {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({
      id: "block-site",
      title: "Blokir situs ini",
      contexts: ["page"],
    });
    chrome.contextMenus.create({
      id: "pause-blocking",
      title: "Jeda blokir 5 menit",
      contexts: ["page"],
    });
    chrome.contextMenus.create({
      id: "separator",
      type: "separator",
      contexts: ["page"],
    });
    chrome.contextMenus.create({
      id: "open-app",
      title: "Buka AntiDistract App",
      contexts: ["page"],
    });
  });
}

function updateContextMenu() {
  const pauseTitle = state.focusActive ? "Jeda blokir 5 menit" : "Mulai Fokus 25 menit";
  chrome.contextMenus.update("pause-blocking", { title: pauseTitle }).catch(() => {});
}

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "block-site" && tab?.url) {
    try {
      const domain = new URL(tab.url).hostname.replace(/^www\./, "");
      send({ type: "add_block_domain", domain });
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icons/icon48.png",
        title: "Situs Diblokir",
        message: `${domain} ditambahkan ke daftar blokir.`,
      });
    } catch { /* ignore */ }
  } else if (info.menuItemId === "pause-blocking") {
    if (state.focusActive) {
      send({ type: "pause_request", duration_m: 5 });
    } else {
      send({ type: "start_request", category: "umum" });
    }
  }
});

function notifyPopup(data) {
  chrome.runtime.sendMessage(data).catch(() => {});
}
