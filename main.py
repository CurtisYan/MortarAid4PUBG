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
        self.reset_hotkey = "alt+right"
        self.reset_requested = False
        self.is_measuring = False

    
    def create_static_window(self):
        window = tk.Tk()
        window.overrideredirect(True)
        window.geometry("+10+10")
        window.attributes("-topmost", True)
        label = tk.Label(window, font=("Helvetica", 14), bg="yellow", padx=10, pady=5)
        label.pack()
        return window, label

    def get_point(self):
        pos = None

        def on_click(event):
            nonlocal pos
            if isinstance(event, mouse.ButtonEvent) and event.event_type == 'down' and event.button == 'left' and keyboard.is_pressed(self.point_hotkey.split('+')[0]):
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

    def _run_measurement_once(self, window, label):
        calculator = calc.calculator()

        # get point1 and point2 for scale factor
        point1 = self._get_step_point(window, label, "Set 100 meters: First point")
        if point1 is None:
            return None

        point2 = self._get_step_point(window, label, "Set 100 meters: Second point")
        if point2 is None:
            return None

        # calculate scale factor
        calculator.set_scale_factor(point1, point2)

        # get point1 and point2 for distance
        point1 = self._get_step_point(window, label, "Measurement: First point")
        if point1 is None:
            return None

        point2 = self._get_step_point(window, label, "Measurement: Second point")
        if point2 is None:
            return None

        # calculate horizontal distance
        calculator.get_horizontal_distance(point1, point2)
        label.config(text=f"MAX Distance: {calculator.horizontal_distance:.2f} m")
        window.update()

        # get elevation angle point
        point = self._get_step_point(window, label, "Elevation angle: Only one point")
        if point is None:
            return None

        # calculate elevation angle
        label.config(text=f"Evelation angle: {calculator.get_evelation_angle(point):.2f} degrees")
        window.update()

        # calculate final distance
        label.config(text=f"Distance: {calculator.solve(calculator.evelation_angle, calculator.horizontal_distance):.2f} m")
        window.update()

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
                    label.config(text="Reset detected. Restarting...")
                    window.update()
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
        root = tk.Tk()
        root.title(self.title)
        root.geometry(self.geometry)
        root.attributes("-topmost", True)

        # text
        info_text = (
            "Control:\n"
            "Alt + Q: Start measurement\n"
            "Alt + Left: Set point\n\n"
            "Alt + Right: Reset measurement\n\n"
        )

        message_label = tk.Label(root, text=info_text, font=("Console", 12), justify="left")
        message_label.pack(pady=20)

        root.mainloop()

if __name__ == "__main__":
    app = main()
    app.main()