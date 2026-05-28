# Browser Extension

Dokumentasi teknis browser extension AntiDistract (Chrome/Edge, Manifest V3).

---

## Overview

Extension bertindak sebagai agent pemblokiran di browser. Terhubung ke aplikasi desktop via WebSocket untuk menerima state fokus dan blocklist secara real-time.

### Browser yang Didukung

| Browser | Versi Minimal | Manifest |
|---------|--------------|----------|
| Google Chrome | 110+ | V3 |
| Microsoft Edge | 110+ | V3 |
| Brave | 1.50+ | V3 |
| Opera | 100+ | V3 |
| Vivaldi | 6.0+ | V3 |

---

## Arsitektur Extension

```
extension/
├── manifest.json              # MV3 manifest
├── package.json               # Build tools (opsional)
├── vite.config.js             # Vite config (opsional)
└── src/
    ├── background.js          # Service Worker
    ├── popup/
    │   ├── popup.html         # Popup UI (340px)
    │   ├── popup.js           # Popup logic
    │   └── popup.css          # Popup styles (dark theme)
    ├── blocked/
    │   ├── blocked.html       # Blocked page overlay
    │   ├── blocked.js         # Blocked page logic
    │   └── blocked.css        # Blocked page styles
    └── utils/
        ├── ws-client.js       # WebSocket client helper
        └── storage.js         # chrome.storage wrapper
```

---

## Komponen

### 1. Service Worker (`background.js`)

Entry point extension. Berjalan di background, tidak punya akses DOM.

**Responsibilities**:
- Menghubungkan WebSocket ke `ws://localhost:8765`
- Menerima `focus_state` dan `blocklist_update` dari app
- Mengintersep navigasi via `chrome.webNavigation.onBeforeNavigate`
- Memblokir URL yang match dengan blocklist
- Mengupdate badge icon dengan timer
- Melaporkan tab yang diblokir ke app

**Lifecycle**:
```
Install → Activate → Connect WS → Listen Messages → Handle Navigation
                                                      │
                                              onBeforeNavigate
                                                      │
                                              Check URL vs blocklist
                                                      │
                                              Blocked? → Redirect to blocked.html
                                              Allowed? → Allow navigation
```

**Blocking logic**:
```javascript
chrome.webNavigation.onBeforeNavigate.addListener((details) => {
  const hostname = new URL(details.url).hostname.replace('www.', '');
  const blocked = state.blocklist.some(domain =>
    hostname === domain || hostname.endsWith('.' + domain)
  );
  if (blocked && state.active) {
    // Redirect ke blocked page
    chrome.tabs.update(details.tabId, {
      url: chrome.runtime.getURL('src/blocked/blocked.html') +
           '?url=' + encodeURIComponent(details.url) +
           '&hostname=' + encodeURIComponent(hostname)
    });
    // Kirim event ke app via WebSocket
    ws.send(JSON.stringify({
      type: 'tab_blocked',
      url: details.url,
      hostname: hostname,
    }));
  }
});
```

**Badge update**:
```javascript
// Update badge text setiap detik saat sesi aktif
// Tampilkan menit tersisa di icon extension
chrome.action.setBadgeText({ text: '25' });
chrome.action.setBadgeBackgroundColor({ color: '#6c63ff' });
```

### 2. Popup UI (`popup/`)

Popup 340px yang muncul saat user klik icon extension.

**Sections**:
- **Status indicator**: Pulsing dot (hijau = connected, merah = disconnected)
- **Timer display**: Menit:detik tersisa (real-time dari WebSocket)
- **Phase label**: "Kerja" / "Istirahat"
- **Cycle**: Siklus ke berapa
- **Blocklist status**: Jumlah domain yang diblokir
- **Quick actions**:
  - "Pause Blocking 5 min" button
  - "Open Dashboard" button

**Real-time update**:
Pop-up menerima state dari background melalui `chrome.runtime.sendMessage`:
```javascript
// background.js → popup.js
chrome.runtime.sendMessage({
  type: 'focus_state_update',
  active: true,
  phase: 'work',
  remaining_s: 1200,
  cycle: 3,
});
```

### 3. Blocked Page (`blocked/`)

Halaman yang ditampilkan saat user mencoba mengakses domain yang diblokir.

**Layout**:
```
┌──────────────────────────────────────────────┐
│                                              │
│           🛡️ (animated float)                │
│                                              │
│         "Fokus Sedang Berjalan"              │
│                                              │
│     "youtube.com diblokir selama sesi"       │
│                                              │
│   ┌─────────────────────────────────────┐    │
│   │  "Disiplin adalah jembatan antara    │    │
│   │   tujuan dan pencapaian."           │    │
│   │            — Jim Rohn               │    │
│   └─────────────────────────────────────┘    │
│                                              │
│         [Kembali Bekerja]                    │
│                                              │
│     Blokir berakhir dalam: 15:00             │
│                                              │
└──────────────────────────────────────────────┘
```

**Features**:
- Background gradient animasi (berputar perlahan)
- Ikon animasi melayang (CSS keyframes)
- Kutipan motivasi rotasi setiap 8 detik (array 20+ quotes)
- Countdown timer real-time (dari URL parameter atau state)
- Tombol "Kembali Bekerja" — menutup tab via `chrome.tabs.remove()`

**URL Parameters**:
```
chrome-extension://xxx/src/blocked/blocked.html?url=https://youtube.com/watch?v=abc&hostname=youtube.com
```

Quotes diambil dari array terkurasi (Jim Rohn, Cal Newport, James Clear, dll.):
```javascript
const QUOTES = [
  { text: "Disiplin adalah jembatan antara tujuan dan pencapaian.", author: "Jim Rohn" },
  { text: "Fokus adalah kunci dari segala produktivitas.", author: "Cal Newport" },
  { text: "You do not rise to the level of your goals. You fall to the level of your systems.", author: "James Clear" },
  // ... 17+ more
];
```

### 4. WebSocket Client (`utils/ws-client.js`)

Wrapper untuk koneksi WebSocket dengan auto-reconnect.

```javascript
class WSClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.handlers = {};
    this.reconnectDelay = 1000;
    this.maxReconnectDelay = 30000;
  }

  connect() { /* connect + auto-reconnect dengan exponential backoff */ }
  send(data) { /* kirim JSON */ }
  on(event, callback) { /* register handler */ }
  off(event) { /* unregister handler */ }
  close() { /* disconnect */ }
}
```

**Reconnect strategy**: Exponential backoff (1s → 2s → 4s → 8s → 16s → cap 30s).

### 5. Storage Helper (`utils/storage.js`)

Wrapper untuk `chrome.storage.local`:

```javascript
// Set
await storage.set({ focusActive: true, blocklist: [...] });

// Get
const { focusActive } = await storage.get('focusActive');

// Subscribe to changes
storage.onChanged((changes) => {
  if (changes.focusActive) {
    updateUI(changes.focusActive.newValue);
  }
});
```

---

## Permission Model

| Permission | Purpose | Justification |
|------------|---------|---------------|
| `tabs` | Redirect blocked tabs | Required untuk update tab ke blocked page |
| `webNavigation` | Intercept before navigation | Blocking terjadi sebelum halaman dimuat |
| `storage` | Persist state | Blocklist dan config antar session |
| `notifications` | Desktop notifications | Alert saat tab diblokir (opsional) |
| `alarms` | Scheduled checks | Timer untuk schedule-based blocking |
| `<all_urls>` | Block any website | Diperlukan untuk intersep semua domain |

---

## Keamanan

### Data Flow

```
Desktop App ←── WebSocket (localhost only) ──→ Service Worker
                                                    │
                                              chrome.storage.local
                                                    │
                                              Popup UI (read-only)
```

- WebSocket hanya menerima koneksi dari `localhost:8765` — tidak bisa diakses dari jaringan eksternal
- Tidak ada data user yang dikirim ke internet
- Blocklist disimpan di `chrome.storage.local` — tidak tersinkronisasi ke Google account
- Service worker tidak punya akses ke DOM halaman (isolated context)

### Manifest V3 Compliance

Extension menggunakan Manifest V3:
- Service worker (bukan persistent background page) — lebih hemat resource
- `chrome.webNavigation` API (bukan blocking webRequest)
- Tidak ada remote code execution
- Tidak ada eval() atau inline script

---

## Development

### Local Development

1. Clone repository
2. Buka `chrome://extensions`
3. Enable Developer mode
4. Load unpacked → pilih folder `extension/`
5. Setiap perubahan: klik "Reload" pada extension card

### Debugging

**Service Worker Console**:
1. Buka `chrome://extensions`
2. Cari AntiDistract → klik "Service Worker" link
3. Console akan muncul — lihat log WebSocket dan blocking events

**Popup Debugging**:
1. Klik kanan icon extension
2. Pilih "Inspect Popup"
3. DevTools akan terbuka untuk popup context

**Blocked Page Debugging**:
1. Buka blocked page URL secara manual
2. Klik kanan → Inspect

### Testing Koneksi

Cek apakah extension terhubung:

```javascript
// Di service worker console
// Status WebSocket connection
console.log(ws.readyState); // 1 = OPEN, 3 = CLOSED

// Cek state tersimpan
chrome.storage.local.get(null, console.log);
```

---

## WebSocket Protocol Reference

Semua pesan dalam format JSON.

### App → Extension

| Type | Payload | Trigger |
|------|---------|---------|
| `focus_state` | `active, phase, remaining_s, cycle, deep_focus, blocklist, categories_blocked` | Setiap tick timer |
| `blocklist_update` | `blocklist, categories` | User ubah blocklist di settings |

### Extension → App

| Type | Payload | Trigger |
|------|---------|---------|
| `tab_blocked` | `url, hostname, category` | Tab mencoba akses domain terblokir |
| `request_pause` | `duration_m` | User klik "Pause 5 min" di popup |
| `ping` | — | Keep-alive setiap 30 detik |

---

[Kembali ke README](../README.md)
