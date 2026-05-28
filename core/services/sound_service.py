import struct
import wave
import math
import tempfile
import os
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum


class AlarmType(Enum):
    SOFT_CHIME = "soft_chime"
    ALERT = "alert"
    EMERGENCY = "emergency"
    BELL = "bell"
    BUZZER = "buzzer"


@dataclass
class SoundProfile:
    name: str
    alarm_type: AlarmType
    volume: float = 0.7
    repeat_count: int = 3
    repeat_interval_ms: int = 500
    enabled: bool = True


def _generate_sine_wav(filepath: str, frequency: float, duration_s: float,
                       sample_rate: int = 44100, volume: float = 0.8,
                       fade_out: bool = True):
    n_samples = int(sample_rate * duration_s)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            value = volume * math.sin(2 * math.pi * frequency * t)
            if fade_out:
                fade = 1.0 - (i / n_samples)
                value *= fade
            wf.writeframes(struct.pack("<h", int(value * 32767)))


def _generate_dual_tone(filepath: str, freq1: float, freq2: float,
                        duration_s: float, sample_rate: int = 44100,
                        volume: float = 0.7):
    n_samples = int(sample_rate * duration_s)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            f = freq1 if (i // (sample_rate // 4)) % 2 == 0 else freq2
            value = volume * math.sin(2 * math.pi * f * t)
            fade = 1.0 - (i / n_samples)
            value *= fade
            wf.writeframes(struct.pack("<h", int(value * 32767)))


def _generate_emergency(filepath: str, sample_rate: int = 44100, volume: float = 0.85):
    duration_s = 2.5
    n_samples = int(sample_rate * duration_s)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            cycle = int(t * 8) % 2
            freq = 800 if cycle == 0 else 1200
            value = volume * math.sin(2 * math.pi * freq * t)
            attack = min(1.0, t * 20)
            fade = 1.0 - (i / n_samples) if i > n_samples * 0.8 else 1.0
            value *= attack * fade
            wf.writeframes(struct.pack("<h", int(value * 32767)))


def _generate_buzzer(filepath: str, sample_rate: int = 44100, volume: float = 0.9):
    duration_s = 1.5
    n_samples = int(sample_rate * duration_s)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            on = (i // (sample_rate // 10)) % 2
            freq = 440
            value = volume * math.sin(2 * math.pi * freq * t) * on
            value *= 1.0 - (i / n_samples) * 0.3
            wf.writeframes(struct.pack("<h", int(value * 32767)))


def _generate_bell(filepath: str, sample_rate: int = 44100, volume: float = 0.7):
    duration_s = 1.8
    n_samples = int(sample_rate * duration_s)
    with wave.open(filepath, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        for i in range(n_samples):
            t = i / sample_rate
            freq1 = 880 * math.exp(-t * 4)
            freq2 = 1100 * math.exp(-t * 5)
            value = volume * 0.5 * (math.sin(2 * math.pi * freq1 * t) +
                                    math.sin(2 * math.pi * freq2 * t))
            value *= math.exp(-t * 3)
            wf.writeframes(struct.pack("<h", int(value * 32767)))


class SoundAlarm:
    def __init__(self, sounds_dir: Path | None = None):
        from PyQt6.QtMultimedia import QSoundEffect
        from PyQt6.QtCore import QUrl, QTimer

        self._sounds_dir = Path(sounds_dir or Path.home() / ".antidistract" / "sounds")
        self._sounds_dir.mkdir(parents=True, exist_ok=True)
        self._effects: dict[str, QSoundEffect] = {}
        self._master_volume = 0.7
        self._muted = False
        self._continuous_timers: dict[str, QTimer] = {}
        self._continuous_effects: dict[str, QSoundEffect] = {}

        self._profiles: dict[str, SoundProfile] = {
            "away_warning": SoundProfile("Peringatan Menjauh", AlarmType.ALERT, volume=0.6, repeat_count=2),
            "away_critical": SoundProfile("Away Kritis", AlarmType.EMERGENCY, volume=0.85, repeat_count=5, repeat_interval_ms=300),
            "tab_blocked": SoundProfile("Tab Diblokir", AlarmType.BELL, volume=0.5, repeat_count=1),
            "break_reminder": SoundProfile("Istirahat", AlarmType.SOFT_CHIME, volume=0.4, repeat_count=2, repeat_interval_ms=800),
            "focus_start": SoundProfile("Mulai Fokus", AlarmType.BELL, volume=0.5, repeat_count=1),
            "focus_end": SoundProfile("Selesai Fokus", AlarmType.SOFT_CHIME, volume=0.5, repeat_count=1),
            "deep_focus_lock": SoundProfile("Deep Focus", AlarmType.BUZZER, volume=0.75, repeat_count=1),
        }

        self._generate_builtin_sounds()
        self._load_effects()

    def _generate_builtin_sounds(self):
        sounds = {
            "soft_chime": lambda p: _generate_sine_wav(p, 880, 0.6, volume=0.6),
            "alert": lambda p: _generate_dual_tone(p, 600, 800, 1.0, volume=0.7),
            "emergency": _generate_emergency,
            "bell": _generate_bell,
            "buzzer": _generate_buzzer,
        }
        for name, gen_fn in sounds.items():
            path = self._sounds_dir / f"{name}.wav"
            if not path.exists():
                gen_fn(str(path))

    def _load_effects(self):
        from PyQt6.QtMultimedia import QSoundEffect
        from PyQt6.QtCore import QUrl

        for name in ["soft_chime", "alert", "emergency", "bell", "buzzer"]:
            path = self._sounds_dir / f"{name}.wav"
            if path.exists():
                effect = QSoundEffect()
                effect.setSource(QUrl.fromLocalFile(str(path)))
                effect.setVolume(self._master_volume)
                self._effects[name] = effect

    def play(self, profile_key: str):
        if self._muted:
            return

        profile = self._profiles.get(profile_key)
        if not profile or not profile.enabled:
            return

        sound_name = profile.alarm_type.value
        effect = self._effects.get(sound_name)
        if not effect:
            return

        vol = profile.volume * self._master_volume
        effect.setVolume(min(1.0, vol))
        self._play_repeat(effect, profile.repeat_count, profile.repeat_interval_ms)

    def _play_repeat(self, effect, count: int, interval_ms: int):
        from PyQt6.QtCore import QTimer

        if count <= 0:
            return

        remaining = [count]
        effect.play()

        if count > 1:
            timer = QTimer()
            timer.setInterval(interval_ms)

            def replay():
                if remaining[0] > 0:
                    remaining[0] -= 1
                    if remaining[0] > 0:
                        effect.play()
                    else:
                        timer.stop()
                        timer.deleteLater()

            timer.timeout.connect(replay)
            timer.start()

    def play_continuous(self, profile_key: str):
        """Play alarm in infinite loop until stop_all() called. For face away and sleep alerts."""
        if self._muted:
            return

        profile = self._profiles.get(profile_key)
        if not profile or not profile.enabled:
            return

        sound_name = profile.alarm_type.value
        effect = self._effects.get(sound_name)
        if not effect:
            return

        # Don't restart if already playing this profile continuously
        if profile_key in self._continuous_timers:
            return

        vol = profile.volume * self._master_volume
        effect.setVolume(min(1.0, vol))
        effect.play()

        from PyQt6.QtCore import QTimer
        timer = QTimer()
        timer.setInterval(profile.repeat_interval_ms)
        timer.timeout.connect(lambda: effect.play())
        timer.start()

        self._continuous_timers[profile_key] = timer
        self._continuous_effects[profile_key] = effect

    def stop_all(self):
        """Stop all continuously playing alarms and clean up timers."""
        for timer in self._continuous_timers.values():
            timer.stop()
            timer.deleteLater()
        self._continuous_timers.clear()

        for effect in self._continuous_effects.values():
            effect.stop()
        self._continuous_effects.clear()

    def stop_continuous(self, profile_key: str):
        """Stop a specific continuous alarm."""
        timer = self._continuous_timers.pop(profile_key, None)
        if timer:
            timer.stop()
            timer.deleteLater()

        effect = self._continuous_effects.pop(profile_key, None)
        if effect:
            effect.stop()

    def is_continuous_active(self, profile_key: str = "") -> bool:
        """Check if continuous alarm(s) are active. If profile_key given, check specific."""
        if profile_key:
            return profile_key in self._continuous_timers
        return len(self._continuous_timers) > 0

    def set_master_volume(self, vol: float):
        self._master_volume = max(0.0, min(1.0, vol))
        for effect in self._effects.values():
            effect.setVolume(self._master_volume)

    def set_muted(self, muted: bool):
        self._muted = muted

    def master_volume(self) -> float:
        return self._master_volume

    def is_muted(self) -> bool:
        return self._muted

    def get_profiles(self) -> dict:
        return {k: {
            "name": p.name,
            "type": p.alarm_type.value,
            "volume": p.volume,
            "repeat": p.repeat_count,
            "enabled": p.enabled,
        } for k, p in self._profiles.items()}

    def set_profile_volume(self, key: str, vol: float):
        if key in self._profiles:
            self._profiles[key].volume = max(0.0, min(1.0, vol))

    def set_profile_enabled(self, key: str, enabled: bool):
        if key in self._profiles:
            self._profiles[key].enabled = enabled
