const params = new URLSearchParams(location.search);
const site = params.get("site") || "";
const remainingAtBlock = parseInt(params.get("remaining") || "0", 10);

try {
  document.getElementById("site-url").textContent = new URL(site).hostname;
} catch {
  document.getElementById("site-url").textContent = site;
}

const quotes = [
  "Fokus adalah seni menghilangkan yang tidak penting.",
  "Deep work menghasilkan hasil yang langka dan berharga.",
  "Kamu selangkah lebih dekat ke tanaman virtual berikutnya.",
  "Setiap distraksi yang kamu lawan adalah kemenangan kecil.",
  "Orang sukses tidak menghindari distraksi — mereka mendesain lingkungan yang bebas distraksi.",
  "Disiplin adalah memilih apa yang kamu inginkan nanti di atas apa yang kamu inginkan sekarang.",
  "Fokus seperti otot — semakin kamu melatihnya, semakin kuat.",
  "90% kesuksesan datang dari kemampuan untuk fokus dan mengatakan tidak.",
  "Jangan biarkan 5 menit scrolling merusak 50 menit deep work.",
  "Kunci produktivitas bukan manajemen waktu, tapi manajemen perhatian.",
];

const q = quotes[Math.floor(Math.random() * quotes.length)];
const el = document.getElementById("quote");
el.textContent = "“" + q + "”";

// Cycle quotes
let idx = quotes.indexOf(q);
setInterval(() => {
  idx = (idx + 1) % quotes.length;
  el.style.opacity = "0";
  setTimeout(() => {
    el.textContent = "“" + quotes[idx] + "”";
    el.style.opacity = "1";
  }, 300);
}, 8000);

// Countdown — use reference time approach
const blockTimestamp = params.get("ts");
let countdownSecs = 0;

if (remainingAtBlock > 0 && blockTimestamp) {
  const blockedAt = parseInt(blockTimestamp, 10);
  countdownSecs = Math.max(0, remainingAtBlock - Math.floor((Date.now() / 1000) - blockedAt));
} else if (remainingAtBlock > 0) {
  countdownSecs = remainingAtBlock;
}

if (countdownSecs > 0) {
  document.getElementById("timer-section").style.display = "block";
  updateCountdown(countdownSecs);
  const interval = setInterval(() => {
    countdownSecs--;
    if (countdownSecs <= 0) {
      clearInterval(interval);
      document.getElementById("countdown").textContent = "Selesai!";
    } else {
      updateCountdown(countdownSecs);
    }
  }, 1000);
}

function updateCountdown(secs) {
  if (secs <= 0) return;
  const m = Math.floor(secs / 60);
  const s = secs % 60;
  document.getElementById("countdown").textContent =
    `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
}

// Show streak info from storage
chrome.storage?.local?.get(["focusActive"], (data) => {
  if (data?.focusActive) {
    document.getElementById("streak-info").textContent = "Focus Mode aktif — tetap semangat!";
  }
});
