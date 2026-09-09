# AI-DisasterGuard — Citizen Mobile Web App

## How to Deploy to Vercel (Easiest Way):
1. Go to https://vercel.com/new
2. Either drag-and-drop this extracted folder OR push it to a new GitHub repo.
3. Settings:
   - Framework: Vite
   - Build Command: npm run build
   - Output Directory: dist
4. Environment Variables:
   - VITE_API_URL: https://<YOUR-RENDER-BACKEND-URL>
   - VITE_WS_URL: wss://<YOUR-RENDER-BACKEND-URL>/api/v1/ws
5. Click Deploy!
