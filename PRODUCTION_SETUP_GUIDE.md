# 🚀 Production Setup Guide - CV Updater

## 📋 **Your Deployed URLs**
- **Frontend**: https://cv-updater-dwj2.vercel.app
- **Backend**: https://cv-updater-backend-version1.onrender.com

## ✅ **Current Configuration Status**

### **Frontend Configuration** ✅
- **File**: `frontend/.env`
- **API URL**: `REACT_APP_API_URL=https://cv-updater-backend-version1.onrender.com`
- **Status**: ✅ Correctly configured

### **Backend Configuration** ✅
- **File**: `backend/.env`
- **CORS Origins**: `CORS_ORIGINS=https://cv-updater-dwj2.vercel.app,http://localhost:3000,http://127.0.0.1:3000`
- **Status**: ✅ Correctly configured

## 🔧 **Deployment Platform Setup**

### **1. Vercel (Frontend) Setup**

#### **Environment Variables in Vercel Dashboard:**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Select your project: `cv-updater-dwj2`
3. Go to **Settings** → **Environment Variables**
4. Add/Update these variables:

```
REACT_APP_API_URL=https://cv-updater-backend-version1.onrender.com
REACT_APP_SUPABASE_URL=your_supabase_url_here
REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

#### **Vercel Configuration File:**
- **File**: `vercel.json` ✅ Already configured correctly

### **2. Render (Backend) Setup**

#### **Environment Variables in Render Dashboard:**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select your service: `cv-updater-backend-version1`
3. Go to **Environment** tab
4. Add/Update these variables:

```
CORS_ORIGINS=https://cv-updater-dwj2.vercel.app,http://localhost:3000,http://127.0.0.1:3000
VITE_OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
SUPABASE_DB_URL=your_supabase_db_url_here
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key_here
```

#### **Render Configuration File:**
- **File**: `railway.json` ✅ Already configured correctly

## 🚀 **Deployment Steps**

### **Step 1: Update Environment Variables**
1. **Vercel**: Update environment variables in dashboard
2. **Render**: Update environment variables in dashboard

### **Step 2: Push Code Changes**
```bash
# Commit your current changes
git add .
git commit -m "Configure production URLs and CORS settings"
git push origin main
```

### **Step 3: Verify Deployment**
1. **Frontend**: https://cv-updater-dwj2.vercel.app
2. **Backend**: https://cv-updater-backend-version1.onrender.com/test

## 🔍 **Testing Your Setup**

### **1. Test Backend API**
```bash
curl https://cv-updater-backend-version1.onrender.com/test
```
**Expected Response**: `{"status": "Backend is running!"}`

### **2. Test Frontend-Backend Communication**
1. Open https://cv-updater-dwj2.vercel.app
2. Try to upload a CV
3. Check browser console for any CORS errors

### **3. Test Complete Flow**
1. **Sign up/Login** at frontend
2. **Upload CV** (PDF/TXT/DOCX)
3. **Chat with AI** to update CV
4. **Download** enhanced CV

## 🛠️ **Troubleshooting**

### **Common Issues:**

#### **1. CORS Errors**
- **Symptom**: Browser console shows CORS errors
- **Solution**: Verify `CORS_ORIGINS` in Render includes your Vercel URL

#### **2. API Connection Errors**
- **Symptom**: Frontend can't connect to backend
- **Solution**: Check `REACT_APP_API_URL` in Vercel environment variables

#### **3. Environment Variables Not Loading**
- **Symptom**: App uses localhost instead of production URLs
- **Solution**: Rebuild and redeploy after updating environment variables

### **Debug Commands:**
```bash
# Test backend health
curl https://cv-updater-backend-version1.onrender.com/test

# Check frontend build
npm run build

# Check environment variables
echo $REACT_APP_API_URL
```

## 📱 **Local Development vs Production**

### **Local Development:**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8081`
- Use local `.env` files

### **Production:**
- Frontend: `https://cv-updater-dwj2.vercel.app`
- Backend: `https://cv-updater-backend-version1.onrender.com`
- Use platform environment variables

## ✅ **Final Checklist**

- [ ] Vercel environment variables updated
- [ ] Render environment variables updated
- [ ] Code changes committed and pushed
- [ ] Backend API responding at `/test` endpoint
- [ ] Frontend loading without errors
- [ ] CORS errors resolved
- [ ] Complete user flow working (upload → chat → download)

## 🎉 **Success Indicators**

When everything is working correctly:
1. ✅ Frontend loads at https://cv-updater-dwj2.vercel.app
2. ✅ Backend responds at https://cv-updater-backend-version1.onrender.com/test
3. ✅ No CORS errors in browser console
4. ✅ Users can upload CVs and chat with AI
5. ✅ Users can download enhanced CVs

Your application is now fully configured for production! 🚀 