import tkinter as tk
import tkinter.font as tkfont
import json
import os
import sys
import pyautogui
import time
import mouse
import keyboard
import mortar_tools.calculator as calc

class main():
    def __init__(self):
        self.title = "Mortar Distance Measurement Tool"
        self.geometry = "360x220"
        self.start_hotkey = "alt+q"
        self.point_hotkey = "alt+left"
        self.point_modifier = self.point_hotkey.split("+", 1)[0]
        self.reset_hotkey = "alt+right"
        self.start_combo_max_interval = 0.5
        self.exit_combo_guard_seconds = 1.5
        self.start_combo_options = [0.3, 0.5, 0.8]
        self.reset_requested = False
        self.is_measuring = False
        self.exit_signal = object()
        self.modifier_is_down = False
        self.alt_is_down = False
        self.q_is_down = False
        self.alt_down_at = 0.0
        self.q_down_at = 0.0
        self.exit_combo_count = 0
        self.exit_combo_deadline = 0.0
        self.start_hotkey_latched = False
        self.start_requested = False
        self.language = "en"
        self.root = None
        self.current_page = "home"
        self.content_frame = None
        self.home_frame = None
        self.settings_frame = None
        self.message_label = None
        self.language_var = None
        self.start_interval_var = None
        self.settings_path = self.get_settings_path()

        self.i18n = {
            "en": {
                "window_title": "Mortar Distance Measurement Tool",
                "menu_settings": "Settings",
                "menu_home": "Home",
                "menu_language": "Language",
                "menu_lang_en": "English",
                "menu_lang_zh": "Chinese",
                "menu_trigger_window": "Start Trigger Window",
                "menu_trigger_window_value": "{value:.1f}s",
                "settings_title": "Settings",
                "settings_hint": "If your Alt key is bound to other keys and easily triggers distance measurement with Q, you can reduce the interval to 0.3s; if Alt+Q is hard to trigger, you can increase it to 0.8s.",
                "settings_back": "Back to Home",
                "control_title": "Control:",
                "control_start": "Alt + Q: Start measurement",
                "control_point": "Alt + Left: Set point",
                "control_reset": "Alt + Right Click: Reset measurement",
                "step_scale_1": "Set 100 meters: First point",
                "step_scale_2": "Set 100 meters: Second point",
                "step_measure_1": "Measurement: First point",
                "step_measure_2": "Measurement: Second point",
                "max_distance": "MAX Distance: {value:.2f} m",
                "step_elevation": "Elevation angle: Only one point",
                "elevation_value": "Elevation angle: {value:.2f} degrees",
                "distance_value": "Distance: {value:.2f} m",
                "reset_restarting": "Reset detected. Restarting...",
            },
            "zh": {
                "window_title": "迫击炮距离测量工具",
                "menu_settings": "设置",
                "menu_home": "首页",
                "menu_language": "语言",
                "menu_lang_en": "英文",
                "menu_lang_zh": "中文",
                "menu_trigger_window": "触发窗口",
                "menu_trigger_window_value": "{value:.1f}秒",
                "settings_title": "设置",
                "settings_hint": "如果你的 Alt 键绑定的其他键，容易和Q误触发测距，可调小触发时机到0.3秒内；如果 Alt+Q 难触发，可调大到0.8秒。",
                "settings_back": "返回首页",
                "control_title": "操作说明:",
                "control_start": "Alt + Q: 开始测距",
                "control_point": "Alt + 左键: 标点",
                "control_reset": "Alt + 右键: 重置流程",
                "step_scale_1": "设置100米比例尺：第一个点",
                "step_scale_2": "设置100米比例尺：第二个点",
                "step_measure_1": "测距：第一个点（自己的位置）",
                "step_measure_2": "测距：第二个点（目标位置）",
                "max_distance": "最大距离: {value:.2f} 米",
                "step_elevation": "高低差角度：标记你要打击的目标",
                "elevation_value": "仰角: {value:.2f} 度",
                "distance_value": "最终距离: {value:.2f} 米",
                "reset_restarting": "检测到重置，正在重新开始...",
            },
        }

        self.load_settings()
        self.title = self.t("window_title")

    def get_settings_path(self):
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "settings.json")

    def load_settings(self):
        if not os.path.exists(self.settings_path):
            return

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return

        saved_lang = data.get("language")
        if saved_lang in self.i18n:
            self.language = saved_lang

        saved_interval = data.get("start_combo_max_interval")
        if isinstance(saved_interval, (int, float)):
            for option in self.start_combo_options:
                if abs(float(saved_interval) - option) < 1e-6:
                    self.start_combo_max_interval = float(option)
                    break

    def save_settings(self):
        data = {
            "language": self.language,
            "start_combo_max_interval": self.start_combo_max_interval,
        }
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError:
            pass

    def t(self, key, **kwargs):
        text = self.i18n[self.language][key]
        if kwargs:
            return text.format(**kwargs)
        return text

    def get_ui_font(self):
        if self.language == "zh":
            return ("Microsoft YaHei UI", 12)
        return ("Consolas", 12)

    def fit_window_to_content(self):
        if self.root is None or self.message_label is None:
            return

        text = self.get_info_text()
        lines = text.splitlines()
        if not lines:
            lines = [""]

        font = tkfont.Font(font=self.message_label.cget("font"))
        max_text_width = max(font.measure(line) for line in lines)
        lines_height = font.metrics("linespace") * len(lines)

        width = max(360, max_text_width + 36)
        height = max(220, lines_height + 90)

        self.root.geometry(f"{width}x{height}")
        self.root.minsize(width, height)

    def update_window_size_for_page(self):
        if self.root is None:
            return

        if self.current_page == "settings":
            width, height = 460, 320
            self.root.geometry(f"{width}x{height}")
            self.root.minsize(width, height)
            return

        self.fit_window_to_content()

    def get_info_text(self):
        return (
            f"{self.t('control_title')}\n"
            f"{self.t('control_start')}\n"
            f"{self.t('control_point')}\n\n"
            f"{self.t('control_reset')}\n\n"
        )

    def set_language(self, lang):
        if lang not in self.i18n:
            return
        self.language = lang
        self.title = self.t("window_title")
        self.save_settings()
        self.refresh_ui_texts()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        menu_bar.add_command(label=self.t("menu_home"), command=self.show_home_page)
        menu_bar.add_command(label=self.t("menu_settings"), command=self.show_settings_page)
        self.root.config(menu=menu_bar)

    def create_pages(self):
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill="both", expand=True)

        self.home_frame = tk.Frame(self.content_frame)
        self.settings_frame = tk.Frame(self.content_frame)

        self.message_label = tk.Label(self.home_frame, text="", justify="left", anchor="nw")
        self.message_label.pack(fill="both", expand=True, padx=12, pady=(10, 12))

        self.language_var = tk.StringVar(value=self.language)
        self.start_interval_var = tk.DoubleVar(value=self.start_combo_max_interval)

    def build_settings_page(self):
        if self.settings_frame is None:
            return

        for child in self.settings_frame.winfo_children():
            child.destroy()

        ui_font = self.get_ui_font()
        title_font = (ui_font[0], ui_font[1] + 1)

        self.language_var.set(self.language)
        self.start_interval_var.set(self.start_combo_max_interval)

        title_label = tk.Label(self.settings_frame, text=self.t("settings_title"), font=title_font, anchor="w")
        title_label.pack(fill="x", padx=14, pady=(12, 6))

        language_label = tk.Label(self.settings_frame, text=self.t("menu_language"), font=ui_font, anchor="w")
        language_label.pack(fill="x", padx=14, pady=(6, 4))

        language_options = tk.Frame(self.settings_frame)
        language_options.pack(fill="x", padx=14)
        tk.Radiobutton(
            language_options,
            text=self.t("menu_lang_en"),
            value="en",
            variable=self.language_var,
            command=lambda: self.set_language(self.language_var.get()),
            font=ui_font,
            anchor="w",
        ).pack(side="left", padx=(0, 12))
        tk.Radiobutton(
            language_options,
            text=self.t("menu_lang_zh"),
            value="zh",
            variable=self.language_var,
            command=lambda: self.set_language(self.language_var.get()),
            font=ui_font,
            anchor="w",
        ).pack(side="left")

        trigger_label = tk.Label(self.settings_frame, text=self.t("menu_trigger_window"), font=ui_font, anchor="w")
        trigger_label.pack(fill="x", padx=14, pady=(10, 4))

        trigger_options = tk.Frame(self.settings_frame)
        trigger_options.pack(fill="x", padx=14)
        for option in self.start_combo_options:
            tk.Radiobutton(
                trigger_options,
                text=self.t("menu_trigger_window_value", value=option),
                value=option,
                variable=self.start_interval_var,
                command=lambda v=option: self.set_start_combo_interval(v),
                font=ui_font,
                anchor="w",
            ).pack(side="left", padx=(0, 12))

        hint_label = tk.Label(
            self.settings_frame,
            text=self.t("settings_hint"),
            font=ui_font,
            justify="left",
            anchor="w",
            wraplength=430,
        )
        hint_label.pack(fill="x", padx=14, pady=(14, 8))

        back_button = tk.Button(self.settings_frame, text=self.t("settings_back"), command=self.show_home_page)
        back_button.pack(anchor="w", padx=14, pady=(2, 10))

    def show_page(self, page):
        self.current_page = page
        if self.home_frame is not None:
            self.home_frame.pack_forget()
        if self.settings_frame is not None:
            self.settings_frame.pack_forget()

        if page == "settings":
            self.settings_frame.pack(fill="both", expand=True)
        else:
            self.home_frame.pack(fill="both", expand=True)

        self.update_window_size_for_page()

    def show_home_page(self):
        self.show_page("home")

    def show_settings_page(self):
        self.build_settings_page()
        self.show_page("settings")

    def set_start_combo_interval(self, value):
        value = float(value)
        if value not in self.start_combo_options:
            return
        self.start_combo_max_interval = value
        self.save_settings()
        self.refresh_ui_texts()

    def refresh_ui_texts(self):
        if self.root is not None:
            self.root.title(self.t("window_title"))
            self.create_menu()
        if self.message_label is not None:
            self.message_label.config(font=self.get_ui_font())
            self.message_label.config(text=self.get_info_text())
        if self.current_page == "settings":
            self.build_settings_page()
        self.update_window_size_for_page()

    
    def create_static_window(self):
        window = tk.Toplevel(self.root)
        window.overrideredirect(True)
        window.attributes("-topmost", True)
        label = tk.Label(window, font=("Helvetica", 14), bg="yellow", padx=10, pady=5)
        label.pack()
        window.update_idletasks()
        window.geometry("+0+0")
        window.lift()
        return window, label

    def _set_overlay_text(self, window, label, key, **kwargs):
        label.config(text=self.t(key, **kwargs))
        window.update()
        self.pump_main_ui()

    def pump_main_ui(self):
        if self.root is None:
            return
        try:
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            pass

    def wait_with_ui(self, seconds, interval=0.03, allow_exit=False):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if allow_exit and self.consume_exit_request():
                return "exit"
            self.pump_main_ui()
            time.sleep(interval)
        return "ok"

    def get_point(self):
        pos = None

        def on_click(event):
            nonlocal pos
            if not isinstance(event, mouse.ButtonEvent) or event.event_type != 'down':
                return

            modifier_pressed = self.modifier_is_down or keyboard.is_pressed(self.point_modifier)

            if modifier_pressed and event.button == 'right':
                self.reset_requested = True
                return

            if modifier_pressed and event.button == 'left':
                pos = pyautogui.position()
        mouse.hook(on_click)

        try:
            # 等待用户点击
            while pos is None:
                if self.consume_exit_request():
                    return self.exit_signal
                if self.reset_requested:
                    return None
                self.pump_main_ui()
                time.sleep(0.03)  # 防止 CPU 过载，同时提高退出与重置响应速度
            return pos
        finally:
            mouse.unhook(on_click)

    def request_reset(self):
        if self.is_measuring:
            self.reset_requested = True

    def try_trigger_start_combo(self):
        if self.start_hotkey_latched:
            return
        if not (self.alt_is_down and self.q_is_down):
            return

        if abs(self.alt_down_at - self.q_down_at) <= self.start_combo_max_interval:
            self.start_hotkey_latched = True
            if self.is_measuring:
                self.register_exit_combo()
            else:
                self.start_requested = True

    def register_exit_combo(self):
        now = time.monotonic()

        if self.exit_combo_count == 0 or now > self.exit_combo_deadline:
            self.exit_combo_count = 1
            self.exit_combo_deadline = now + self.exit_combo_guard_seconds
            return

        self.exit_combo_count += 1

    def consume_exit_request(self):
        if self.exit_combo_count == 0:
            return False

        if time.monotonic() < self.exit_combo_deadline:
            return False

        should_exit = self.exit_combo_count == 1
        self.exit_combo_count = 0
        self.exit_combo_deadline = 0.0
        return should_exit

    def on_alt_press(self, _event):
        if self.alt_is_down:
            return
        self.alt_is_down = True
        self.modifier_is_down = True
        self.alt_down_at = time.monotonic()
        self.try_trigger_start_combo()

    def on_alt_release(self, _event):
        self.alt_is_down = False
        self.modifier_is_down = False
        self.start_hotkey_latched = False

    def on_q_press(self, _event):
        if self.q_is_down:
            return
        self.q_is_down = True
        self.q_down_at = time.monotonic()
        self.try_trigger_start_combo()

    def on_q_release(self, _event):
        self.q_is_down = False
        self.start_hotkey_latched = False

    def process_pending_actions(self):
        if self.start_requested and not self.is_measuring:
            self.start_requested = False
            self.start_measurement()
        self.root.after(30, self.process_pending_actions)

    def _get_step_point(self, window, label, text):
        label.config(text=text)
        window.update()
        return self.get_point()

    def _measure_two_points(self, window, label, first_key, second_key):
        point1 = self._get_step_point(window, label, self.t(first_key))
        if point1 is self.exit_signal:
            return self.exit_signal, self.exit_signal
        if point1 is None:
            return None, None
        point2 = self._get_step_point(window, label, self.t(second_key))
        if point2 is self.exit_signal:
            return self.exit_signal, self.exit_signal
        if point2 is None:
            return None, None
        return point1, point2

    def _run_measurement_once(self, window, label):
        calculator = calc.calculator()

        # get point1 and point2 for scale factor
        point1, point2 = self._measure_two_points(window, label, "step_scale_1", "step_scale_2")
        if point1 is self.exit_signal:
            return "exit"
        if point1 is None:
            return "reset"

        # calculate scale factor
        calculator.set_scale_factor(point1, point2)

        # get point1 and point2 for distance
        point1, point2 = self._measure_two_points(window, label, "step_measure_1", "step_measure_2")
        if point1 is self.exit_signal:
            return "exit"
        if point1 is None:
            return "reset"

        # calculate horizontal distance
        calculator.get_horizontal_distance(point1, point2)
        self._set_overlay_text(window, label, "max_distance", value=calculator.horizontal_distance)

        # get elevation angle point
        point = self._get_step_point(window, label, self.t("step_elevation"))
        if point is self.exit_signal:
            return "exit"
        if point is None:
            return "reset"

        # calculate elevation angle
        self._set_overlay_text(window, label, "elevation_value", value=calculator.get_evelation_angle(point))

        # calculate final distance
        self._set_overlay_text(
            window,
            label,
            "distance_value",
            value=calculator.solve(calculator.evelation_angle, calculator.horizontal_distance),
        )

        return "done"
    
    def start_measurement(self):
        if self.is_measuring:
            return

        self.is_measuring = True
        window, label = self.create_static_window()

        try:
            while True:
                self.reset_requested = False
                status = self._run_measurement_once(window, label)

                if status == "exit":
                    window.withdraw()
                    window.update_idletasks()
                    break

                if status == "reset":
                    self._set_overlay_text(window, label, "reset_restarting")
                    if self.wait_with_ui(0.2, allow_exit=True) == "exit":
                        window.withdraw()
                        window.update_idletasks()
                        break
                    continue

                if self.wait_with_ui(3, allow_exit=True) == "exit":
                    window.withdraw()
                    window.update_idletasks()
                    break
                break
        finally:
            self.reset_requested = False
            self.is_measuring = False
            self.exit_combo_count = 0
            self.exit_combo_deadline = 0.0
            window.destroy()

    def main(self):
        # register hotkeys
        keyboard.add_hotkey(self.reset_hotkey, self.request_reset)
        keyboard.on_press_key(self.point_modifier, self.on_alt_press)
        keyboard.on_release_key(self.point_modifier, self.on_alt_release)
        keyboard.on_press_key("q", self.on_q_press)
        keyboard.on_release_key("q", self.on_q_release)

        # create UI
        self.root = tk.Tk()
        self.root.geometry(self.geometry)
        self.root.attributes("-topmost", True)

        self.create_pages()

        self.refresh_ui_texts()
        self.show_home_page()
        self.process_pending_actions()
        self.root.mainloop()

if __name__ == "__main__":
    app = main()
    app.main()