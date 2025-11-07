# 🚀 Production Deployment Guide

Deploy your trading bot to run 24/7 in the cloud - **even when your computer is off!**

---

## ⭐ **OPTION 1: GitHub Actions (FREE, EASIEST)** - RECOMMENDED

**Perfect for:** Paper trading, learning, testing  
**Cost:** FREE forever  
**Reliability:** High (GitHub infrastructure)  
**Setup Time:** 5 minutes

### **How It Works:**
- Runs on GitHub's servers (free)
- Executes 4x daily automatically
- Stores learning data between runs
- No server needed!

### **Setup Steps:**

#### 1. **Push Code to GitHub** (Already done ✅)
Your code is at: `https://github.com/DJN2709/DJN-Broker`

#### 2. **Add Secrets to GitHub**
Go to: `https://github.com/DJN2709/DJN-Broker/settings/secrets/actions`

Click **"New repository secret"** and add:

```
REDDIT_CLIENT_ID = your_reddit_client_id
REDDIT_CLIENT_SECRET = your_reddit_client_secret
REDDIT_USER_AGENT = free-mvp/0.1 by your_username
NEWSAPI_KEY = your_newsapi_key (optional)
ALPACA_PAPER_API_KEY = PKT6PH6KPSNWHSDSZRRYQVSJMK
ALPACA_PAPER_API_SECRET = 6A6qxJVL32CjpXT9YcXADjLdgWGorCAV58oviWpUrTMz
ALPACA_LIVE_API_KEY = AKUSSE272MUBVFISBTAFSEJUSW
ALPACA_LIVE_API_SECRET = M11fg5SEdujkdwfznKwNMpT5owTy95YpqRV7qXTQ1Ep
```

#### 3. **Enable GitHub Actions**
- Go to: `https://github.com/DJN2709/DJN-Broker/actions`
- Click "I understand my workflows, go ahead and enable them"

#### 4. **Done!**
Bot will now run automatically 4x daily:
- 09:00 Berlin time
- 15:35 Berlin time (US market open)
- 18:00 Berlin time (US midday)
- 21:30 Berlin time (before US close)

### **Monitor Your Bot:**
```
View runs: https://github.com/DJN2709/DJN-Broker/actions
Check logs: Click on any run → View job details
Download data: Artifacts section (trading logs, summaries)
```

### **Manual Trigger:**
- Go to Actions tab
- Select "Automated Trading Bot"
- Click "Run workflow"
- Bot runs immediately!

### **Pros:**
✅ Completely FREE  
✅ Zero maintenance  
✅ Runs automatically  
✅ Stores logs & data  
✅ No server needed  

### **Cons:**
⚠️ Limited to 4 runs per day (could add more)  
⚠️ ~10 minute startup time per run  
⚠️ Learning data persists but needs cache  

---

## 🚂 **OPTION 2: Railway (FREE Tier, Always-On)**

**Perfect for:** 24/7 operation, live trading preparation  
**Cost:** FREE tier ($5 credit/month, ~500 hours)  
**Reliability:** Very high  
**Setup Time:** 10 minutes

### **Setup Steps:**

#### 1. **Create Railway Account**
- Go to: https://railway.app
- Sign up with GitHub

#### 2. **Deploy from GitHub**
- Click "New Project"
- Select "Deploy from GitHub repo"
- Choose: `DJN2709/DJN-Broker`
- Railway auto-detects Dockerfile

#### 3. **Add Environment Variables**
In Railway dashboard → Variables:
```
REDDIT_CLIENT_ID = your_value
REDDIT_CLIENT_SECRET = your_value
REDDIT_USER_AGENT = your_value
NEWSAPI_KEY = your_value
ALPACA_PAPER_API_KEY = your_value
ALPACA_PAPER_API_SECRET = your_value
ALPACA_LIVE_API_KEY = your_value
ALPACA_LIVE_API_SECRET = your_value
```

#### 4. **Deploy!**
- Click "Deploy"
- Railway builds and starts your bot
- Bot runs 24/7 automatically!

### **Monitor:**
```
Logs: Railway dashboard → Deployments → View logs
Metrics: CPU, memory, network usage
Restart: Click "Redeploy" button
```

### **Pros:**
✅ Always running (24/7)  
✅ Real-time logs  
✅ Auto-restarts on crash  
✅ Free tier generous  
✅ Simple setup  

### **Cons:**
⚠️ Free tier limited to 500 hours/month  
⚠️ Need to monitor usage  

---

## 🎨 **OPTION 3: Render (FREE, Similar to Railway)**

**Perfect for:** Alternative to Railway  
**Cost:** FREE tier  
**Reliability:** High  
**Setup Time:** 10 minutes

### **Setup Steps:**

#### 1. **Create Render Account**
- Go to: https://render.com
- Sign up with GitHub

#### 2. **New Web Service**
- Click "New +"
- Select "Background Worker"
- Connect to: `DJN2709/DJN-Broker`

#### 3. **Configure**
- Name: `djn-broker-bot`
- Build Command: `pip install -r requirements.txt`
- Start Command: `python schedule_runner.py`

#### 4. **Add Environment Variables**
Same as Railway (see above)

#### 5. **Deploy!**
Bot runs continuously.

### **Pros:**
✅ Always running  
✅ Free tier available  
✅ Good performance  

### **Cons:**
⚠️ Free tier spins down after 15 min inactivity  
⚠️ May need paid plan for 24/7  

---

## 🐳 **OPTION 4: Docker on VPS (Full Control)**

**Perfect for:** Maximum control, live trading  
**Cost:** $5-10/month (DigitalOcean, Hetzner, etc.)  
**Reliability:** Depends on provider  
**Setup Time:** 20 minutes

### **Setup Steps:**

#### 1. **Get a VPS**
- DigitalOcean: https://digitalocean.com ($5/month)
- Hetzner: https://hetzner.com (€4/month)
- Linode: https://linode.com ($5/month)

#### 2. **SSH into Server**
```bash
ssh root@your-server-ip
```

#### 3. **Install Docker**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

#### 4. **Clone Your Repo**
```bash
git clone https://github.com/DJN2709/DJN-Broker.git
cd DJN-Broker
```

#### 5. **Create .env File**
```bash
nano .env
# Paste your credentials
```

#### 6. **Run with Docker Compose**
```bash
docker-compose up -d
```

#### 7. **Check Status**
```bash
docker-compose logs -f  # View live logs
docker-compose ps       # Check if running
```

### **Pros:**
✅ Full control  
✅ Always running  
✅ Can install anything  
✅ Good for live trading  

### **Cons:**
⚠️ Costs $5-10/month  
⚠️ Need to maintain server  
⚠️ More complex setup  

---

## 📊 **Comparison Table**

| Feature | GitHub Actions | Railway | Render | VPS |
|---------|---------------|---------|--------|-----|
| **Cost** | FREE ✅ | FREE (limited) | FREE (limited) | $5-10/mo |
| **Setup** | 5 min ⚡ | 10 min | 10 min | 20 min |
| **Always On** | ❌ (scheduled) | ✅ | ⚠️ (spins down) | ✅ |
| **Maintenance** | ✅ Zero | ✅ Minimal | ✅ Minimal | ⚠️ Some |
| **Best For** | Paper trading | 24/7 paper | Paper trading | Live trading |
| **Reliability** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🎯 **My Recommendation for You:**

### **Start with GitHub Actions (FREE)** ⭐

**Why:**
1. ✅ Completely FREE
2. ✅ Zero maintenance
3. ✅ Perfect for paper trading
4. ✅ Runs 4x daily automatically
5. ✅ Already set up! Just add secrets

**Then upgrade to:**
- **Railway** when you want 24/7 operation
- **VPS** when you go live with real money

---

## ⚡ **Quick Start (GitHub Actions):**

```bash
# 1. Code is already pushed ✅

# 2. Add secrets to GitHub:
Go to: https://github.com/DJN2709/DJN-Broker/settings/secrets/actions
Add all API keys (see list above)

# 3. Enable Actions:
Go to: https://github.com/DJN2709/DJN-Broker/actions
Enable workflows

# 4. Done! Bot runs automatically 4x daily 🎉
```

---

## 📊 **Monitoring Your Bot:**

### **GitHub Actions:**
```
View runs: https://github.com/DJN2709/DJN-Broker/actions
Check logs: Click any run → Job details
Download data: Artifacts section
```

### **Railway/Render:**
```
Dashboard → Logs → Live tail
Metrics → CPU, Memory, Network
Restart → Redeploy button
```

### **VPS:**
```bash
docker-compose logs -f                    # Live logs
docker-compose restart                    # Restart bot
docker exec -it djn-broker-bot bash      # Shell access
```

---

## 🚨 **Important Notes:**

### **For Paper Trading:**
- GitHub Actions is perfect
- No need for always-on server
- Free and reliable

### **For Live Trading:**
- Use Railway or VPS
- Need 24/7 uptime
- More reliable execution

### **Security:**
- NEVER commit .env file
- Use secrets/environment variables
- Rotate API keys regularly

---

## 📞 **Support:**

**GitHub Actions not working?**
- Check Actions tab for errors
- Verify secrets are added
- Check workflow file syntax

**Railway/Render issues?**
- Check logs in dashboard
- Verify environment variables
- Restart deployment

**VPS problems?**
- SSH and check docker logs
- Restart container if needed
- Check server resources

---

## ✅ **You're Ready!**

Your bot can now run 24/7 in the cloud, even when your computer is off!

Choose your deployment method and get started! 🚀

