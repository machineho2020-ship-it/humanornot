# HumanOrNot — Deploy to Render

## Step 1: Create GitHub Repo
1. Go to [github.com](https://github.com) → New repo → name it `humanornot`
2. Push the code:
```bash
cd /Users/mac/humanornot
git remote add origin https://github.com/YOUR_USERNAME/humanornot.git
git push -u origin main
```

## Step 2: Deploy on Render (Free)
1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **"New +"** → **"Web Service"**
3. Connect your `humanornot` repo
4. Settings:
   - **Name:** `humanornot`
   - **Region:** Singapore (or closest to you)
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free

5. **Environment Variables** → Add:
   - `HF_API_KEY` = your Hugging Face API key (free at huggingface.co/settings/tokens)

## Step 3: Get Hugging Face API Key
1. Go to [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
2. Create new token → copy it
3. Paste into Render environment variable

## Step 4: Deploy
- Click **"Create Web Service"**
- Wait ~3-5 minutes for deployment
- Your app will be live at: `https://humanornot.onrender.com`

## Cost
- **Render:** Free (good for testing)
- **Hugging Face API:** Free tier (500 requests/month on roberta-base-openai-detector)
- **Domain:** Use the free `.onrender.com` subdomain

## Upgrade Path
When you get paying users → upgrade Render to paid plan ($7/mo) for better performance.
