# 🌲 Tree Rings Counter – Estimate a Tree’s Age Using AI

> AI-powered web app that estimates the age of a tree based on a photo of its cross-section (tree rings).

---

## 📸 Demo

![screenshot](./assets/demo.png)

Try it live: [treerings.karaulanov.com](https://demo-link.com) *(optional)*

---

## 🧠 What It Does

Upload a photo of a cut tree’s cross-section. The app:
- Detects visible rings using a trained AI model
- Estimates the age based on the number of rings
- Visualizes the result with overlays and confidence scores

---

## 🏗️ Tech Stack

| Layer        | Tech                          |
|--------------|-------------------------------|
| Frontend     | React, TypeScript, TailwindCSS |
| Backend      | FastAPI (Python), Docker       |
| AI/ML        | PyTorch, OpenCV, CNN (U-Net)   |
| Deployment   | Azure App Service, Vercel      |

---

## 🚀 Getting Started

### Frontend
```bash
cd frontend
npm install
npm run dev
