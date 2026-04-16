import tkinter as tk
import pyautogui
import time
import mouse
import keyboard
import mortar_tools.calculator as calc

class main():
    def __init__(self):
        self.title = "Mortar Distance Measurement Tool"
        self.geometry = "300x150"
        self.start_hotkey = "alt+q"
        self.point_hotkey = "alt+left"
        self.point_modifier = self.point_hotkey.split("+", 1)[0]
        self.reset_hotkey = "alt+right"
        self.reset_requested = False
        self.is_measuring = False
        self.language = "en"
        self.root = None
        self.message_label = None

        self.i18n = {
            "en": {
                "window_title": "Mortar Distance Measurement Tool",
                "menu_settings": "Settings",
                "menu_language": "Language",
                "menu_lang_en": "English",
                "menu_lang_zh": "Chinese",
                "control_title": "Control:",
                "control_start": "Alt + Q: Start measurement",
                "control_point": "Alt + Left: Set point",
                "control_reset": "Alt + Right: Reset measurement",
                "step_scale_1": "Set 100 meters: First point",
                "step_scale_2": "Set 100 meters: Second point",
                "step_measure_1": "Measurement: First point",
                "step_measure_2": "Measurement: Second point",
                "max_distance": "MAX Distance: {value:.2f} m",
                "step_elevation": "Elevation angle: Only one point",
                "elevation_value": "Evelation angle: {value:.2f} degrees",
                "distance_value": "Distance: {value:.2f} m",
                "reset_restarting": "Reset detected. Restarting...",
            },
            "zh": {
                "window_title": "迫击炮距离测量工具",
                "menu_settings": "设置",
                "menu_language": "语言",
                "menu_lang_en": "英文",
                "menu_lang_zh": "中文",
                "control_title": "操作说明:",
                "control_start": "Alt + Q: 开始测距",
                "control_point": "Alt + 左键: 标点",
                "control_reset": "Alt + 右键: 重置流程",
                "step_scale_1": "设置100米比例尺：第一个点",
                "step_scale_2": "设置100米比例尺：第二个点",
                "step_measure_1": "测距：第一个点",
                "step_measure_2": "测距：第二个点",
                "max_distance": "最大距离: {value:.2f} 米",
                "step_elevation": "高低差角度：只需一个点",
                "elevation_value": "仰角: {value:.2f} 度",
                "distance_value": "最终距离: {value:.2f} 米",
                "reset_restarting": "检测到重置，正在重新开始...",
            },
        }

    def t(self, key, **kwargs):
        text = self.i18n[self.language][key]
        if kwargs:
            return text.format(**kwargs)
        return text

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
        self.refresh_ui_texts()

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        settings_menu = tk.Menu(menu_bar, tearoff=0)
        language_menu = tk.Menu(settings_menu, tearoff=0)
        language_menu.add_command(label=self.t("menu_lang_en"), command=lambda: self.set_language("en"))
        language_menu.add_command(label=self.t("menu_lang_zh"), command=lambda: self.set_language("zh"))

        settings_menu.add_cascade(label=self.t("menu_language"), menu=language_menu)
        menu_bar.add_cascade(label=self.t("menu_settings"), menu=settings_menu)
        self.root.config(menu=menu_bar)

    def refresh_ui_texts(self):
        if self.root is not None:
            self.root.title(self.t("window_title"))
            self.create_menu()
        if self.message_label is not None:
            self.message_label.config(text=self.get_info_text())

    
    def create_static_window(self):
        window = tk.Toplevel(self.root)
        window.overrideredirect(True)
        window.geometry("+10+10")
        window.attributes("-topmost", True)
        label = tk.Label(window, font=("Helvetica", 14), bg="yellow", padx=10, pady=5)
        label.pack()
        return window, label

    def _set_overlay_text(self, window, label, key, **kwargs):
        label.config(text=self.t(key, **kwargs))
        window.update()

    def get_point(self):
        pos = None

        def on_click(event):
            nonlocal pos
            if isinstance(event, mouse.ButtonEvent) and event.event_type == 'down' and event.button == 'left' and keyboard.is_pressed(self.point_modifier):
                pos = pyautogui.position()
        mouse.hook(on_click)

        try:
            # 等待用户点击
            while pos is None:
                if self.reset_requested:
                    return None
                time.sleep(0.05)  # 防止 CPU 过载，同时提高重置响应速度
            return pos
        finally:
            mouse.unhook(on_click)

    def request_reset(self):
        if self.is_measuring:
            self.reset_requested = True

    def _get_step_point(self, window, label, text):
        label.config(text=text)
        window.update()
        return self.get_point()

    def _measure_two_points(self, window, label, first_key, second_key):
        point1 = self._get_step_point(window, label, self.t(first_key))
        if point1 is None:
            return None, None
        point2 = self._get_step_point(window, label, self.t(second_key))
        if point2 is None:
            return None, None
        return point1, point2

    def _run_measurement_once(self, window, label):
        calculator = calc.calculator()

        # get point1 and point2 for scale factor
        point1, point2 = self._measure_two_points(window, label, "step_scale_1", "step_scale_2")
        if point1 is None:
            return None

        # calculate scale factor
        calculator.set_scale_factor(point1, point2)

        # get point1 and point2 for distance
        point1, point2 = self._measure_two_points(window, label, "step_measure_1", "step_measure_2")
        if point1 is None:
            return None

        # calculate horizontal distance
        calculator.get_horizontal_distance(point1, point2)
        self._set_overlay_text(window, label, "max_distance", value=calculator.horizontal_distance)

        # get elevation angle point
        point = self._get_step_point(window, label, self.t("step_elevation"))
        if point is None:
            return None

        # calculate elevation angle
        self._set_overlay_text(window, label, "elevation_value", value=calculator.get_evelation_angle(point))

        # calculate final distance
        self._set_overlay_text(
            window,
            label,
            "distance_value",
            value=calculator.solve(calculator.evelation_angle, calculator.horizontal_distance),
        )

        return calculator.result
    
    def start_measurement(self):
        if self.is_measuring:
            return

        self.is_measuring = True
        window, label = self.create_static_window()

        try:
            while True:
                self.reset_requested = False
                result = self._run_measurement_once(window, label)

                if result is None:
                    self._set_overlay_text(window, label, "reset_restarting")
                    time.sleep(0.2)
                    continue

                time.sleep(3)
                break
        finally:
            self.reset_requested = False
            self.is_measuring = False
            window.destroy()

    def main(self):
        # register hotkeys
        keyboard.add_hotkey(self.start_hotkey, self.start_measurement)
        keyboard.add_hotkey(self.point_hotkey, self.get_point)
        keyboard.add_hotkey(self.reset_hotkey, self.request_reset)

        # create UI
        self.root = tk.Tk()
        self.root.geometry(self.geometry)
        self.root.attributes("-topmost", True)

        self.message_label = tk.Label(self.root, text="", font=("Console", 12), justify="left")
        self.message_label.pack(pady=20)

        self.refresh_ui_texts()
        self.root.mainloop()

if __name__ == "__main__":
    app = main()
    app.main()