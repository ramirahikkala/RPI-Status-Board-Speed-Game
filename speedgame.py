import random
import time
from threading import Thread
from threading import Event
from multiprocessing import Queue
from stopwatch import Stopwatch
from gpiozero import StatusBoard


class SpeedGame:
    def __init__(self):
        self.status_board = StatusBoard()
        self.button_press_queue = Queue(20)
        self.led_shown_queue = Queue(20)
        self.game_over_event = Event()
        self.score = 0
        self.previous_press = Stopwatch()
        self.previous_press.start()

        button_callbacks = {
            0: lambda: self.button_press_queue.put(0),
            1: lambda: self.button_press_queue.put(1),
            2: lambda: self.button_press_queue.put(2),
            3: lambda: self.button_press_queue.put(3),
            4: lambda: self.button_press_queue.put(4),
        }

        strip_count = 0
        self.strip_dict = {}
        for strip in self.status_board:
            strip.lights.red.off()
            strip.lights.green.off()
            strip.button.when_pressed = button_callbacks[strip_count]
            self.strip_dict[strip_count] = strip
            strip_count = strip_count + 1

        # Start lights
        for strip in self.status_board:
            strip.lights.red.on()
            time.sleep(0.5)

        time.sleep(1)

        for strip in self.status_board:
            strip.lights.red.off()

        self.check_thread = Thread(target=self.run_check_thread)
        self.check_thread.name = "Button check thread"
        self.check_thread.setDaemon(True)
        self.check_thread.start()

        self.led_show_thread = Thread(target=self.run_led_thread)
        self.led_show_thread.name = "Led thread"
        self.led_show_thread.setDaemon(True)
        self.led_show_thread.start()

        self.game_over_event.wait()

        for strip in self.status_board:
            # start with all the reds on
            strip.lights.red.on()

        print("Points: " + str(self.score))

    def run_check_thread(self):
        while True:
            button = self.button_press_queue.get()
            # Omit button glitches
            if self.previous_press.duration < 0.05:
                continue
            led_shown = self.led_shown_queue.get()
            if button != led_shown:
                self.game_over_event.set()
                break
            else:
                self.score = self.score + 1

    def run_led_thread(self):
        sleep_time = 2
        while True:
            time.sleep(sleep_time)
            if self.game_over_event.is_set():
                break
            rand = random.randint(0, 4)
            self.led_shown_queue.put(rand)
            self.strip_dict[rand].lights.green.on()
            time.sleep(sleep_time / 2)
            self.strip_dict[rand].lights.green.off()
            if sleep_time > 0.4:
                sleep_time = sleep_time * 0.9


SpeedGame()
input("Press Enter to continue...")
