# 🔄 CourtListener API Call Sequence

## Complete Flow: From CourtListener → Your Database → Your API

---

## 📥 **PART 1: Fetching Data from CourtListener**

### When You Run: `python manage.py fetch_judge_complete 1713`

**Here's EXACTLY what happens:**

```
Step 1: Fetch Judge Info
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Call:
   GET https://www.courtlistener.com/api/rest/v4/people/1713/

📦 Data Received:
   {
     "id": 1713,
     "name_first": "Brett",
     "name_last": "Kavanaugh",
     "name_full": "Brett M. Kavanaugh",
     "date_of_birth": "1965-01-01",
     "gender": "m",
     "education": [...],
     ...
   }

💾 Saved To:
   Table: judges
   Fields: judge_id, name_first, name_last, full_name, date_birth, gender
   
🧠 Embedding Generated From:
   Text: "Brett M. Kavanaugh [biography] [education] [positions]"
   Saved To: judges.embedding (1536 dimensions)


Step 2: Fetch Judge's Opinions List
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Call:
   GET https://www.courtlistener.com/api/rest/v4/opinions/?author=1713

📦 Data Received:
   {
     "results": [
       {
         "id": 11120611,
         "cluster": "https://www.courtlistener.com/.../clusters/11120611/",
         "author": 1713,
         "type": "010combined",
         "plain_text": "First Amendment protects...",
         ...
       },
       {
         "id": 11120610,
         ...
       }
     ]
   }

💾 Saved To:
   Table: opinions (will save later, after cluster)
   Note: Temporarily stored, waiting for cluster data


Step 3: For EACH Opinion, Fetch Opinion Cluster
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Call:
   GET https://www.courtlistener.com/api/rest/v4/clusters/11120611/

📦 Data Received:
   {
     "id": 11120611,
     "docket": "https://www.courtlistener.com/.../dockets/71110480/",
     "case_name": "NetChoice, LLC v. Lynn Fitch",
     "case_name_short": "NetChoice",
     "date_filed": "2024-06-13",
     "panel": [1713, 3045, 2776],
     ...
   }

💾 Saved To:
   Table: opinion_clusters
   Fields: cluster_id, case_name, case_name_short, date_filed


Step 4: For EACH Cluster, Fetch Docket (Case)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Call:
   GET https://www.courtlistener.com/api/rest/v4/dockets/71110480/

📦 Data Received:
   {
     "id": 71110480,
     "court": "https://www.courtlistener.com/.../courts/scotus/",
     "docket_number": "25A97",
     "case_name": "NetChoice, LLC v. Lynn Fitch",
     "date_filed": "2024-06-13",
     "nature_of_suit": "Civil Rights",
     ...
   }

💾 Saved To:
   Table: dockets
   Fields: docket_id, docket_number, case_name, date_filed, nature_of_suit

🧠 Embedding Generated From:
   Text: "NetChoice Civil Rights [case summary]"
   Saved To: dockets.embedding (1536 dimensions)


Step 5: For EACH Docket, Fetch Court
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Call:
   GET https://www.courtlistener.com/api/rest/v4/courts/scotus/

📦 Data Received:
   {
     "id": "scotus",
     "name": "Supreme Court of the United States",
     "short_name": "Supreme Court",
     "jurisdiction": "F",
     "position": "Supreme",
     ...
   }

💾 Saved To:
   Table: courts
   Fields: court_id, name, short_name, jurisdiction, position


Step 6: Save Opinion (Now That We Have Everything)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Saved To:
   Table: opinions
   Fields:
     - opinion_id: 11120611
     - cluster_id: 11120611 (FK → opinion_clusters)
     - author_id: 1713 (FK → judges)
     - plain_text: "First Amendment protects..."
     - type: "010combined"
     - date_filed: "2024-06-20"

🧠 Embedding Generated From:
   Text: First 8000 chars of opinion.plain_text
   Saved To: opinions.embedding (1536 dimensions)
   
   ⭐ THIS IS THE KEY EMBEDDING FOR SEMANTIC SEARCH!


Step 7: Fetch Citations (What This Opinion Cites)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Call:
   GET https://www.courtlistener.com/api/rest/v4/opinions-cited/?citing_opinion=11120611

📦 Data Received:
   {
     "results": [
       {
         "citing_opinion": 11120611,
         "cited_opinion": 9876543,
         "depth": 1
       },
       ...
     ]
   }

💾 Saved To:
   Table: opinions_cited
   Fields:
     - citing_opinion_id: 11120611 (FK → opinions)
     - cited_opinion_id: 9876543 (FK → opinions)
     - depth: 1
```

---

## 🔗 **PART 2: Database Relationships Created**

After fetching judge 1713 with 20 opinions, your database looks like:

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE STRUCTURE                         │
└─────────────────────────────────────────────────────────────────┘

courts (5-10 records)
  court_id: scotus
  name: "Supreme Court of the United States"
  ↓ (one court has many dockets)
  
dockets (20 records)
  docket_id: 71110480
  court_id: scotus (FK)
  case_name: "NetChoice v. Fitch"
  embedding: [0.123, -0.456, ...] ← Can search by case topic
  ↓ (one docket has many clusters)
  
opinion_clusters (20 records)
  cluster_id: 11120611
  docket_id: 71110480 (FK)
  case_name: "NetChoice v. Fitch"
  ↓ (one cluster has many opinions)
  
opinions (20 records)  ← THIS IS WHAT YOU NEED!
  opinion_id: 11120611
  cluster_id: 11120611 (FK)
  author_id: 1713 (FK)
  plain_text: "First Amendment protects..."
  embedding: [0.234, -0.567, ...] ← Semantic search uses this!
  ↓ (one opinion cites many opinions)
  
opinions_cited (50-100 records)
  citing_opinion_id: 11120611 (FK)
  cited_opinion_id: 9876543 (FK)
  ↓ (back to opinions)
  
judges (1 record)
  judge_id: 1713
  full_name: "Brett M. Kavanaugh"
  embedding: [0.345, -0.678, ...] ← Can search by judge expertise
```

---

## 📤 **PART 3: Your API Endpoints Query This Data**

### Endpoint 1: `/api/legal-research-advanced/`

**Query:** `{"query": "constitutional rights"}`

```
Flow:
1. Generate embedding for "constitutional rights"
   OpenAI API → [0.234, -0.567, ...]

2. Search opinions.embedding using pgvector
   SELECT * FROM opinions
   WHERE embedding IS NOT NULL
   ORDER BY embedding <=> '[0.234, -0.567, ...]'
   LIMIT 20

3. Get matching opinion IDs: [11120611, 11120610, ...]

4. Fetch full opinion data with relationships:
   Opinion.objects.filter(opinion_id__in=[11120611, ...])
     .select_related('cluster__docket__court', 'author')

5. For each opinion, traverse:
   - opinion.plain_text → Excerpt
   - opinion.author.full_name → "Brett M. Kavanaugh"
   - opinion.cluster.docket.case_name_short → "NetChoice"
   - opinion.cluster.docket.court.name → "Supreme Court"
   - opinion.cited_by.count() → Citation count

6. Return JSON response
```

**Response:**
```json
{
  "query": "constitutional rights",
  "key_authorities": [
    {
      "case_name": "NetChoice",
      "judge": "Brett M. Kavanaugh",
      "court": "Supreme Court",
      "excerpt": "First Amendment protects..."
    }
  ]
}
```

---

### Endpoint 2: `/api/agents/semantic-search/`

**Query:** `{"query": "First Amendment cases"}`

```
Flow:
1. Generate embedding for query

2. Search 3 tables in parallel:
   
   A. opinions.embedding (legal text)
   B. dockets.embedding (case topics)
   C. judges.embedding (expertise)

3. Combine results:
   - Top 10 opinions
   - Top 5 cases
   - Top 3 judges

4. Return mixed results
```

---

### Endpoint 3: `/api/judges/<id>/complete_profile/`

**Query:** `GET /api/judges/1713/complete_profile/`

```
Flow:
1. Get judge: Judge.objects.get(judge_id=1713)

2. Get all their opinions:
   judge.authored_opinions.select_related('cluster__docket__court')

3. Calculate statistics:
   - Total cases: opinions.count()
   - Citations: sum of opinion.cited_by.count()
   - Grant rate: outcomes analysis

4. Return complete profile
```

---

## 📊 **PART 4: Complete Data Journey**

```
CourtListener API
      ↓
Python Service (courtlistener_service.py)
      ↓
Data Processors (data_processors.py)
      ↓
Generate Embeddings (OpenAI)
      ↓
Save to PostgreSQL
      ├── judges table
      ├── courts table
      ├── dockets table (with embeddings)
      ├── opinion_clusters table
      ├── opinions table (with embeddings) ← KEY FOR SEARCH
      └── opinions_cited table
      ↓
Django ORM Models
      ↓
API Views (api/views.py)
      ↓
AI Services (api/ai_services.py)
      ↓
Semantic Search (pgvector)
      ↓
REST API Response (JSON)
      ↓
Your Frontend/Agent
```

---

## 🎯 **PART 5: Why Each Embedding Matters**

### 1. **opinions.embedding** ⭐ MOST IMPORTANT
```
Source: opinion.plain_text (first 8000 chars)
Used By: 
  - /api/legal-research-advanced/
  - /api/agents/semantic-search/
  
Why: Contains the actual legal reasoning and precedents
Example: "The First Amendment protects free speech..."
```

### 2. **dockets.embedding**
```
Source: docket.case_name + nature_of_suit
Used By:
  - /api/agents/semantic-search/
  
Why: Good for finding cases by topic
Example: "Civil Rights - Free Speech"
```

### 3. **judges.embedding**
```
Source: judge bio + education + positions
Used By:
  - /api/agents/semantic-search/
  
Why: Find judges by expertise area
Example: "Constitutional law expert, Harvard Law"
```

---

## ✅ **SUMMARY**

### API Call Order (when fetching judge):
```
1. People API → Judge info
2. Opinions API → List of opinion IDs
3. Clusters API → Case grouping (one per opinion)
4. Dockets API → Case details (one per cluster)
5. Courts API → Court info (one per docket)
6. Save Opinion → With all relationships
7. OpinionsCited API → Citation network
```

### Database Tables Created:
```
✅ judges (1)
✅ courts (5-10)
✅ dockets (20) with embeddings
✅ opinion_clusters (20)
✅ opinions (20) with embeddings ← THIS IS CRITICAL
✅ opinions_cited (50-100)
```

### Your API Endpoints Use:
```
Primary: opinions.embedding
Secondary: dockets.embedding, judges.embedding
```

### Why You Had 0 Results:
```
❌ You only fetched courts (no opinions)
❌ Endpoints search opinions table
❌ No opinions = no results
```

### Fix:
```
✅ Fetch judge with opinions
✅ Generates opinion.embedding automatically
✅ Now semantic search works!
```

---

**Run this to fix:**
```bash
python manage.py fetch_judge_complete 1713 --max-opinions=20
```

**Then test:**
```bash
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "constitutional rights"}'
```

**Will return results!** ✅

