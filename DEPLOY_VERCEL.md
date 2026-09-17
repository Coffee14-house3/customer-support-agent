# Deploying to Vercel Guide

This repository is pre-configured for **1-click deployment on Vercel** with full support for:
- **Vite React Frontend**: Automatically built into static assets with edge CDN caching.
- **Serverless API Routes (`/api/*`)**: Handled via `api/index.ts` and `vercel.json`.
- **Zero Python Runtime Dependency**: The retrieval and agent pipeline includes a high-speed, pure TypeScript in-memory vector store that runs natively in Vercel's serverless environment with sub-millisecond retrieval.

---

## Method 1: Deploy via GitHub & Vercel Dashboard (Recommended)

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Deploy AI Customer Support Agent to Vercel"
   git push origin main
   ```

2. **Open Vercel Dashboard**:
   - Go to [vercel.com](https://vercel.com) and log in.
   - Click **"Add New"** $\rightarrow$ **"Project"**.
   - Select your GitHub repository.

3. **Configure Project Settings**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `./` (leave default)
   - **Build Command**: `vite build` (or leave default)
   - **Output Directory**: `dist` (or leave default)

4. **Add Environment Variables (Optional)**:
   In Vercel's **Environment Variables** section, add your model API keys if you wish to use remote LLM synthesis:
   - `GROQ_API_KEY`: *(Optional)* Your Groq API key (for ultra-fast LLaMA-3.3 inference).
   - `OPENROUTER_API_KEY`: *(Optional)* Your OpenRouter API key.
   *(Note: If no API key is supplied, the agent automatically runs the deterministic grounded policy synthesizer, ensuring 100% uptime with zero hallucinations).*

5. **Click "Deploy"**:
   Vercel will build the frontend and provision the serverless API routes. Your app will be live with a free `.vercel.app` URL!

---

## Method 2: Deploy via Vercel CLI

If you have Node.js and the Vercel CLI installed:

1. In the project directory, run:
   ```bash
   npx vercel
   ```
2. Follow the prompts:
   - `Set up and deploy?` **Y**
   - `Which scope?` *(Select your personal account)*
   - `Link to existing project?` **N**
   - `Project name?` *(Press Enter or type a custom name)*
   - `In which directory is your code located?` `./`
3. For production deployment:
   ```bash
   npx vercel --prod
   ```

---

## Configuration Files Included

* **`vercel.json`**: Configures Vercel to route `/api/*` requests to the serverless function in `api/index.ts` and static routes to `dist/index.html`.
* **`api/index.ts`**: The serverless Express entrypoint providing `/api/chat`, `/api/metrics`, `/api/knowledge-base`, and `/api/golden-set`.
* **`server/agentEngine.ts`**: The pure-TypeScript grounded RAG engine and in-memory vector index, guaranteeing zero runtime crashes in serverless Lambda environments.
