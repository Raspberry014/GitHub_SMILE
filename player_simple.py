# player_simple.py
import sys, os, time, threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --------- Попытка использовать pygame (лучше) ---------
USE_PYGAME = False
try:
    import pygame  # pip install pygame
    pygame.mixer.init()
    USE_PYGAME = True
except Exception:
    pass

# --------- Fallback: winsound для WAV ---------
if not USE_PYGAME and sys.platform == "win32":
    import winsound
    import wave, contextlib

class BackendBase:
    name = "Base"
    can_pause = False
    can_seek = False
    can_volume = False
    length_ms = 0

    def open(self, path): ...
    def play(self): ...
    def pause(self): ...
    def stop(self): ...
    def get_pos_ms(self): return 0
    def set_pos_ms(self, ms): ...
    def set_volume(self, vol): ...

# ---- Backend на pygame (если доступен) ----
class PygameBackend(BackendBase):
    name = "pygame"
    can_pause = True
    can_seek = True   # эмулируем set_pos перезапуском
    can_volume = True

    def __init__(self):
        self.path = None
        self.start_ms = 0     # откуда стартовали (для seek)
        self.started_at = 0   # когда запустили (time.time()*1000)
        self.paused = False
        self.pause_at = 0     # момент паузы (мс)

    def open(self, path):
        self.stop()
        self.path = path
        pygame.mixer.music.load(path)
        # Оценим длину (пытаемся через pygame.Sound для ogg/wav; mp3 может вернуться 0)
        try:
            snd = pygame.mixer.Sound(path)
            self.length_ms = int(snd.get_length() * 1000)
        except Exception:
            self.length_ms = 0
        self.start_ms = 0
        self.started_at = 0
        self.paused = False
        self.pause_at = 0

    def play(self):
        if not self.path: return
        # если мы в паузе — просто продолжаем
        if self.paused:
            pygame.mixer.music.unpause()
            self.paused = False
            # корректируем старт времени
            self.started_at = int(time.time()*1000) - (self.pause_at - self.start_ms)
            return
        # старт/рестарт с позиции self.start_ms
        sec = self.start_ms/1000.0
        pygame.mixer.music.play(start=sec)
        self.started_at = int(time.time()*1000)

    def pause(self):
        if not self.path: return
        if not self.paused:
            pygame.mixer.music.pause()
            self.paused = True
            self.pause_at = self.get_pos_ms()

    def stop(self):
        pygame.mixer.music.stop()
        self.paused = False
        self.start_ms = 0
        self.started_at = 0
        self.pause_at = 0

    def get_pos_ms(self):
        if not self.path: return 0
        if self.paused:
            return self.pause_at
        if self.started_at == 0:
            return self.start_ms
        return max(self.start_ms, int(time.time()*1000) - self.started_at + self.start_ms)

    def set_pos_ms(self, ms):
        if not self.path: return
        self.start_ms = max(0, ms)
        was_playing = pygame.mixer.music.get_busy() and not self.paused
        if was_playing:
            self.play()  # перезапускаем с новой позиции

    def set_volume(self, vol):
        pygame.mixer.music.set_volume(max(0.0, min(1.0, vol)))  # 0..1

# ---- Backend на winsound (WAV only, без паузы/перемотки) ----
class WinSoundBackend(BackendBase):
    name = "winsound"
    can_pause = False
    can_seek = False
    can_volume = False

    def __init__(self):
        self.path = None
        self._playing = False
        self._t = None
        self.length_ms = 0
        self.started_at = 0

    def _play_async(self):
        if not self.path: return
        self.started_at = int(time.time()*1000)
        winsound.PlaySound(self.path, winsound.SND_FILENAME | winsound.SND_ASYNC)

    def open(self, path):
        self.stop()
        if not path.lower().endswith(".wav"):
            raise RuntimeError("В режиме без pygame поддерживаются только WAV-файлы.")
        self.path = path
        # определим длину через wave
        try:
            with contextlib.closing(wave.open(self.path, 'rb')) as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                self.length_ms = int(frames * 1000 / rate)
        except Exception:
            self.length_ms = 0

    def play(self):
        if not self.path: return
        self._playing = True
        self._play_async()

    def pause(self):
        pass  # не поддерживается

    def stop(self):
        if self._playing:
            winsound.PlaySound(None, 0)
        self._playing = False
        self.started_at = 0

    def get_pos_ms(self):
        if not self._playing: return 0
        return int(time.time()*1000) - self.started_at

# Выбор backend’а
Backend = PygameBackend if USE_PYGAME else WinSoundBackend

# ----------------- GUI -----------------
APP_NAME = "MiniPlayer — без VLC"
UPDATE_MS = 200

class MiniPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME + ("" if USE_PYGAME else " (WAV-only)"))
        self.geometry("560x220")
        self.backend = Backend()

        self._build_ui()
        self.after(UPDATE_MS, self._tick)

        if not USE_PYGAME:
            ttk.Label(self, text="⚠ Без pygame доступны только WAV и нет паузы/перемотки.",
                      foreground="#b35c00").pack(side=tk.BOTTOM, pady=6)

    def _build_ui(self):
        top = tk.Frame(self, padx=8, pady=8); top.pack(fill=tk.X)

        ttk.Button(top, text="Открыть файл…", command=self.open_file).pack(side=tk.LEFT)
        self.btn_play = ttk.Button(top, text="▶ Play", command=self.play_pause, state=tk.DISABLED)
        self.btn_play.pack(side=tk.LEFT, padx=6)
        ttk.Button(top, text="■ Stop", command=self.stop, state=tk.NORMAL).pack(side=tk.LEFT)

        self.time_lbl = ttk.Label(top, text="00:00 / 00:00")
        self.time_lbl.pack(side=tk.RIGHT)

        mid = tk.Frame(self, padx=10); mid.pack(fill=tk.X)
        self.scale = ttk.Scale(mid, from_=0, to=1000, orient=tk.HORIZONTAL, command=self._on_seek)
        self.scale.pack(fill=tk.X)
        if not self.backend.can_seek:
            self.scale.state(["disabled"])

        bottom = tk.Frame(self, padx=10, pady=8); bottom.pack(fill=tk.X)
        ttk.Label(bottom, text="Громкость").pack(side=tk.LEFT)
        self.vol = tk.DoubleVar(value=1.0)
        self.vol_scale = ttk.Scale(bottom, from_=0, to=1, variable=self.vol,
                                   orient=tk.HORIZONTAL, command=self._on_volume)
        self.vol_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8)
        if not self.backend.can_volume:
            self.vol_scale.state(["disabled"])

        self.file_lbl = ttk.Label(self, text="Файл не выбран", foreground="#555")
        self.file_lbl.pack(anchor="w", padx=12)

    def open_file(self):
        types = [("Аудио (mp3/wav/ogg)", "*.mp3;*.wav;*.ogg"), ("Все файлы", "*.*")]
        if not USE_PYGAME:
            types = [("WAV", "*.wav")]
        fn = filedialog.askopenfilename(filetypes=types)
        if not fn: return
        try:
            self.backend.open(fn)
            self.file_lbl.config(text=os.path.basename(fn))
            self.btn_play.state(["!disabled"])
            # обновим длину
            self._update_time(0, self.backend.length_ms)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def play_pause(self):
        # для winsound: только Play (pause нет)
        if not self.backend.can_pause:
            self.backend.play()
            self.btn_play.config(text="▶ Play")
            return

        # pygame
        if self.btn_play.cget("text").startswith("▶"):
            self.backend.play()
            self.btn_play.config(text="⏸ Pause")
        else:
            self.backend.pause()
            self.btn_play.config(text="▶ Play")

    def stop(self):
        self.backend.stop()
        self.btn_play.config(text="▶ Play")
        self.scale.set(0)
        self._update_time(0, self.backend.length_ms)

    def _on_volume(self, *_):
        if self.backend.can_volume:
            self.backend.set_volume(self.vol.get())

    def _on_seek(self, *_):
        if self.backend.can_seek and self.backend.length_ms > 0:
            pos = int(float(self.scale.get())/1000.0 * self.backend.length_ms)
            self.backend.set_pos_ms(pos)

    def _tick(self):
        try:
            cur = self.backend.get_pos_ms()
            total = self.backend.length_ms
            if total > 0 and cur >= 0 and cur <= total and self.backend.can_seek:
                self.scale.set(cur/total*1000.0)
            self._update_time(cur, total)
        finally:
            self.after(UPDATE_MS, self._tick)

    def _fmt_ms(self, ms):
        if ms <= 0: return "00:00"
        s = ms//1000
        m, s = divmod(s, 60)
        h, m = divmod(m, 60)
        return f"{h:02}:{m:02}:{s:02}" if h else f"{m:02}:{s:02}"

    def _update_time(self, cur, total):
        self.time_lbl.config(text=f"{self._fmt_ms(cur)} / {self._fmt_ms(total)}")

if __name__ == "__main__":
    app = MiniPlayer()
    app.mainloop()
