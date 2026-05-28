from enum import Enum, auto


class Phase(Enum):
    WORK = "work"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


class State(Enum):
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()


class FocusService:
    def __init__(self):
        self._state = State.IDLE
        self._phase = Phase.WORK
        self._cycle = 0
        self._session_elapsed = 0
        self._phase_elapsed = 0
        self._deep_focus = False
        self._session_id: str | None = None
        self._category = "umum"

        self._work_s = 25 * 60
        self._short_break_s = 5 * 60
        self._long_break_s = 15 * 60
        self._cycles_before_long = 4

        self.interruptions = 0
        self.distraction_count = 0
        self.mood_before: int | None = None
        self.mood_after: int | None = None
        self.productivity: int | None = None
        self.note = ""

    @property
    def state(self) -> State:
        return self._state

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def cycle(self) -> int:
        return self._cycle

    @property
    def deep_focus(self) -> bool:
        return self._deep_focus

    @property
    def session_id(self) -> str | None:
        return self._session_id

    @property
    def session_elapsed(self) -> int:
        return self._session_elapsed

    @property
    def phase_elapsed(self) -> int:
        return self._phase_elapsed

    @property
    def is_active(self) -> bool:
        return self._state != State.IDLE

    @property
    def phase_length(self) -> int:
        if self._phase == Phase.WORK:
            return self._work_s
        elif self._phase == Phase.LONG_BREAK:
            return self._long_break_s
        return self._short_break_s

    @property
    def remaining(self) -> int:
        return max(0, self.phase_length - self._phase_elapsed)

    def configure(self, work_m: int, short_break_m: int, long_break_m: int, cycles_before_long: int):
        self._work_s = work_m * 60
        self._short_break_s = short_break_m * 60
        self._long_break_s = long_break_m * 60
        self._cycles_before_long = cycles_before_long

    def start(self, category: str = "umum", deep_focus: bool = False):
        from core.repositories.session_repo import start_session

        self._state = State.RUNNING
        self._phase = Phase.WORK
        self._cycle = 0
        self._session_elapsed = 0
        self._phase_elapsed = 0
        self._deep_focus = deep_focus
        self._category = category
        self.interruptions = 0
        self.distraction_count = 0
        self.mood_before = None
        self.mood_after = None
        self.productivity = None
        self.note = ""

        self._session_id = start_session(
            phase=self._phase.value,
            planned_s=self._work_s,
            category=category,
        )

    def pause(self):
        if self._state == State.RUNNING and not self._deep_focus:
            self._state = State.PAUSED

    def resume(self):
        if self._state == State.PAUSED:
            self._state = State.RUNNING

    def stop(self) -> dict:
        from core.repositories.session_repo import end_session

        was_active = self._state != State.IDLE
        sid = self._session_id
        duration = self._session_elapsed

        self._state = State.IDLE
        self._session_id = None

        result = {
            "session_id": sid,
            "duration_s": duration,
            "cycle": self._cycle,
            "was_active": was_active,
        }
        return result

    def tick(self) -> dict | None:
        """Called every second. Returns phase change info if phase ended, else None."""
        if self._state != State.RUNNING:
            return None

        self._session_elapsed += 1
        self._phase_elapsed += 1

        if self._phase_elapsed >= self.phase_length:
            return self._advance_phase()
        return None

    def _advance_phase(self) -> dict:
        old_phase = self._phase
        self._phase_elapsed = 0

        import core.repositories.settings_repo as srepo
        auto_start_break = srepo.get_setting("auto_start_break", "1") == "1"
        auto_start_work = srepo.get_setting("auto_start_work", "0") == "1"

        if self._phase == Phase.WORK:
            self._cycle += 1
            if self._cycle % self._cycles_before_long == 0:
                self._phase = Phase.LONG_BREAK
            else:
                self._phase = Phase.SHORT_BREAK
            if not auto_start_break:
                self._state = State.PAUSED
        else:
            self._phase = Phase.WORK
            if not auto_start_work:
                self._state = State.PAUSED

        return {
            "from": old_phase.value,
            "to": self._phase.value,
            "cycle": self._cycle,
            "auto_paused": self._state == State.PAUSED,
        }

    def skip_phase(self) -> dict:
        return self._advance_phase()

    def set_deep_focus(self, enabled: bool):
        self._deep_focus = enabled
