# 🚀 Deployment Guide - Postal AI Service

How to deploy your AI service to work with Render (backend) and Vercel (frontend).

---

## 🎯 Recommended Architecture

```
Vercel (Frontend) 
    ↓ HTTPS
Render (Node.js Backend)
    ↓ HTTPS
Hugging Face Spaces (AI Service) ← FREE & ML-optimized!
    ↓
Qdrant Cloud (Vector DB) ← FREE tier
    ↓
MongoDB Atlas (Database) ← Already have this
```

---

## 📋 Step-by-Step Deployment

### **Step 1: Deploy Qdrant Cloud (Vector Database)**

1. **Sign up**: Go to https://cloud.qdrant.io
2. **Create cluster**:
   - Name: `postal-vectors`
   - Region: Choose closest to your backend
   - Tier: **Free** (1GB storage)
3. **Get credentials**:
   ```
   Cluster URL: xyz-abc.qdrant.io
   API Key: your_api_key_here
   ```
4. **Save these** - you'll need them

**Cost:** $0/month ✅

---

### **Step 2: Deploy AI Service to Hugging Face Spaces**

#### **Why Hugging Face Spaces:**
- ✅ **FREE unlimited** (for public spaces)
- ✅ **Designed for ML models**
- ✅ 16GB RAM (plenty for our models)
- ✅ No cold starts
- ✅ Community support

#### **Setup:**

1. **Create account**: https://huggingface.co/join

2. **Create new Space**:
   - Go to: https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `postal-ai-service`
   - License: Apache 2.0
   - SDK: **Docker**
   - Visibility: Public (for free tier)

3. **Push your code**:
   ```bash
   cd /Users/mind/Projects/Postal/postal_ai_services
   
   # Initialize git (if not already)
   git init
   git add .
   git commit -m "Initial AI service"
   
   # Add Hugging Face remote
   git remote add hf https://huggingface.co/spaces/YOUR_USERNAME/postal-ai-service
   
   # Push
   git push hf main
   ```

4. **Add environment variables** in Space settings:
   ```
   MONGODB_URI=mongodb+srv://...
   QDRANT_HOST=xyz-abc.qdrant.io
   QDRANT_API_KEY=your_api_key
   QDRANT_PORT=6333
   EMBEDDING_MODEL=all-MiniLM-L6-v2
   EMBEDDING_DIMENSION=384
   ENVIRONMENT=production
   ```

5. **Your AI service will be available at**:
   ```
   https://YOUR_USERNAME-postal-ai-service.hf.space
   ```

**Cost:** $0/month ✅

---

### **Step 3: Update Node.js Backend on Render**

1. **Add environment variable** in Render dashboard:
   ```
   AI_SERVICE_URL=https://YOUR_USERNAME-postal-ai-service.hf.space
   ```

2. **Redeploy** your backend (or it auto-deploys)

---

### **Step 4: Generate Initial Embeddings**

Since the AI service is now deployed, you need to populate Qdrant Cloud:

**Option A: Run locally, connect to cloud**

Update your local `.env`:
```env
QDRANT_HOST=xyz-abc.qdrant.io
QDRANT_API_KEY=your_api_key
```

Then run:
```bash
source venv/bin/activate
python generate_embeddings_local.py
```

**Option B: Create a one-time script endpoint**

Add to your AI service (temporary):
```python
@app.post("/admin/generate-all-embeddings")
async def generate_all_embeddings(admin_key: str):
    if admin_key != "YOUR_SECRET_KEY":
        raise HTTPException(401)
    
    # Run embedding generation
    # ... (use the script logic)
```

Call it once after deployment, then remove the endpoint.

---

## 🔧 Modified Files for Production

### **1. Update `config.py` for Qdrant API Key**

<function_calls>
<invoke name="search_replace">
<parameter name="file_path">/Users/mind/Projects/Postal/postal_ai_services/src/core/config.py

