# Tree Rings Counter

> AI-powered cross-platform app (iOS, Android, Web) that estimates a tree's age from a photo of its cut cross-section.

---

## How it works

1. Point your phone camera at a freshly cut tree stump
2. The app sends the photo to the backend
3. An AI model counts the visible annual rings
4. You get an age estimate with confidence score and ring visualization

---

## Stack

| Layer | Technology |
|---|---|
| Mobile / Web | React Native + Expo SDK 53 (Expo Router v4), TypeScript |
| Styling | NativeWind v4 (Tailwind CSS v3) |
| Backend | FastAPI (Python 3.12) |
| AI — Phase 1 | Gemini 2.5 Flash (primary) + GPT-4o (fallback) |
| AI — Phase 2 | Fine-tuned YOLO26-seg |
| Mobile builds | Expo EAS Build |
| Web hosting | Vercel |
| Backend hosting | Render |

---

## Project structure

```
tree-rings-counter/
├── app/          # Expo app (iOS + Android + Web)
└── backend/      # FastAPI backend + ML pipeline
```

---

## Getting started

Follow these steps to run the project locally. You will need to run both the backend server and the frontend app simultaneously in two separate terminal windows.

### 1. Backend Setup

The backend is built with Python and FastAPI. It handles the image processing and communicates with the Gemini AI model.

1. Open a new terminal in Cursor
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Set up your environment variables:
   ```bash
   # Copy the example file to create your own .env file
   cp .env.example .env
   ```
   *Note: Open `backend/.env` and replace `your_gemini_api_key_here` with your actual Gemini API key.*
4. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
5. Start the backend server:
   ```bash
   uvicorn main:app --reload
   ```

The backend is now running! You can view the API documentation at http://localhost:8000/docs. Leave this terminal running.

### 2. Frontend Setup (Expo)

The frontend is built with React Native and Expo. It can run on the web, iOS, and Android.

1. Open a **second** terminal window in Cursor (click the `+` icon in the terminal panel)
2. Navigate to the app directory:
   ```bash
   cd app
   ```
3. Install the Node.js dependencies:
   ```bash
   npm install
   ```
4. Start the Expo development server:
   ```bash
   npx expo start
   ```

**How to view the app:**
- **Web (Desktop):** Press `w` in the terminal to open the app in your web browser.
- **Mobile (iOS/Android):** Download the **Expo Go** app on your phone and scan the QR code shown in the terminal.

*Note: The frontend is configured to automatically connect to your local backend at `http://localhost:8000` by default.*

### 3. Mobile builds (EAS)

```bash
cd app
npm install -g eas-cli
eas login
eas build --platform ios --profile preview
eas build --platform android --profile preview
```

---

## AI phases

### Phase 1 — LLM Vision (current)
Uses Gemini 2.5 Flash with GPT-4o fallback. No training data required.
Set `GEMINI_API_KEY` and optionally `OPENAI_API_KEY` in `backend/.env`.

### Phase 2 — YOLO26-seg (custom model)
1. Collect annotated phone-camera tree ring photos
2. Convert Poláček et al. dataset: `python backend/ml/training/convert_polacek_to_yolo.py`
3. Train: `python backend/ml/training/train_yolo26.py`
4. Set `USE_YOLO=true` and `YOLO_WEIGHTS_PATH=ml/weights/...` in `.env`

---

## Research reference

Poláček et al. (2023) — *Automation of tree-ring detection and measurements using deep learning*. Methods in Ecology and Evolution.
- GitHub: https://github.com/Gregor-Mendel-Institute/TRG-ImageProcessing
- Dataset: https://zenodo.org/record/8428752
