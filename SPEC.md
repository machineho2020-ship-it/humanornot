# HumanOrNot — Product Specification

## 1. Concept & Vision

HumanOrNot is a free-to-use web tool that detects whether content was written by a human or an AI. Text detection powered by Hugging Face's RoBERTa-based OpenAI detector model. Image detection (PRO) powered by AI-generated image detection models on Hugging Face.

Free users get 10 checks per day. PRO tier removes the daily limit and unlocks image upload detection.

---

## 2. Design Language

- **Aesthetic:** Dark, modern, sharp. Think builder tools like Vercel or Linear — dark backgrounds, neon accent gradients, tight spacing.
- **Color palette:**
  - Background: `#0d0d0f`
  - Surface: `#16161a`
  - Border: `#2a2a35`
  - Text: `#f0f0f5`
  - Muted: `#6b6b80`
  - Accent (gradient): `#ff6b6b` → `#feca57`
  - Human green: `#00b894`
  - AI orange: `#e17055`
  - PRO badge border: `#feca57`
- **Typography:** Inter / system-ui, clean and readable
- **Spatial system:** Mobile-first, max-width 640px container, 16px base padding
- **Motion:** Spinner loader, bar-fill transitions (0.8s ease), button press scale (0.98)

---

## 3. Layout & Structure

- **Hero:** Centered title with PRO badge, tagline, gradient text title
- **Mode toggle:** Text vs Image tab switcher
- **Text panel:** Textarea + character counter + CTA button
- **Image panel:** Drag-and-drop upload area + preview + CTA button
- **Results:** Full-width verdict card + score bars + confidence + remaining count
- **Footer:** Hugging Face credit + Upgrade link

---

## 4. Features & Interactions

### Core Features

#### Text Detection
- POST `/detect` with `{text}` JSON body
- Minimum 50 characters enforced client + server side
- Returns: `ai_pct`, `human_pct`, `verdict`, `confidence`, `status`, `remaining`
- Rate limited: 10 checks/IP/day (in-memory, resets at midnight UTC)

#### Image Detection (PRO)
- POST `/detect/image` with multipart/form-data file upload
- Accepts: JPG, PNG, GIF, WEBP (max ~5MB)
- Returns same structure as text detection
- Requires `HF_IMAGE_API_URL` env var (not yet configured — returns 501)

#### Rate Limiting
- In-memory dict keyed by client IP
- Tracks timestamps per IP, expires after 24h
- Returns HTTP 429 with JSON error + upgrade link when exhausted
- PRO users bypass via separate logic (future: cookie/session)

#### /status Endpoint
- Returns `{"status": "ok", "version": "1.0"}`
- Used for uptime monitoring

#### /upgrade Route
- Redirects to LemonSqueezy checkout URL
- Configurable via `LEMONSQUEEZY_URL` env var

### Error States
- No text / too short → 400 with specific message
- Rate limit hit → 429 with upgrade prompt (PRO badge styling)
- API timeout → 504
- Unknown → 500

### Interactions
- Mode toggle switches between text/image panels
- Drag-and-drop on upload area
- File input auto-shows image preview
- Result verdict color-coded: green (human) / orange (AI)
- PRO badge shown in hero always (placeholder for future gating)

---

## 5. Component Inventory

### Hero Badge
- "PRO" pill badge, yellow border, dark background

### Textarea
- Dark surface, subtle border, glow on focus
- Placeholder text in muted color
- Live character counter

### Upload Area
- Dashed border, drag-over highlight state
- Hidden file input triggered by click
- Preview `<img>` shown after file selected

### Detect Buttons
- Full-width, gradient background, disabled state (dimmed)

### Score Bars
- Background track + colored fill bar (human=green, AI=orange)
- Percentage labels left/right

### Verdict Card
- States: human (green gradient), AI (orange gradient), error (dark with red text), pro-upgrade (dark + yellow border)

---

## 6. Technical Approach

### Stack
- **Backend:** Flask (Python)
- **Frontend:** Vanilla JS, HTML, CSS (no framework)
- **Deployment:** Render (free tier) + Gunicorn
- **APIs:** Hugging Face Inference API (free tier, rate-limited)

### Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Render index.html |
| GET | `/status` | Health check + version |
| GET | `/upgrade` | Redirect to LemonSqueezy |
| POST | `/detect` | Text AI detection |
| POST | `/detect/image` | Image AI detection |

### Environment Variables
| Variable | Description |
|----------|-------------|
| `HF_API_KEY` | Hugging Face API token (required for text detection) |
| `HF_IMAGE_API_URL` | Hugging Face image detection model URL (optional, PRO feature) |
| `LEMONSQUEEZY_URL` | LemonSqueezy checkout URL (PRO upgrade link) |
| `PORT` | Flask port (Render sets this automatically) |

### Rate Limit Logic
- In-memory `defaultdict(list)` keyed by client IP
- Client IP extracted from `X-Forwarded-For` or `request.remote_addr`
- Timestamps stored as UTC `datetime` objects
- Window: 24 hours (midnight UTC reset not enforced — sliding window)
- Max 10 entries per IP before 429 response

### File Structure
```
humanornot/
├── app.py              # Flask backend (all routes + logic)
├── templates/
│   └── index.html      # Full frontend (HTML + CSS + JS)
├── requirements.txt    # flask, requests, gunicorn
├── DEPLOY.md           # Deployment guide
├── SPEC.md             # This file
└── README.md           # User-facing overview
```

---

## 7. Future PRO Features (Out of Scope)

- User accounts / auth
- Persistent rate limit storage (Redis/DB)
- Actual LemonSqueezy integration (webhook + access control)
- Real image detection API integration
- Custom branding / whitelabel
- Usage analytics dashboard
