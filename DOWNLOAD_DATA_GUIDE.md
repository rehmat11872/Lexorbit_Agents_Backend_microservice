# 📥 Complete Data Download Guide

## Step-by-Step Commands to Download ALL Data

---

## 🚀 **QUICK START (Recommended)**

### Single Command to Get Everything:

```bash
cd /Users/paras/Desktop/TK/Agent_ETL_Pipeline
source venv/bin/activate

# Fetch 1 judge with 20 opinions (downloads ALL related data)
python manage.py fetch_judge_complete 1713 --max-opinions 20
```

**This ONE command downloads:**
- ✅ 1 Judge (Brett Kavanaugh)
- ✅ 20 Opinions (with embeddings)
- ✅ 20 OpinionClusters
- ✅ 20 Dockets
- ✅ 5-10 Courts
- ✅ 50-100 Citations (OpinionsCited)
- ✅ ALL embeddings generated automatically

**Time:** 2-3 minutes

---

## 📊 **COMPLETE GUIDE: All Models**

### **Step 1: Setup Environment**

```bash
# Navigate to project
cd /Users/paras/Desktop/TK/Agent_ETL_Pipeline

# Activate virtual environment
source venv/bin/activate

# Verify server is running (in another terminal)
# Terminal 2:
python manage.py runserver
```

---

### **Step 2: Download Data Using fetch_judge_complete**

This is the **BEST** method because it downloads everything with proper relationships.

#### **Option A: Single Judge (Quick Test)**

```bash
# Fetch Brett Kavanaugh with 20 opinions
python manage.py fetch_judge_complete 1713 --max-opinions 20
```

**What gets downloaded:**

| Model | Table | Records | Description |
|-------|-------|---------|-------------|
| Judge | `judges` | 1 | Brett Kavanaugh's info + embedding |
| Opinion | `opinions` | 20 | His legal opinions + embeddings |
| OpinionCluster | `opinion_clusters` | 20 | Case decisions |
| Docket | `dockets` | 20 | Case details + embeddings |
| Court | `courts` | 5-10 | Courts he's written for |
| OpinionsCited | `opinions_cited` | 50-100 | Citation network |

**Total records:** ~115 across 6 tables

---

#### **Option B: Multiple Judges (Better Dataset)**

```bash
# Fetch 3 Supreme Court judges with 20 opinions each
python manage.py fetch_judge_complete 1713 --max-opinions 20  # Brett Kavanaugh
python manage.py fetch_judge_complete 3045 --max-opinions 20  # John Roberts
python manage.py fetch_judge_complete 2776 --max-opinions 20  # Sonia Sotomayor
```

**What gets downloaded:**

| Model | Table | Records | Description |
|-------|-------|---------|-------------|
| Judge | `judges` | 3 | 3 judges + embeddings |
| Opinion | `opinions` | 60 | 60 legal opinions + embeddings |
| OpinionCluster | `opinion_clusters` | 60 | 60 case decisions |
| Docket | `dockets` | 60 | 60 cases + embeddings |
| Court | `courts` | 10-15 | Various courts |
| OpinionsCited | `opinions_cited` | 150-300 | Citation network |

**Total records:** ~350 across 6 tables

**Time:** 8-10 minutes

---

#### **Option C: Full Supreme Court Dataset (Production)**

```bash
# Fetch all 9 current Supreme Court justices

# Conservative wing
python manage.py fetch_judge_complete 1713 --max-opinions 30  # Brett Kavanaugh
python manage.py fetch_judge_complete 3045 --max-opinions 50  # John Roberts (Chief)
python manage.py fetch_judge_complete 3454 --max-opinions 30  # Samuel Alito
python manage.py fetch_judge_complete 2745 --max-opinions 30  # Clarence Thomas
python manage.py fetch_judge_complete 4238 --max-opinions 30  # Neil Gorsuch
python manage.py fetch_judge_complete 4285 --max-opinions 20  # Amy Coney Barrett

# Liberal wing
python manage.py fetch_judge_complete 2776 --max-opinions 30  # Sonia Sotomayor
python manage.py fetch_judge_complete 2873 --max-opinions 30  # Elena Kagan
python manage.py fetch_judge_complete 4464 --max-opinions 20  # Ketanji Brown Jackson
```

**What gets downloaded:**

| Model | Table | Records | Description |
|-------|-------|---------|-------------|
| Judge | `judges` | 9 | All 9 justices + embeddings |
| Opinion | `opinions` | 270 | 270 legal opinions + embeddings |
| OpinionCluster | `opinion_clusters` | 270 | 270 case decisions |
| Docket | `dockets` | 270 | 270 cases + embeddings |
| Court | `courts` | 15-20 | Supreme Court + related |
| OpinionsCited | `opinions_cited` | 800-1500 | Full citation network |

**Total records:** ~1,650+ across 6 tables

**Time:** 30-45 minutes

---

### **Step 3: Verify Data Was Downloaded**

```bash
# Check database contents
python manage.py shell
```

```python
from court_data.models import Judge, Court, Docket, OpinionCluster, Opinion, OpinionsCited

# Count all records
print("📊 DATABASE CONTENTS:")
print(f"Courts:          {Court.objects.count()}")
print(f"Judges:          {Judge.objects.count()}")
print(f"Dockets:         {Docket.objects.count()}")
print(f"OpinionClusters: {OpinionCluster.objects.count()}")
print(f"Opinions:        {Opinion.objects.count()}")
print(f"OpinionsCited:   {OpinionsCited.objects.count()}")

# Check embeddings
print("\n🧠 EMBEDDINGS:")
print(f"Judges with embeddings:   {Judge.objects.exclude(embedding__isnull=True).count()}")
print(f"Dockets with embeddings:  {Docket.objects.exclude(embedding__isnull=True).count()}")
print(f"Opinions with embeddings: {Opinion.objects.exclude(embedding__isnull=True).count()}")

# Show sample data
print("\n📄 SAMPLE OPINION:")
opinion = Opinion.objects.select_related('cluster__docket__court', 'author').first()
if opinion:
    print(f"Case: {opinion.cluster.docket.case_name_short}")
    print(f"Judge: {opinion.author.full_name}")
    print(f"Court: {opinion.cluster.docket.court.name}")
    print(f"Has embedding: {opinion.embedding is not None}")
    print(f"Text length: {len(opinion.plain_text)} chars")

# Exit
exit()
```

**Expected Output (after Option A):**
```
📊 DATABASE CONTENTS:
Courts:          8
Judges:          1
Dockets:         20
OpinionClusters: 20
Opinions:        20
OpinionsCited:   75

🧠 EMBEDDINGS:
Judges with embeddings:   1
Dockets with embeddings:  20
Opinions with embeddings: 20

📄 SAMPLE OPINION:
Case: NetChoice
Judge: Brett M. Kavanaugh
Court: Supreme Court of the United States
Has embedding: True
Text length: 15234 chars
```

---

### **Step 4: Test API Endpoints**

```bash
# Test semantic search
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "constitutional rights and free speech"
  }'

# Expected: Should return matching opinions with analysis
```

```bash
# Test judge profile
curl "http://localhost:8000/api/judges/1/complete_profile/"

# Expected: Complete judge data with all opinions
```

```bash
# Run full test suite
./test_agents.sh

# Expected: All 6 tests should pass ✅
```

---

## 🎯 **ALTERNATIVE METHODS (Not Recommended)**

### Method 2: Individual Commands (More Work)

If you want to fetch data separately:

#### **A. Fetch Courts Only**
```bash
python manage.py fetch_courts --max-results 20
```
**Downloads:** 20 courts
**Problem:** No opinions, so semantic search won't work ❌

#### **B. Fetch Judges Only**
```bash
python manage.py fetch_judges --max-results 10
```
**Downloads:** 10 judges (basic info only)
**Problem:** No opinions, so semantic search won't work ❌

#### **C. Fetch Cases (Dockets)**
```bash
python manage.py fetch_cases --max-results 50 --court scotus
```
**Downloads:** 50 dockets
**Problem:** No opinions, so semantic search won't work ❌

#### **D. Fetch Opinions**
```bash
python manage.py fetch_opinions --max-results 100
```
**Downloads:** 100 random opinions
**Problem:** 
- May not have related judges/courts/clusters
- Relationships might be broken
- Need to manually generate embeddings ❌

**❌ WHY NOT USE THESE:**
- More commands to run
- Relationships not guaranteed
- Must manually generate embeddings
- More error-prone

---

## ✅ **RECOMMENDED WORKFLOW**

### **For Testing (5 minutes):**

```bash
cd /Users/paras/Desktop/TK/Agent_ETL_Pipeline
source venv/bin/activate

# Quick test with 1 judge
python manage.py fetch_judge_complete 1713 --max-opinions 20

# Verify
python manage.py shell -c "from court_data.models import Opinion; print(f'Opinions: {Opinion.objects.count()}')"

# Test API
./test_agents.sh
```

---

### **For Development (15 minutes):**

```bash
cd /Users/paras/Desktop/TK/Agent_ETL_Pipeline
source venv/bin/activate

# Fetch 3 judges for diverse dataset
python manage.py fetch_judge_complete 1713 --max-opinions 20
python manage.py fetch_judge_complete 3045 --max-opinions 20
python manage.py fetch_judge_complete 2776 --max-opinions 20

# Verify
python manage.py shell -c "
from court_data.models import *
print(f'Judges: {Judge.objects.count()}')
print(f'Opinions: {Opinion.objects.count()}')
print(f'Citations: {OpinionsCited.objects.count()}')
"

# Test API
./test_agents.sh
```

---

### **For Production (45 minutes):**

```bash
cd /Users/paras/Desktop/TK/Agent_ETL_Pipeline
source venv/bin/activate

# Fetch all 9 Supreme Court justices (see Option C above)
# Run each command one by one

# Or use a script:
cat > fetch_all_judges.sh << 'EOF'
#!/bin/bash
JUDGES=(1713 3045 3454 2745 4238 4285 2776 2873 4464)
for judge_id in "${JUDGES[@]}"; do
    echo "Fetching judge $judge_id..."
    python manage.py fetch_judge_complete $judge_id --max-opinions 30
    echo "Done with judge $judge_id"
    echo "---"
done
EOF

chmod +x fetch_all_judges.sh
./fetch_all_judges.sh

# Verify
python manage.py shell -c "
from court_data.models import *
print('📊 PRODUCTION DATABASE:')
print(f'  Judges: {Judge.objects.count()}')
print(f'  Opinions: {Opinion.objects.count()}')
print(f'  Dockets: {Docket.objects.count()}')
print(f'  Courts: {Court.objects.count()}')
print(f'  Citations: {OpinionsCited.objects.count()}')
print(f'  Total Records: {Judge.objects.count() + Opinion.objects.count() + Docket.objects.count() + Court.objects.count() + OpinionsCited.objects.count()}')
"

# Test
./test_agents.sh
```

---

## 📋 **COMMAND REFERENCE**

### **Primary Command: fetch_judge_complete**

```bash
python manage.py fetch_judge_complete <JUDGE_ID> [OPTIONS]
```

**Arguments:**
- `JUDGE_ID` (required): CourtListener judge ID (integer)
- `--max-opinions N`: Maximum opinions to fetch (default: 50)

**Examples:**
```bash
# Fetch judge with 20 opinions
python manage.py fetch_judge_complete 1713 --max-opinions 20

# Fetch judge with 50 opinions (default)
python manage.py fetch_judge_complete 1713

# Fetch judge with 100 opinions
python manage.py fetch_judge_complete 1713 --max-opinions 100
```

---

### **Supreme Court Judge IDs (Reference)**

| Judge ID | Name | Appointed | Ideology |
|----------|------|-----------|----------|
| 3045 | John Roberts (Chief) | 2005 | Conservative |
| 2745 | Clarence Thomas | 1991 | Conservative |
| 3454 | Samuel Alito | 2006 | Conservative |
| 2776 | Sonia Sotomayor | 2009 | Liberal |
| 2873 | Elena Kagan | 2010 | Liberal |
| 4238 | Neil Gorsuch | 2017 | Conservative |
| 1713 | Brett Kavanaugh | 2018 | Conservative |
| 4285 | Amy Coney Barrett | 2020 | Conservative |
| 4464 | Ketanji Brown Jackson | 2022 | Liberal |

---

## 🔍 **WHAT EACH MODEL STORES**

### **1. Court**
```
Fields: court_id, name, short_name, jurisdiction, position
Example: "scotus", "Supreme Court of the United States", "F", "Supreme"
Fetched: Automatically when fetching judges/opinions
```

### **2. Judge**
```
Fields: judge_id, name_first, name_last, full_name, date_birth, gender, education, embedding
Example: 1713, "Brett", "Kavanaugh", "Brett M. Kavanaugh", embedding: [...]
Fetched: Primary command (fetch_judge_complete)
```

### **3. Docket**
```
Fields: docket_id, court_id, case_name, docket_number, date_filed, nature_of_suit, embedding
Example: 71110480, "scotus", "NetChoice v. Fitch", "25A97", "Civil Rights", embedding: [...]
Fetched: Automatically with opinions
```

### **4. OpinionCluster**
```
Fields: cluster_id, docket_id, case_name, date_filed, citation_count
Example: 11120611, 71110480, "NetChoice v. Fitch", "2024-06-13", 0
Fetched: Automatically with opinions
```

### **5. Opinion** ⭐ **MOST IMPORTANT**
```
Fields: opinion_id, cluster_id, author_id, plain_text, embedding, type, date_filed
Example: 11120611, 11120611, 1713, "First Amendment...", embedding: [...], "010combined"
Fetched: Primary data from fetch_judge_complete
```

### **6. OpinionsCited**
```
Fields: citing_opinion_id, cited_opinion_id, depth
Example: 11120611 cites 9876543, depth: 1
Fetched: Automatically with each opinion
```

---

## ⚡ **QUICK COMMANDS CHEAT SHEET**

```bash
# SETUP
cd /Users/paras/Desktop/TK/Agent_ETL_Pipeline
source venv/bin/activate

# DOWNLOAD DATA (pick one)

# Quick test (2-3 min)
python manage.py fetch_judge_complete 1713 --max-opinions 20

# Better dataset (8-10 min)
python manage.py fetch_judge_complete 1713 --max-opinions 20
python manage.py fetch_judge_complete 3045 --max-opinions 20
python manage.py fetch_judge_complete 2776 --max-opinions 20

# VERIFY
python manage.py shell -c "from court_data.models import Opinion; print(Opinion.objects.count())"

# TEST
./test_agents.sh

# CHECK EMBEDDINGS
python manage.py shell -c "from court_data.models import Opinion; print(Opinion.objects.exclude(embedding__isnull=True).count())"
```

---

## 🎓 **UNDERSTANDING THE DATA FLOW**

```
fetch_judge_complete command
        ↓
1. Fetch Judge from CourtListener
   API: /api/rest/v4/people/{judge_id}/
   Save to: judges table
   Generate: judges.embedding
        ↓
2. Fetch Judge's Opinions
   API: /api/rest/v4/opinions/?author={judge_id}
   Store temporarily (need cluster info first)
        ↓
3. For Each Opinion, Fetch Cluster
   API: /api/rest/v4/clusters/{cluster_id}/
   Save to: opinion_clusters table
        ↓
4. For Each Cluster, Fetch Docket
   API: /api/rest/v4/dockets/{docket_id}/
   Save to: dockets table
   Generate: dockets.embedding
        ↓
5. For Each Docket, Fetch Court
   API: /api/rest/v4/courts/{court_id}/
   Save to: courts table
        ↓
6. Save Opinion (now has all relationships)
   Save to: opinions table
   Generate: opinions.embedding ← CRITICAL FOR SEARCH
        ↓
7. Fetch Citations for Opinion
   API: /api/rest/v4/opinions-cited/?citing_opinion={opinion_id}
   Save to: opinions_cited table
```

**Result:** Complete, connected dataset with embeddings!

---

## ✅ **SUCCESS CHECKLIST**

After running commands, verify:

- [ ] Server is running (`http://localhost:8000`)
- [ ] Opinions table has data (`Opinion.objects.count() > 0`)
- [ ] Opinions have embeddings (`Opinion.objects.exclude(embedding__isnull=True).count() > 0`)
- [ ] Relationships work (can access `opinion.cluster.docket.court`)
- [ ] API returns results (`curl /api/legal-research-advanced/`)
- [ ] Test script passes (`./test_agents.sh` all ✅)

---

## 🚨 **TROUBLESHOOTING**

### Problem: "No opinions found"
```bash
# Check if opinions exist
python manage.py shell -c "from court_data.models import Opinion; print(Opinion.objects.count())"

# If 0, run:
python manage.py fetch_judge_complete 1713 --max-opinions 20
```

### Problem: "API returns 0 results"
```bash
# Check embeddings
python manage.py shell -c "from court_data.models import Opinion; print(Opinion.objects.exclude(embedding__isnull=True).count())"

# If 0, embeddings weren't generated. Re-fetch data.
```

### Problem: "Court not found"
```bash
# The fetch_judge_complete command automatically fetches courts
# Just run it again, it will fetch missing courts
python manage.py fetch_judge_complete 1713 --max-opinions 20
```

---

## 📖 **SUMMARY**

**Best Command to Download ALL Data:**
```bash
python manage.py fetch_judge_complete 1713 --max-opinions 20
```

**This downloads ALL 6 models with relationships and embeddings!**

**For production, fetch multiple judges:**
```bash
python manage.py fetch_judge_complete 1713 --max-opinions 30
python manage.py fetch_judge_complete 3045 --max-opinions 30
python manage.py fetch_judge_complete 2776 --max-opinions 30
```

**Time:** 2-3 minutes per judge
**Result:** Complete dataset ready for AI agents! ✅

