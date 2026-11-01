# Exam Countdown widget

A small desktop widget that shows the **hours left** until JEE Main, CBSE Class 12 boards and JEE Advanced.

There are two versions. Pick one:

| Version | Works on | Needs |
|---|---|---|
| **Rainmeter skin** (`rainmeter/`) | Windows | [Rainmeter](https://www.rainmeter.net/) (free) |
| **Python widget** (`exam_countdown.pyw`) | Windows, macOS, Linux | [Python 3](https://www.python.org/downloads/) |

## Exam dates used

Not every 2027 date is official yet, so the widget marks them **(tentative)**. Update them when the notices come out.

| Exam | Date in widget | Status (as of 1 Nov 2026) |
|---|---|---|
| JEE Main 2027, Session 1 | 20 Jan 2027, 9:00 AM | Reported window 20–28 Jan, so check [jeemain.nta.nic.in](https://jeemain.nta.nic.in) for your exact date |
| CBSE Class 12 Boards 2027 | 16 Feb 2027, 10:30 AM | Date sheet not released, estimate is mid-Feb ([cbse.gov.in](https://www.cbse.gov.in)) |
| JEE Advanced 2027 | 16 May 2027, 9:00 AM | Not announced yet, usually mid/late May ([jeeadv.ac.in](https://jeeadv.ac.in)) |

Once your JEE Main admit card shows your exact day, set that date so the countdown is exact.

## Option A: Rainmeter (Windows, recommended)

1. Install Rainmeter from https://www.rainmeter.net/.
2. Copy the `rainmeter/ExamCountdown` folder into `Documents\Rainmeter\Skins\`.
3. Right-click the Rainmeter icon in the system tray, then **Refresh all**.
4. Open **Manage**, choose `ExamCountdown > ExamCountdown.ini`, and click **Load**.
5. Drag it where you want it. Right-click, then Settings, to lock its position, set "Click through", etc.

**Change a date:** right-click the widget, **Edit skin**, change the `ExamXDate=` lines under `[Variables]`, save, then right-click and **Refresh skin**.
Rainmeter already starts with Windows, so the widget will be back after every restart.

## Option B: Python widget (any OS)

Run it:

```bash
python exam_countdown.pyw
```

(On Windows you can just double-click `exam_countdown.pyw`.)

- **Move it:** drag with the left mouse button. The position is remembered.
- **Menu:** right-click for *Always on top*, *Reload dates*, *Edit dates…* and *Quit*.
- **Change dates:** edit `exams.json` (24-hour time, IST), then right-click and choose **Reload dates**. Set `"confirmed": true` to drop the "(tentative)" label.

**Start automatically on Windows:** double-click `install_windows_startup.bat`. To undo, press `Win+R`, type `shell:startup` and delete "Exam Countdown".

**Start automatically on macOS:** open *Automator*, make a new *Application* with a *Run Shell Script* step `python3 /full/path/to/exam_countdown.pyw`, save it, then add it under *System Settings, General, Login Items*.
