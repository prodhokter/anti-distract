import datetime
from dataclasses import dataclass, field
from enum import Enum


class BreakType(Enum):
    EYE_REST = "eye_rest"
    STRETCH = "stretch"
    HYDRATION = "hydration"


@dataclass
class BreakConfig:
    break_type: BreakType
    label: str
    emoji: str
    interval_minutes: int
    message: str
    enabled: bool = True


DEFAULT_BREAKS = [
    BreakConfig(BreakType.EYE_REST, "Istirahat Mata", "👁", 20,
                "Sudah 20 menit. Alihkan pandangan ke objek sejauh 6 meter selama 20 detik (20-20-20 rule)."),
    BreakConfig(BreakType.STRETCH, "Peregangan", "🧘", 45,
                "Sudah 45 menit. Berdiri, lakukan peregangan ringan selama 1-2 menit."),
    BreakConfig(BreakType.HYDRATION, "Hidrasi", "💧", 90,
                "Sudah 90 menit. Minum air! Target: 8 gelas sehari."),
]


class BreakReminder:
    def __init__(self):
        self._configs = DEFAULT_BREAKS
        self._last_triggered: dict[str, float] = {}
        self._session_start_time = 0.0

    def configure(self, breaks: list[BreakConfig]):
        self._configs = breaks

    def get_configs(self) -> list[BreakConfig]:
        return self._configs

    def set_enabled(self, break_type: BreakType, enabled: bool):
        for c in self._configs:
            if c.break_type == break_type:
                c.enabled = enabled

    def set_interval(self, break_type: BreakType, minutes: int):
        for c in self._configs:
            if c.break_type == break_type:
                c.interval_minutes = minutes

    def on_session_start(self):
        import time
        self._session_start_time = time.time()

    def check(self) -> list[BreakConfig]:
        import time
        elapsed = (time.time() - self._session_start_time) / 60.0
        due = []

        for cfg in self._configs:
            if not cfg.enabled:
                continue

            key = cfg.break_type.value
            last = self._last_triggered.get(key, 0)
            interval = cfg.interval_minutes

            trigger_count = int(elapsed / interval)
            last_count = int(last / interval) if interval else 0

            if trigger_count > last_count:
                self._last_triggered[key] = elapsed
                due.append(cfg)

        return due

    def reset(self):
        self._last_triggered.clear()
        self._session_start_time = 0.0


class ProductivityScorer:
    def __init__(self):
        pass

    def calculate_daily_score(self,
                              focus_minutes: int = 0,
                              goal_minutes: int = 120,
                              distractions: int = 0,
                              habits_completed: int = 0,
                              habits_total: int = 0,
                              intention_completed: bool = False,
                              mood_logged: bool = False) -> dict:
        # Focus score: 0-50 points
        focus_ratio = min(1.0, focus_minutes / goal_minutes) if goal_minutes else 0
        focus_score = int(focus_ratio * 50)

        # Distraction score: 0-25 points (fewer distractions = higher)
        if distractions == 0:
            distract_score = 25
        elif distractions <= 3:
            distract_score = 20
        elif distractions <= 6:
            distract_score = 15
        elif distractions <= 10:
            distract_score = 10
        else:
            distract_score = max(0, 25 - distractions)

        # Habits score: 0-15 points
        habit_ratio = (habits_completed / habits_total) if habits_total else 0
        habit_score = int(habit_ratio * 15)

        # Intention: 0-5 points
        intention_score = 5 if intention_completed else 0

        # Mood: 0-5 points
        mood_score = 5 if mood_logged else 0

        total = focus_score + distract_score + habit_score + intention_score + mood_score

        grade = "A" if total >= 90 else "B" if total >= 75 else "C" if total >= 55 else "D" if total >= 35 else "E"

        breakdown = {
            "focus": {"score": focus_score, "max": 50, "label": "Waktu Fokus"},
            "distraction": {"score": distract_score, "max": 25, "label": "Minim Distraksi"},
            "habits": {"score": habit_score, "max": 15, "label": "Kebiasaan"},
            "intention": {"score": intention_score, "max": 5, "label": "Intensi Harian"},
            "mood": {"score": mood_score, "max": 5, "label": "Refleksi Mood"},
        }

        return {"total": total, "grade": grade, "breakdown": breakdown}
