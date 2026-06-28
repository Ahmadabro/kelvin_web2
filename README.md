# kelvin_web2
# 🔬 ThermoAI — Advanced Thermodynamics Intelligence

ThermoAI is an immersive, full-screen interactive web application built as a university project to assist students and researchers in breaking down complex thermodynamic systems. Powered by the high-cognitive intelligence of xAI's Grok engine, the platform transforms abstract physical concepts, complex cyclic pathways, and dense calculations into structured, step-by-step documentation.

## 🚀 Key Features

- **Immersive Full-Screen UI:** Engineered with a glassmorphic layout, fluid atmospheric backgrounds, and responsive typography optimized for desktop learning environments.
- **Step-by-Step System Analysis:** Dynamically tracks boundary conditions, state variable shifts ($P, V, T, S, H, U$), and equation manipulations without just dumping a final answer.
- **Comprehensive Cycle Optimization:** In-depth, physical intuition-first analysis of classic thermodynamic cycles (Carnot, Rankine, Otto, Diesel, and Brayton).
- **Secure Serverless Architecture:** Utilizes Vercel Serverless Functions (Python backend) to shield internal API keys from public exposures while handling high-throughput asynchronous communication safely.
- **Dynamic Markdown Rendering:** Seamlessly renders LaTeX formulas, logical flow lists, and syntax-highlighted script snippets natively inside the chat interface.

## 🛠️ Tech Stack

- **Frontend:** HTML5, Advanced CSS3 (Custom viewports & variables, cubic-bezier spring physics animations), Modern Vanilla JS (ES6 Async/Fetch API).
- **Backend:** Python 3 (Native Serverless Architecture via Vercel Runtime `BaseHTTPRequestHandler`).
- **AI Core:** xAI Grok Engine API (`grok-beta` implementation).
- **Libraries Used:** [Marked.js](https://marked.js.org/) (Client-side Markdown processing via secure CDN).

## 📂 Project Structure

```text
├── api/
│   └── chat.py       # Vercel Serverless Python function (Backend API middleware)
├── index.html        # Clean, semantic structure with background atmosphere objects
├── style.css         # Immersive full-viewport layout & interface elements
├── script.js        # Event tracking, dynamic UI updates & markdown rendering handlers
└── requirements.txt  # Python build configuration for deployment environments
