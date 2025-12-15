# Quick Deployment Guide

## 🚀 Recommended: Deploy Together (Easiest)

Your project is **already configured** to deploy both frontend and backend together!

### Steps:

1. **Go to Vercel:** https://vercel.com/dashboard
2. **Click "Add New Project"**
3. **Import GitHub repo:** `sabasiddique1/emergency_care_navigator`
4. **Set Environment Variables:**
   ```
   JWT_SECRET_KEY=<generate-with-command-below>
   GEMINI_API_KEY=<your-key-optional>
   ```
5. **Click "Deploy"**

### Generate JWT Secret:
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### That's it! ✅

Your app will be live at: `https://your-project.vercel.app`
- Frontend: `https://your-project.vercel.app`
- API: `https://your-project.vercel.app/api/health`

---

## 📋 For Separate Deployment

See `docs/DEPLOYMENT_OPTIONS.md` for detailed instructions.

**Quick Summary:**
1. Create 2 Vercel projects (backend + frontend)
2. Backend: Use root directory, deploy `api/app.py`
3. Frontend: Use `frontend/` directory, set `NEXT_PUBLIC_API_URL` env var
4. Update CORS in backend to allow frontend domain

---

## ✅ Current Status

- ✅ `vercel.json` configured
- ✅ `api/app.py` entrypoint ready
- ✅ `pyproject.toml` fixed
- ✅ Frontend API client supports both modes
- ✅ CORS configured (allows all origins)

**Ready to deploy!**

