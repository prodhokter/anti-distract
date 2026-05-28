const KEYS = {
  focusActive: "focusActive",
  blocklist: "blocklist",
  categories: "categories_blocked",
  deepFocus: "deep_focus",
  sessionRemaining: "session_remaining_s",
  sessionPhase: "session_phase",
};

export async function loadState() {
  const data = await chrome.storage.local.get(Object.values(KEYS));
  return {
    focusActive: data[KEYS.focusActive] ?? false,
    blocklist: data[KEYS.blocklist] ?? [],
    categories: data[KEYS.categories] ?? [],
    deepFocus: data[KEYS.deepFocus] ?? false,
    sessionRemaining: data[KEYS.sessionRemaining] ?? 0,
    sessionPhase: data[KEYS.sessionPhase] ?? "",
  };
}

export async function saveState(state) {
  await chrome.storage.local.set({
    [KEYS.focusActive]: state.focusActive,
    [KEYS.blocklist]: state.blocklist,
    [KEYS.categories]: state.categories,
    [KEYS.deepFocus]: state.deepFocus,
    [KEYS.sessionRemaining]: state.sessionRemaining,
    [KEYS.sessionPhase]: state.sessionPhase,
  });
}
