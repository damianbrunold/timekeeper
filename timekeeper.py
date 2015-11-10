#!/usr/bin/env python3

import math
import os
import time

from tkinter import *
from tkinter.ttk import *

ACTIVITIES_FILE = "activities.txt"

ACTIVITIES = ["testing automatic",
              "testing manual",
              "programming",
              "support",
              "other"]

TIMESTAMP_FORMAT = "%Y%m%d-%H%M%S"


def read_activities():
    global ACTIVITIES
    if os.path.exists(ACTIVITIES_FILE):
        ACTIVITIES = []
        with open(ACTIVITIES_FILE, "r", encoding="utf-8") as infile:
            for line in infile:
                line = line.strip()
                if line:
                    ACTIVITIES.append(line)


def prefixes():
    result = set([])
    for activity in ACTIVITIES:
        pos = activity.find(" ")
        if pos != -1:
            result.add(activity[0:pos])
    return result


def hms(d):
    d = int(d)
    seconds = d % 60
    d //= 60
    minutes = d % 60
    d //= 60
    hours = d
    return (hours, minutes, seconds)


def duration_with_seconds(d):
    hours, minutes, seconds = hms(d)
    if hours:
        return "{0:d}:{1:02d}:{2:02d} h".format(hours, minutes, seconds)
    else:
        return "{0:d}:{1:02d} min".format(minutes, seconds)


def duration(d):
    hours, minutes, _ = hms(d * 60)
    return "{0:d}:{1:02d} h".format(hours, minutes)


def duration_stats(values):
    if len(values) == 0: return None
    min_duration = min(values)
    max_duration = max(values)
    avg_duration = sum(values) / len(values)
    std_duration = math.sqrt(sum([math.pow(duration - avg_duration, 2) for duration in values]) / len(values))
    return (min_duration, max_duration, avg_duration, std_duration)


def timestamp(when=0):
    return time.strftime(TIMESTAMP_FORMAT, time.localtime(when or time.time()))


def parse_timestamp(timestamp):
    if "-" in timestamp:
        return int(time.mktime(time.strptime(timestamp, TIMESTAMP_FORMAT)))
    else:
        return int(timestamp)


def get_day_file_name():
    return time.strftime("%Y-%m-%d.txt")


def ensure_path(*dirs):
    path = os.path.join(*dirs)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    return path


def get_raw_file():
    return os.path.join(ensure_path("data", "raw"), get_day_file_name())


def get_log_file():
    return os.path.join(ensure_path("data"), get_day_file_name())


class TimekeeperModel(object):
    def __init__(self):
        self.activity = None
        self.start = -1
        self.summary = {}
        self.activities = []
        self.read_raw_data()

    def read_raw_data(self):
        rawfile = get_raw_file()
        if os.path.exists(rawfile):
            with open(rawfile, "r", encoding="utf-8") as rawdata:
                for line in rawdata:
                    start, end, activity = line.strip().split(",")
                    start = parse_timestamp(start)
                    end = parse_timestamp(end)
                    minutes = (end - start) // 60
                    self.activities.append((activity, minutes, start, end))
                    if not activity in self.summary:
                        self.summary[activity] = minutes
                    else:
                        self.summary[activity] += minutes

    def elapsed_with_seconds(self):
        return int(time.time() - self.start)

    def elapsed(self):
        return self.elapsed_with_seconds() // 60

    def credit_activity(self):
        self.activities.append((self.activity, self.elapsed(), self.start, int(time.time())))
        if not self.activity in self.summary:
            self.summary[self.activity] = self.elapsed()
        else:
            self.summary[self.activity] += self.elapsed()

    def log_duration(self):
        with open(get_log_file(), "a", encoding="utf-8") as logfile:
            starttime = time.strftime("%H:%M", time.localtime(self.start))
            endtime = time.strftime("%H:%M")
            logfile.write("{0} - {1} {2:<25s} {3}\n".format(starttime, endtime, self.activity, duration(self.elapsed())))

    def log_raw_duration(self):
        with open(get_raw_file(), "a", encoding="utf-8") as rawfile:
            rawfile.write("{0},{1},{2}\n".format(timestamp(self.start), timestamp(), self.activity))

    def set_activity(self, activity):
        if self.activity:
            if self.activity != activity:
                if self.elapsed_with_seconds() < 10:
                    self.activity = activity
                else:
                    self.log_raw_duration()
                    self.log_duration()
                    self.credit_activity()
                    self.activity = activity
                    self.start = time.time()
            else:
                self.start -= 60
        else:
            self.activity = activity
            self.start = time.time()

    def print_task_breakdown(self):
        if len(self.activities) == 0: return
        total = sum(self.summary.values())
        with open(get_log_file(), "w", encoding="utf-8") as logfile:
            for activity in self.activities:
                start = time.strftime("%H:%M", time.localtime(activity[2]))
                end = time.strftime("%H:%M", time.localtime(activity[3]))
                logfile.write("{0} - {1} {2:<25s} {3:>7s}\n".format(start, end, activity[0], duration(activity[1])))
            logfile.write("\n")
            if total == 0: return
            logfile.write("Task breakdown:\n")
            for item in sorted(self.summary.items(), key=lambda x: x[1], reverse=True):
                logfile.write("{0:<25s} {1:>7s} {2:>4d}%\n".format(item[0], duration(item[1]), 100 * item[1] // total))
            logfile.write("{0:<25s} {1:>7s} {2:>4d}%\n".format("total", duration(total), 100))
            logfile.write("\n")
            if prefixes():
                logfile.write("Prefix breakdown:\n")
                for prefix in prefixes():
                    prefix_duration = sum([item[1] for item in self.summary.items() if item[0].startswith(prefix)])
                    if prefix_duration:
                        logfile.write("{0:<25s} {1:>7s} {2:>4d}%\n".format(prefix, duration(prefix_duration), 100 * prefix_duration // total))
                logfile.write("\n")
            switches = len(self.activities) - 1
            switches_per_hour = switches / (total / 60)
            logfile.write("{0} activity switches ({1:.1f}/h)\n".format(switches, switches_per_hour))
            logfile.write("min {0} min, max {1} min, avg {2:.1f} min, std {3:.1f} min\n".format(*duration_stats([a[1] for a in self.activities])))
            logfile.write("\n")


class TimekeeperApp(TimekeeperModel, Frame):
    def __init__(self, master=None):
        TimekeeperModel.__init__(self)
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.update_state()

    def stop(self):
        self.set_activity(None)

    def stopAndQuit(self):
        self.unbind("<Destroy>", funcid=None)
        self.stop()
        self.print_task_breakdown()
        self.quit()

    def get_activity_handler(self, activity):
        def handler():
            self.set_activity(activity)
        return handler

    def createButton(self, text, command):
        button = Button(self, text=text, command=command)
        button.grid(pady=2, sticky="ew")
        return button

    def createLabel(self, text):
        label = Label(self, text=text)
        label.grid()
        return label

    def createWidgets(self):
        self.timeLabel = self.createLabel(time.strftime("%Y-%m-%d %H:%M"))
        self.activityLabel = self.createLabel("-")
        self.elapsedLabel = self.createLabel("-")
        self.totalLabel = self.createLabel("-")
        self.buttons = {}
        for activity in ACTIVITIES:
            self.buttons[activity] = self.createButton(activity, self.get_activity_handler(activity))
        self.stopButton = self.createButton("[stop]", self.stop)
        self.quitButton = self.createButton("[quit]", self.stopAndQuit)
        self.bind("<Destroy>", self._destroy)

    def _destroy(self, event):
        self.stopAndQuit()

    def update_button(self, button, activity):
        if activity in self.summary:
            button.configure(text="{0} ({1})".format(activity, duration(self.summary[activity])))

    def update_state(self):
        self.timeLabel.configure(text=time.strftime("%Y-%m-%d %H:%M"))
        if self.activity:
            activity_duration = duration_with_seconds(self.elapsed_with_seconds())
            total_duration = duration(sum(self.summary.values()) + self.elapsed())
            self.activityLabel.configure(text=self.activity)
            self.elapsedLabel.configure(text=activity_duration)
            self.totalLabel.configure(text="total {0}".format(total_duration))
        for activity in ACTIVITIES:
            self.update_button(self.buttons[activity], activity)
        self.after(500, self.update_state)


if __name__ == "__main__":
    read_activities()
    app = TimekeeperApp()
    app.master.title("Timekeeper")
    app.update_state()
    app.mainloop()
