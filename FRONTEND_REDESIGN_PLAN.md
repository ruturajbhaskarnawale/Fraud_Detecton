# Frontend Redesign Plan: KYC Identity Verification System

## 1. Vision & Goals
Transform the current KYC utility into a premium, multi-page SaaS application. The goal is to build trust through professional design, provide clarity through guided workflows, and offer depth through detailed data visualization.

---

## 2. Updated Page Architecture

| Route | Page | Purpose |
| :--- | :--- | :--- |
| `/` | **Landing Page** | Conversion-focused entry point. Explains OCR, Face Match, and Fraud Detection. |
| `/verify` | **Verification Lab** | The core tool. Step-by-step guided upload process. |
| `/results/[id]` | **Insight Report** | Deep-dive into verification results with confidence scores and fraud signals. |
| `/history` | **Audit Logs** | Management view of all past verifications with advanced filtering. |
| `/dashboard` | **Security Metrics** | High-level analytics: Fraud trends, throughput, and system health. |
| `/docs` | **System Overview** | Educational content on how the AI pipeline (OCR, Face, Fraud) works. |

---

## 3. New Folder Structure (Refactored)
We will move to a more scalable `src/` based structure:
```text
src/
  app/              # Next.js App Router (Pages & Layouts)
    (marketing)/    # Landing, About, Docs (Shared layout)
    (dashboard)/    # Dashboard, History, Results (Sidebar layout)
    (auth)/         # Login/Signup (Future)
  components/
    ui/             # Atomic components (Buttons, Inputs, Cards)
    verification/   # Flow-specific components (Dropzone, Progress)
    charts/         # Dashboard visualizations
    layout/         # Navbar, Footer, Sidebar
  hooks/            # Custom React hooks (useVerification, useLocalStorage)
  services/         # API Layer (api.ts)
  lib/              # Utility functions (shadcn/utils)
  store/            # Global state (if needed, otherwise context)
  types/            # TypeScript interfaces
```

---

## 4. Visual System (Design Tokens)

### Color Palette
- **Primary**: `#3B82F6` (Electric Blue) - Action-oriented, trust-building.
- **Surface**: `#FFFFFF` (Light) / `#0F172A` (Dark) - Clean SaaS aesthetic.
- **Success**: `#10B981` (Emerald) - For valid documents.
- **Alert**: `#F59E0B` (Amber) - For suspicious signals.
- **Critical**: `#EF4444` (Rose) - For rejected/fraudulent uploads.

### Typography
- **Headings**: `Outfit` or `Inter` (Bold/Black) - Modern, tech-forward.
- **Body**: `Inter` (Medium/Regular) - High legibility.

---

## 5. Core Components Breakdown

1. **`LandingHero`**: Large typography, animated security shield, CTA.
2. **`VerificationStepper`**: Multi-state progress indicator (Upload -> OCR -> Match -> Fraud -> Result).
3. **`MetricTile`**: Compact card showing "98.5% Accuracy" or "Avg 2.4s Latency".
4. **`FraudSignalList`**: A list of signals (e.g., "Text manipulation detected", "Font mismatch") with color-coded severity.
5. **`RealTimeConsole`**: A small log-like component showing the AI pipeline's current activity (e.g., "Extracting text from Aadhaar...").

---

## 6. Interaction Design (UX Enhancement)

- **Micro-Animations**: Subtle entrance animations for cards using Framer Motion.
- **Skeleton Loaders**: Dedicated skeleton states for the results page to prevent layout shift.
- **Drag & Drop**: Enhanced visual feedback when hovering files over the dropzone.
- **Real-time API Polling**: If the backend becomes long-running, we will implement a polling or WebSocket strategy for the "Processing" state.

---

## 7. Implementation Roadmap

### Step 1: Foundation (Current Session)
- [ ] Initialize `src/` directory refactor.
- [ ] Set up global CSS with Tailwind 4 design tokens.
- [ ] Create base Layouts (Marketing vs. Dashboard).

### Step 2: The Landing Experience
- [ ] Build the Landing Page (`/`).
- [ ] Create the "How it Works" visual guide.

### Step 3: Refactored Verification Flow
- [ ] Move current home page logic to `/verify`.
- [ ] Enhance File Upload with real-time feedback.
- [ ] Implement the new `VerificationStepper`.

### Step 4: Results & History
- [ ] Create `/results/[tracking_id]` with full data visualization.
- [ ] Upgrade `/history` with search and status filtering.

### Step 5: Dashboard & Docs
- [ ] Build the `/dashboard` with mock metrics (to be backed by `/records` API).
- [ ] Add the `/docs` page.

---

## 8. Wireframe Previews (Text-based)

### Landing Page
```text
[ Navbar: Home | Verify | History | Dashboard ]
------------------------------------------------
[   (Icon: Shield) AI-Powered Identity         ]
[   The most advanced KYC fraud detection      ]
[   platform for modern startups.              ]
[            [ Start Verification ]            ]
------------------------------------------------
[ How it Works: 1. Upload -> 2. AI Scan -> 3. Result ]
```

### Results Page
```text
[ Verification Success: RUTURAJ B. ]  [ SCORE: 98/100 ]
-------------------------------------------------------
[ Photo extracted ] [ OCR Details:       ] [ Signals: ]
[       ID        ] [ Name: Ruturaj...   ] [ [v] Font ]
[      Face       ] [ DOB: 12-01-...     ] [ [v] Face ]
```
