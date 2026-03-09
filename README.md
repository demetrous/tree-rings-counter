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

### 1. Backend

```bash
cd backend
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY and/or OPENAI_API_KEY

pip install -r requirements.txt
uvicorn main:app --reload
```

API docs available at http://localhost:8000/docs

### 2. Frontend (Expo)

```bash
cd app
npm install
npx expo start
```

- Press `w` to open in browser
- Scan the QR code with Expo Go for iOS/Android
- Set `EXPO_PUBLIC_API_URL` in a `.env.local` file to point at your backend

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
