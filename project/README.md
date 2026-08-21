# Left Eye Mouse

Move the Windows mouse pointer by looking around with your left eye. The webcam feed stays visible so you can confirm that the iris is being detected.

## Setup

Use Python 3.10-3.13 for the easiest MediaPipe installation on Windows. From this folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

Look toward the edges of the screen to move the pointer. Press `P` in the camera window to pause/resume, `Q` or `Esc` to quit, or move the mouse quickly to a screen corner to trigger PyAutoGUI's emergency stop.

If the default camera is unavailable, select another device with `python main.py --camera 1`. Adjust cursor smoothing with `--smoothing 0.1` through `--smoothing 1.0`.

## GitHub

The `.gitignore` excludes the virtual environment, Python caches, and local files. No webcam frames are saved by this program.

On the first run, the MediaPipe face-landmark model is downloaded into `models/` automatically. It is ignored by Git because it is generated locally and can be downloaded again during setup.
