# GestureVault — Secret Gesture Lock

A mobile-friendly MSc Computer Science cybersecurity demonstration. It combines browser camera access, MediaPipe hand-landmark recognition, a configurable gesture sequence, a Python/Flask event API, local SQLite audit logs, optional failed-attempt snapshots, and a small FAR/FRR experiment panel.

> **Prototype only:** this is not production-grade authentication. The gesture classifier is heuristic, the demo has no user accounts, the reset endpoint is unauthenticated, and stored photos/logs are not encrypted. Bind to localhost for demos. Do not expose this server to the public internet or use it to protect real accounts.

## Features

- Responsive dark dashboard for desktop and mobile.
- Camera-based gesture detection using MediaPipe Tasks Vision in the browser.
- Default sequence: three fingers → fist → open palm. Edit it from the UI; the sequence is stored in the current browser's local storage.
- ACCESS GRANTED / ACCESS DENIED states, sound alerts, and a three-failure session alert.
- Failed attempt snapshot saved to `data/intruder_photos/` when available, and local SQLite event log.
- Security lab to record experimental outcomes and calculate observed FAR/FRR.

## Requirements

- Python 3.10+ recommended.
- A modern Chrome/Edge browser.
- Camera permission.
- Internet connection on first load for the MediaPipe JavaScript library and hand-landmark model (the app itself is served locally).

## Run on Windows

1. Extract the ZIP.
2. Open the extracted `secret-gesture-lock` folder.
3. In the address bar of File Explorer type `cmd` and press Enter.
4. Run:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install -r requirements.txt
   py app.py
   ```

5. Open `http://127.0.0.1:5000` in Chrome or Edge and allow camera permission.
6. Press **Enable camera**, then **Start authentication**. Hold each gesture steady for around one second and change gestures clearly.

If `py` is unavailable, try `python` in place of `py`. Keep the terminal open while using the app.

## Run on Android

For a same-phone demo, deploy the Flask backend to a Python host that supports persistent storage, then open the HTTPS URL in Chrome and grant camera permission. The frontend uses the same-origin `/api` endpoints. Some free hosting tiers sleep or use ephemeral storage, so SQLite records and photos may be lost on restart. GitHub Pages alone cannot host the Python backend. Do not deploy the current unauthenticated prototype publicly without hardening it.

A local-network demo from a PC may also work if the phone can reach the PC and the page is served in a browser context that permits camera access. Plain HTTP over a LAN IP is commonly blocked for camera APIs; HTTPS hosting is the simpler option.

## Project structure

```text
secret-gesture-lock/
├── app.py                 # Flask API, SQLite events, snapshot storage
├── requirements.txt
├── README.md
├── templates/
│   └── index.html         # App views and accessible controls
├── static/
│   ├── style.css          # Responsive interface
│   └── app.js             # MediaPipe vision + gesture sequence logic
└── data/                  # Created at runtime; logs and photos
```

## Gesture classifier notes

The demo uses a simple landmark heuristic that estimates extended fingers from fingertip and joint positions. It can confuse gestures due to camera angle, mirrored view, lighting, left/right hand orientation, and partial occlusion. For a serious study, collect labelled samples, define a test protocol, and report confidence intervals alongside FAR/FRR.

## FAR and FRR experiment

The lab panel lets you manually record a trial's expected class and observed result. It computes:

- `FAR = false accepts / total unauthorized trials × 100`
- `FRR = false rejects / total legitimate trials × 100`

These metrics depend on the quality and representativeness of the test dataset. Manually entering outcomes does not automatically benchmark the recognizer.

## Privacy and safety

- Camera frames are processed in the browser; frames are not continuously uploaded.
- On a denied attempt, the current video frame is sent to the Flask server for local snapshot storage.
- Tell demo participants before capturing their image and delete demo photos when finished.
- Do not use the sample reset endpoint on a public deployment; it clears all event rows and saved snapshots.
