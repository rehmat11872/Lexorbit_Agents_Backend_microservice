# Legal AI Agent Platform - Complete System Guide

## 🎯 What This System Does

This is a **Legal Research AI Platform** that:
1. Fetches legal data from **CourtListener API** (judges, cases, opinions)
2. Stores data in **PostgreSQL** with proper relationships
3. Generates **embeddings** using **OpenAI** and stores in **pgvector**
4. Provides **REST APIs** for AI agents to query legal data semantically

---

## 📊 PART 1: DATA FLOW - CourtListener to Database

### Step 1: CourtListener API Calls

The system calls these **CourtListener v4 APIs**:

```
1. Courts API
   URL: https://www.courtlistener.com/api/rest/v4/courts/
   Data: Court names, jurisdictions, types
   
2. Judges API  
   URL: https://www.courtlistener.com/api/rest/v4/people/
   Data: Judge names, bio, education, positions
   
3. Dockets API (Cases)
   URL: https://www.courtlistener.com/api/rest/v4/dockets/
   Data: Case names, docket numbers, dates, nature of suit
   
4. Opinion Clusters API
   URL: https://www.courtlistener.com/api/rest/v4/clusters/
   Data: Case decisions, filing dates, panel of judges
   
5. Opinions API
   URL: https://www.courtlistener.com/api/rest/v4/opinions/
   Data: Legal opinion text, author, type, HTML/plain text
   
6. OpinionsCited API (Citations)
   URL: https://www.courtlistener.com/api/rest/v4/opinions-cited/
   Data: Which opinions cite which (citation network)
```

### Step 2: Data Received from APIs

**Example: Fetching Judge Brett Kavanaugh**

```json
{
  "id": 1713,
  "name_first": "Brett",
  "name_middle": "M.",
  "name_last": "Kavanaugh",
  "date_of_birth": "1965-01-01",
  "gender": "m",
  "race": "w",
  "dob_city": "Washington",
  "dob_state": "DC",
  "education": [
    {"degree": "ba", "school": "Yale University", "year": 1987},
    {"degree": "jd", "school": "Yale University", "year": 1990}
  ]
}
```

Then system fetches his opinions → opinion clusters → dockets → citations.

---

## 🗄️ PART 2: DATABASE SCHEMA & RELATIONSHIPS

### Tables & What They Store

#### 1. **`courts`** - Court Information
```
court_id (PK)           → CourtListener court ID
name                    → "Supreme Court of the United States"
short_name              → "Supreme Court"
jurisdiction            → "F" (Federal)
```

#### 2. **`judges`** - Judge Information
```
judge_id (PK)           → CourtListener person ID (e.g., 1713)
name_first              → "Brett"
name_last               → "Kavanaugh"
full_name               → "Brett M. Kavanaugh"
date_birth              → 1965-01-01
gender                  → "m"
race                    → "w"
biography               → Full bio text
education (JSON)        → [{"degree": "ba", "school": "Yale"}]
positions (JSON)        → [{"court": "Supreme Court", "date_start": "2018"}]
embedding (vector)      → [0.123, -0.456, ...] (1536 dimensions)
```
**Embedding**: Contains semantic meaning of judge's bio + education + positions

#### 3. **`dockets`** - Legal Cases
```
docket_id (PK)          → CourtListener docket ID
court_id (FK)           → References courts table
case_name               → "NetChoice, LLC v. Lynn Fitch"
case_name_short         → "NetChoice"
docket_number           → "25A97"
date_filed              → 2024-06-13
nature_of_suit          → "Civil Rights"
embedding (vector)      → Case semantic embedding
```
**Relationship**: Each docket belongs to ONE court

#### 4. **`opinion_clusters`** - Case Decisions (Groups of Opinions)
```
cluster_id (PK)         → CourtListener cluster ID
docket_id (FK)          → References dockets table
case_name               → "Moore v. United States"
date_filed              → 2024-06-20
citation_count          → 150
```
**Relationship**: Each cluster belongs to ONE docket
**Why clusters?**: A single case decision may have multiple opinions (majority, dissent, concurrence)

#### 5. **`opinions`** - Individual Legal Opinions
```
opinion_id (PK)         → CourtListener opinion ID
cluster_id (FK)         → References opinion_clusters table
author_id (FK)          → References judges table (who wrote it)
type                    → "010combined" (majority/dissent/concurrence)
plain_text              → Full opinion text
html                    → HTML version
date_filed              → 2024-06-20
page_count              → 45
embedding (vector)      → Opinion semantic embedding
```
**Relationships**:
- Each opinion belongs to ONE cluster
- Each opinion has ONE author (judge)
- Opinions cite other opinions (many-to-many)

#### 6. **`opinions_cited`** - Citation Network
```
id (PK)
citing_opinion_id (FK)  → Opinion that cites
cited_opinion_id (FK)   → Opinion being cited
depth                   → 1 (direct citation)
influence_score         → 0.85 (how important)
```
**Relationship**: Many-to-many between opinions

#### 7. **`judge_docket_relation`** - Judge-Case Associations
```
id (PK)
judge_id (FK)           → References judges
docket_id (FK)          → References dockets
role                    → "panel_member" / "author"
outcome                 → "grant" / "deny"
```

#### 8. **`case_outcomes`** - Case Results
```
id (PK)
docket_id (FK)          → References dockets
outcome_type            → "favorable" / "dismissed"
date_decided            → 2024-06-20
```

---

## 🔗 PART 3: COMPLETE RELATIONSHIP DIAGRAM

```
Court
  ↓ (has many)
Docket (Case)
  ↓ (has many)
OpinionCluster (Decision)
  ↓ (has many)
Opinion ──────→ Judge (author)
  ↓ (cites)
Opinion ←──────→ Opinion (citations network)
```

**Example Flow**:
```
Supreme Court (court_id: scotus)
  └── NetChoice v. Fitch (docket_id: 71110480)
      └── Cluster (cluster_id: 11120611)
          └── Opinion (opinion_id: 11120611)
              ├── Author: Brett Kavanaugh (judge_id: 1713)
              ├── Cites: 15 other opinions
              └── Cited by: 0 opinions (too new)
```

---

## 🧠 PART 4: EMBEDDINGS - How Semantic Search Works

### What Are Embeddings?

Embeddings convert text into **1536 numbers** that represent **meaning**.

**Example**:
```
Text: "constitutional rights and federal jurisdiction"
Embedding: [0.023, -0.145, 0.678, ..., 0.234]  (1536 numbers)
```

Similar meanings → similar number patterns

### Where Embeddings Are Stored

**3 tables have embeddings**:

1. **`judges.embedding`**
   - Generated from: biography + education + positions
   - Used for: "Find judges who specialize in civil rights"

2. **`dockets.embedding`**
   - Generated from: case_name + nature_of_suit + summary
   - Used for: "Find similar cases about banking fraud"

3. **`opinions.embedding`**
   - Generated from: plain_text (first 8000 chars)
   - Used for: "Find opinions discussing constitutional law"

### How Embeddings Are Generated

**In `data_processors.py`**:
```python
def generate_embedding(text):
    # Call OpenAI API
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding  # Returns 1536 numbers

# When saving a judge:
judge_text = f"{judge.full_name} {judge.biography} {judge.education}"
judge.embedding = generate_embedding(judge_text)
judge.save()
```

### How Semantic Search Works

**Using pgvector for similarity**:

```sql
-- Find opinions similar to user query
SELECT 
    opinion_id, 
    plain_text,
    embedding <=> '[0.123, -0.456, ...]' AS distance
FROM opinions
WHERE embedding IS NOT NULL
ORDER BY distance  -- Lower distance = more similar
LIMIT 10
```

**The `<=>` operator** calculates **cosine distance** between vectors:
- 0.0 = identical meaning
- 1.0 = completely different
- 0.2 = very similar

---

## 🚀 PART 5: HOW TO USE THE SYSTEM

### Setup & Start

```bash
# 1. Start PostgreSQL (if not running)
# 2. Activate virtual environment
cd /Users/paras/Desktop/TK/Agent_ETL_Pipeline
source venv/bin/activate

# 3. Start Django server
python manage.py runserver
```

Server runs on: `http://localhost:8000`

---

## 🤖 PART 6: AGENT QUERIES - How to Get Answers

### Method 1: Semantic Search (Vector Similarity)

**What it does**: Finds legal content by meaning, not keywords

```bash
curl -X POST http://localhost:8000/api/agents/semantic-search/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "civil rights and free speech",
    "max_results": 10
  }'
```

**What happens**:
1. System generates embedding for "civil rights and free speech"
2. Compares to all embeddings in database using pgvector
3. Returns top 10 most similar: opinions, cases, judges

**Response**:
```json
{
  "query": "civil rights and free speech",
  "total_results": 10,
  "results": [
    {
      "type": "opinion",
      "id": 11120611,
      "title": "NetChoice v. Fitch",
      "author": "Brett M. Kavanaugh",
      "court": "Supreme Court",
      "excerpt": "First Amendment protections..."
    },
    {
      "type": "judge",
      "id": 1713,
      "name": "Brett M. Kavanaugh",
      "biography": "Known for First Amendment cases..."
    }
  ]
}
```

---

### Method 2: Legal Research Assistant (AI-Powered)

**What it does**: Semantic search + GPT-4 analysis

```bash
curl -X POST http://localhost:8000/api/legal-research-advanced/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can states regulate social media content?",
    "filters": {
      "jurisdiction": "federal",
      "court_level": "supreme"
    }
  }'
```

**What happens**:
1. Semantic search finds relevant cases
2. GPT-4 analyzes the cases
3. Generates legal summary with citations

**Response**:
```json
{
  "query": "Can states regulate social media content?",
  "summary": "Recent Supreme Court decisions indicate...",
  "analysis": "The Court in NetChoice v. Fitch held that...",
  "key_authorities": [
    {
      "case_name": "NetChoice v. Fitch",
      "citation": "606 U.S. ____ (2025)",
      "excerpt": "First Amendment prohibits state content moderation laws...",
      "relevance": "Directly addresses state regulation of platforms"
    }
  ]
}
```

---

### Method 3: Judge Complete Profile

**Get ALL data for a judge**:

```bash
curl http://localhost:8000/api/judges/34/complete_profile/
```

**Response includes**:
```json
{
  "basic_info": {
    "judge_id": 1713,
    "full_name": "Brett M. Kavanaugh",
    "date_birth": "1965-01-01",
    "biography": "..."
  },
  "education": [
    {"degree": "ba", "school": "Yale", "year": 1987}
  ],
  "statistics": {
    "total_cases": 150,
    "total_opinions": 200,
    "grant_rate": 65.2
  },
  "all_cases": [
    {
      "case_name": "NetChoice v. Fitch",
      "opinion": {...},
      "citations": {"cites_to": 15, "cited_by": 0}
    }
  ]
}
```

---

### Method 4: Case Prediction (AI)

**Predict case outcome**:

```bash
curl -X POST http://localhost:8000/api/agents/case-prediction/ \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "civil rights",
    "jurisdiction": "federal",
    "judge_id": 1713,
    "brief_summary": "Free speech case about social media"
  }'
```

**What happens**:
1. Finds similar historical cases
2. Analyzes judge's history in similar cases
3. Calculates success probability

**Response**:
```json
{
  "predicted_outcome": "favorable",
  "success_probability": 78.5,
  "factors": [
    {
      "factor": "Judge historical grant rate",
      "impact": "positive",
      "weight": 0.4
    },
    {
      "factor": "Similar case precedents",
      "impact": "positive",
      "weight": 0.35
    }
  ]
}
```

---

## 📥 PART 7: FETCHING MORE DATA

### Fetch Specific Judge with All Data

```bash
python manage.py fetch_judge_complete 1713 --max-opinions=50
```

**What it fetches**:
1. Judge info (bio, education)
2. All their opinions (up to 50)
3. All opinion clusters
4. All dockets (cases)
5. All citations
6. Generates embeddings automatically

**Data saved to**:
- `judges` table (1 row)
- `courts` table (10-20 rows)
- `dockets` table (50 rows)
- `opinion_clusters` table (50 rows)
- `opinions` table (50 rows)
- `opinions_cited` table (100+ rows)

### Fetch Multiple Judges

```bash
# Create a script
echo "python manage.py fetch_judge_complete 1713 --max-opinions=20
python manage.py fetch_judge_complete 3045 --max-opinions=20
python manage.py fetch_judge_complete 2776 --max-opinions=20" > fetch_all.sh

chmod +x fetch_all.sh
./fetch_all.sh
```

---

## 🔍 PART 8: HOW EMBEDDINGS ENABLE SMART QUERIES

### Traditional Keyword Search ❌
```
Query: "constitutional rights"
Only finds: documents with exact words "constitutional" AND "rights"
Misses: "First Amendment protections", "due process", "civil liberties"
```

### Semantic Search with Embeddings ✅
```
Query: "constitutional rights"
Finds:
  - "First Amendment protections" (similar meaning)
  - "due process violations" (related concept)
  - "civil liberties framework" (related concept)
  - "Fourth Amendment search" (similar meaning)
```

**Why?** Embeddings capture **meaning**, not just words.

---

## 📊 PART 9: API ENDPOINTS SUMMARY

| Endpoint | Method | Purpose | Returns |
|----------|--------|---------|---------|
| `/api/statistics/` | GET | Platform stats | Counts of judges, cases, opinions |
| `/api/agents/semantic-search/` | POST | Vector search | Similar opinions/cases/judges |
| `/api/legal-research-advanced/` | POST | AI legal research | GPT-4 analysis + cases |
| `/api/judges/<id>/complete_profile/` | GET | Full judge data | Bio + cases + opinions |
| `/api/judges/<id>/cases/` | GET | Judge's cases | List of cases |
| `/api/agents/case-prediction/` | POST | Predict outcome | Success probability |
| `/api/opinions/<id>/` | GET | Opinion details | Full opinion text |
| `/api/cases/<id>/` | GET | Case details | Docket information |

---

## 🧪 PART 10: QUICK TEST

```bash
# Run all tests
./test_agents.sh
```

**Tests**:
1. ✅ Platform statistics
2. ✅ Semantic search
3. ✅ Legal research (AI)
4. ✅ Judge profile
5. ✅ Judge cases
6. ✅ Case prediction

---

## 🎯 PART 11: REAL WORLD EXAMPLE

### Scenario: Agent Queries "First Amendment social media cases"

**Step 1**: Agent calls semantic search
```bash
POST /api/agents/semantic-search/
{"query": "First Amendment social media cases"}
```

**Step 2**: System generates embedding
```
"First Amendment social media cases" 
→ [0.234, -0.567, 0.123, ...] (1536 numbers)
```

**Step 3**: pgvector searches database
```sql
SELECT opinion_id, plain_text,
       embedding <=> '[0.234, -0.567, ...]' AS distance
FROM opinions
ORDER BY distance
LIMIT 10
```

**Step 4**: Returns relevant cases
```json
{
  "results": [
    {
      "title": "NetChoice v. Fitch",
      "excerpt": "Texas law compelling content moderation violates First Amendment..."
    },
    {
      "title": "Moody v. NetChoice",  
      "excerpt": "Florida's social media law unconstitutional..."
    }
  ]
}
```

**Step 5**: If using AI research endpoint, GPT-4 analyzes
```
"Based on NetChoice v. Fitch (2025), the Supreme Court held that 
state laws requiring social media platforms to host certain content 
violate the First Amendment..."
```

---

## 📝 SUMMARY

**Data Flow**:
```
CourtListener API 
  → Python Service (`courtlistener_service.py`)
  → Data Processors (`data_processors.py`)
  → Generate Embeddings (OpenAI)
  → Save to PostgreSQL
  → Store embeddings in pgvector
```

**Query Flow**:
```
User Question 
  → Agent calls API endpoint
  → Generate query embedding (OpenAI)
  → Search database (pgvector)
  → Optional: AI analysis (GPT-4)
  → Return results to agent
```

**Key Components**:
- **PostgreSQL**: Stores all legal data
- **pgvector**: Enables semantic search
- **OpenAI**: Generates embeddings & AI analysis
- **Django REST**: API framework
- **CourtListener**: Legal data source

---

## ⚙️ Configuration

**Required in `.env`**:
```bash
COURTLISTENER_API_KEY=your-key-here
OPENAI_API_KEY=your-openai-key-here
```

**Database**:
```
Name: legal_agent_db
User: legal_agent_user
Extension: pgvector
```

---

## 🚦 Current Status

**Data Loaded**:
- 2 judges (Brett Kavanaugh, Sonia Sotomayor)
- 20 cases
- 10 opinions
- 10 courts
- All with embeddings ✅

**Working Features**:
- ✅ Semantic search
- ✅ AI legal research
- ✅ Judge profiles
- ✅ Case predictions
- ✅ Citation network

**Ready for**:
- Frontend integration
- More data ingestion
- Production deployment

---

## 🎓 Key Concepts

1. **Embeddings** = Converting text to numbers that represent meaning
2. **Vector Search** = Finding similar items by comparing number patterns
3. **Semantic Search** = Search by meaning, not keywords
4. **Opinion Cluster** = A case decision (may have multiple opinions)
5. **Citation Network** = How cases reference each other

---

**System is fully operational and ready to use!** 🚀
