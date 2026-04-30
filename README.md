# LinkedIn Post Studio — Setup Guide

## Quick Start (Local / API Key)

1. Copy `.env.example` to `.env` and add your `GOOGLE_API_KEY`
2. `pip install -r requirements.txt`
3. `streamlit run main.py`

---

## Fixing Availability in India (and other regions)

Google AI Studio's free API (`generativelanguage.googleapis.com`) is **geo-blocked in India**.
The solution is to route through **Vertex AI** — same Gemini models, served from Google Cloud
infrastructure which is globally available.

### Steps

1. **Create a Google Cloud project** at https://console.cloud.google.com
2. **Enable the Vertex AI API** for your project
3. **Install the gcloud CLI** and authenticate:
   ```bash
   gcloud auth application-default login
   ```
4. **Update your `.env`**:
   ```
   USE_VERTEX=true
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_LOCATION=us-central1
   ```
5. On Render, add these as **Environment Variables** in your service settings.
   For auth, use a **Service Account key** and set `GOOGLE_APPLICATION_CREDENTIALS`
   to the path of the JSON key file, or paste the key contents into a secret.

### Cost

Vertex AI Gemini has a free tier (60 QPM for Flash models). Image generation
(Imagen) requires billing to be enabled but costs fractions of a cent per image.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | Local dev only | API key from Google AI Studio |
| `USE_VERTEX` | For India/prod | Set to `true` to use Vertex AI |
| `GOOGLE_CLOUD_PROJECT` | If USE_VERTEX=true | Your GCP project ID |
| `GOOGLE_CLOUD_LOCATION` | If USE_VERTEX=true | Region, e.g. `us-central1` |

---

## Adding New Posts to the Database

Place your raw posts JSON at `data/raw/raw_posts.json` in this format:

```json
[
  { "text": "Your LinkedIn post text here..." },
  { "text": "Another post..." }
]
```

Then run:
```bash
python preprocess.py
```

This re-processes all posts and rebuilds the database. It respects free-tier
rate limits automatically (4.5s delay between calls).