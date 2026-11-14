# DEPLOYMENT GUIDE

**Analog Finder** is a 100% client-side static web application requiring **zero backend servers, zero databases, and zero paid API keys**. It can be deployed in under 2 minutes to Vercel, GitHub Pages, or Netlify.

---

## ⚡ Option 1: Deploy to Vercel (Recommended, 1-Click)

### Via Vercel Web Dashboard:
1. Push this repository to your GitHub account.
2. Log in to [Vercel](https://vercel.com/) and click **"Add New Project"**.
3. Import your `Analog-Finder` repository.
4. Set the following project settings:
   - **Root Directory:** `web`
   - **Framework Preset:** `Vite`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
5. Click **Deploy**. Vercel will build and host the site globally on edge CDN in ~30 seconds.

### Via Vercel CLI:
```bash
npm install -g vercel
cd web
vercel
```

---

## 🌐 Option 2: Deploy to GitHub Pages

### Automatic Deployment via GitHub Actions:
A GitHub Actions workflow is provided in [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

1. In your GitHub repository, navigate to **Settings** > **Pages**.
2. Under **Build and deployment** > **Source**, select **GitHub Actions**.
3. Push any commit to the `main` branch:
   ```bash
   git add .
   git commit -m "Deploy Analog Finder"
   git push origin main
   ```
4. GitHub Actions will automatically build `web/` and deploy `web/dist` to `https://<username>.github.io/<repo>/`.

---

## 💻 Option 3: Local Testing / Development

To run the application locally on Windows, macOS, or Linux:

```bash
# 1. Navigate to the web folder
cd web

# 2. Install dependencies (Node 20+)
npm install

# 3. Start local development server
npm run dev

# 4. Or build and preview production bundle
npm run build
npm run preview
```

Open your browser to `http://localhost:5173/`.

---

## 📦 Static Payload Verification
- **Total payload size:** 3.09 MB (well below the 50 MB budget limit).
- **Largest raster overlay:** 916.8 KB (well below the 10 MB per overlay limit).
- **Initial page load time:** $< 1.2\text{ seconds}$ on standard 4G/broadband.
