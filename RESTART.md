# 🔄 Quick Restart Guide

## To Test the PDF Upload Fix:

### 1. Stop Current Servers
- Close any open terminal windows running the app
- Or press `Ctrl+C` in the terminals to stop servers

### 2. Restart Application
Double-click `start_all.bat` or run:
```bash
# Terminal 1 (Backend)
cd backend
python main_enhanced.py

# Terminal 2 (Frontend)  
cd frontend
npm start
```

### 3. Test PDF Upload
1. Go to http://localhost:3000
2. Sign in with your account
3. Upload your PDF file again
4. **Check browser console (F12)** for PDF extraction logs
5. You should now see the full CV content on the right panel

### 4. What to Look For:
- ✅ "Full Content" status in CV panel stats
- ✅ Complete CV text displayed (not just placeholder)
- ✅ Word count > 17 words
- ✅ Console logs showing: "Extracted file content length: [large number]"

### 5. If Still Not Working:
- Try with a different PDF file
- Upload a .txt file instead of PDF
- Check browser console for any errors

The fixes should now properly extract and display your complete CV content! 🚀 