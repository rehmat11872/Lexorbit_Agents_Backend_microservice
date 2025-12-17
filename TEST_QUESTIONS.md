# 🧪 Legal Research API - General Test Questions

## Comprehensive Test Questions for Legal AI Agent

---

## 📋 **SECTION 1: TORT LAW**

### Negligence & Liability

```bash
# Question 1: Elements of Negligence
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the elements of negligence in tort law?"
  }'
```

```bash
# Question 2: Duty of Care
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "duty of care reasonable person standard foreseeability"
  }'
```

```bash
# Question 3: Proximate Cause
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "proximate cause but-for causation tort liability"
  }'
```

```bash
# Question 4: Strict Liability
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "strict liability products liability dangerous activities"
  }'
```

```bash
# Question 5: Comparative Negligence
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "comparative negligence contributory negligence fault allocation"
  }'
```

---

## 📜 **SECTION 2: CONTRACT LAW**

### Contract Formation & Enforcement

```bash
# Question 6: Promissory Estoppel
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Explain the doctrine of promissory estoppel in contract law"
  }'
```

```bash
# Question 7: Contract Formation
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "offer acceptance consideration mutual assent contract formation"
  }'
```

```bash
# Question 8: Breach of Contract
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "material breach anticipatory breach contract remedies"
  }'
```

```bash
# Question 9: Statute of Frauds
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "statute of frauds written agreement real estate contracts"
  }'
```

```bash
# Question 10: Specific Performance
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "specific performance equitable remedy contract enforcement"
  }'
```

---

## 🏠 **SECTION 3: PROPERTY LAW**

### Real & Personal Property

```bash
# Question 11: Adverse Possession
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "adverse possession property rights continuous exclusive possession"
  }'
```

```bash
# Question 12: Easements
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "easement by necessity express easement property rights"
  }'
```

```bash
# Question 13: Fee Simple vs Life Estate
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fee simple absolute life estate property ownership interests"
  }'
```

```bash
# Question 14: Eminent Domain
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "eminent domain taking just compensation public use"
  }'
```

---

## ⚖️ **SECTION 4: CRIMINAL LAW**

### Criminal Liability & Defenses

```bash
# Question 15: Mens Rea
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mens rea criminal intent actus reus guilty mind"
  }'
```

```bash
# Question 16: Self-Defense
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "self-defense justification imminent threat reasonable force"
  }'
```

```bash
# Question 17: Insanity Defense
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "insanity defense McNaughten rule diminished capacity"
  }'
```

```bash
# Question 18: Felony Murder Rule
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "felony murder rule constructive malice dangerous felony"
  }'
```

---

## 🏛️ **SECTION 5: CONSTITUTIONAL LAW**

### Fundamental Rights & Principles

```bash
# Question 19: Due Process Clause
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "procedural due process substantive due process fundamental rights"
  }'
```

```bash
# Question 20: Equal Protection
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "equal protection clause strict scrutiny suspect classification"
  }'
```

```bash
# Question 21: Commerce Clause
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "commerce clause federal power interstate commerce regulation"
  }'
```

```bash
# Question 22: Separation of Powers
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "separation of powers checks and balances executive legislative judicial"
  }'
```

---

## 🏢 **SECTION 6: CORPORATE & BUSINESS LAW**

### Business Entities & Liability

```bash
# Question 23: Piercing Corporate Veil
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "piercing corporate veil alter ego liability shareholder protection"
  }'
```

```bash
# Question 24: Fiduciary Duty
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fiduciary duty loyalty care corporate directors shareholders"
  }'
```

```bash
# Question 25: Business Judgment Rule
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "business judgment rule director liability corporate decisions"
  }'
```

---

## 📝 **SECTION 7: CIVIL PROCEDURE**

### Procedural Rules & Standards

```bash
# Question 26: Personal Jurisdiction
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "personal jurisdiction minimum contacts long-arm statute"
  }'
```

```bash
# Question 27: Summary Judgment
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "summary judgment genuine issue material fact motion standard"
  }'
```

```bash
# Question 28: Class Actions
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "class action certification numerosity commonality adequacy representation"
  }'
```

```bash
# Question 29: Discovery Rules
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "discovery rules interrogatories depositions privilege"
  }'
```

---

## 📊 **SECTION 8: QUESTIONS WITH FILTERS**

### Filtered Searches

```bash
# Question 30: Federal Jurisdiction Filter
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "breach of contract damages remedies",
    "filters": {
      "jurisdiction": "federal"
    }
  }'
```

```bash
# Question 31: Supreme Court Only
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "property rights takings clause compensation",
    "filters": {
      "court_level": "supreme"
    }
  }'
```

```bash
# Question 32: Recent Cases (Date Filter)
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "negligence tort liability standard of care",
    "filters": {
      "date_from": "2020-01-01"
    }
  }'
```

```bash
# Question 33: Specific Judge
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract interpretation ambiguity construction",
    "filters": {
      "judge_name": "Kavanaugh"
    }
  }'
```

```bash
# Question 34: Multiple Filters
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "administrative law agency authority deference",
    "filters": {
      "jurisdiction": "federal",
      "court_level": "supreme",
      "date_from": "2024-01-01"
    }
  }'
```

---

## 👨‍👩‍👧 **SECTION 9: FAMILY LAW**

```bash
# Question 35: Child Custody
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "child custody best interests standard parental rights"
  }'
```

```bash
# Question 36: Divorce & Alimony
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "divorce grounds spousal support alimony maintenance"
  }'
```

```bash
# Question 37: Property Division
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "marital property division community property equitable distribution"
  }'
```

---

## 💼 **SECTION 10: EMPLOYMENT LAW**

```bash
# Question 38: Wrongful Termination
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "wrongful termination at-will employment public policy exception"
  }'
```

```bash
# Question 39: Discrimination
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "employment discrimination Title VII protected classes"
  }'
```

```bash
# Question 40: Workers Compensation
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "workers compensation workplace injury exclusive remedy"
  }'
```

---

## 🌍 **SECTION 11: ENVIRONMENTAL LAW**

```bash
# Question 41: NEPA Requirements
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "environmental impact statement NEPA requirements federal actions"
  }'
```

```bash
# Question 42: Clean Water Act
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Clean Water Act wetlands protection navigable waters"
  }'
```

```bash
# Question 43: Endangered Species Act
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Endangered Species Act critical habitat incidental take"
  }'
```

---

## 📚 **SECTION 12: EVIDENCE LAW**

```bash
# Question 44: Hearsay Rule
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "hearsay rule exceptions excited utterance present sense impression"
  }'
```

```bash
# Question 45: Privilege
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "attorney-client privilege work product doctrine confidential communications"
  }'
```

```bash
# Question 46: Expert Testimony
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "expert witness testimony Daubert standard reliability"
  }'
```

---

## 🏦 **SECTION 13: BANKRUPTCY LAW**

```bash
# Question 47: Chapter 7 vs Chapter 11
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "bankruptcy Chapter 7 liquidation Chapter 11 reorganization"
  }'
```

```bash
# Question 48: Discharge of Debts
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "discharge of debts bankruptcy exemptions non-dischargeable debts"
  }'
```

---

## 💡 **SECTION 14: INTELLECTUAL PROPERTY**

```bash
# Question 49: Copyright Fair Use
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "copyright fair use transformative use commercial purpose"
  }'
```

```bash
# Question 50: Patent Infringement
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "patent infringement literal infringement doctrine of equivalents"
  }'
```

```bash
# Question 51: Trademark Dilution
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "trademark dilution blurring tarnishment famous marks"
  }'
```

---

## 🔬 **SECTION 15: SEMANTIC SEARCH TESTS**

### Testing AI Understanding of Legal Concepts

```bash
# Question 52: Test Synonyms - "Damages" vs "Compensation"
curl -X POST "http://localhost:8000/api/agents/semantic-search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "monetary damages compensation injury harm",
    "max_results": 10
  }'
```

```bash
# Question 53: Test Related Concepts
curl -X POST "http://localhost:8000/api/agents/semantic-search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "legal obligation duty responsibility requirement",
    "max_results": 10
  }'
```

```bash
# Question 54: Test Legal Doctrines
curl -X POST "http://localhost:8000/api/agents/semantic-search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "reasonable person standard objective test foreseeability",
    "max_results": 15
  }'
```

---

## 🎯 **SECTION 16: CASE PREDICTION**

```bash
# Question 55: Predict Tort Case Outcome
curl -X POST "http://localhost:8000/api/agents/case-prediction/" \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "tort",
    "jurisdiction": "federal",
    "brief_summary": "Negligence claim involving car accident and duty of care"
  }'
```

```bash
# Question 56: Predict Contract Dispute
curl -X POST "http://localhost:8000/api/agents/case-prediction/" \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "contract",
    "jurisdiction": "federal",
    "brief_summary": "Breach of contract claim seeking specific performance"
  }'
```

```bash
# Question 57: Predict Property Dispute
curl -X POST "http://localhost:8000/api/agents/case-prediction/" \
  -H "Content-Type: application/json" \
  -d '{
    "case_type": "property",
    "jurisdiction": "state",
    "brief_summary": "Adverse possession claim over residential land"
  }'
```

---

## 📋 **SECTION 17: COMPLEX LEGAL QUESTIONS**

```bash
# Question 58: Multi-Part Tort Question
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "When can a plaintiff recover damages in negligence case considering duty breach causation and harm?"
  }'
```

```bash
# Question 59: Contract Formation Elements
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the essential elements for valid contract formation including offer acceptance and consideration?"
  }'
```

```bash
# Question 60: Constitutional Analysis
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do courts analyze government action under equal protection clause using different scrutiny levels?"
  }'
```

---

## 🔍 **SECTION 18: EDGE CASES**

### Short Queries

```bash
# Question 61: Single Legal Term
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "negligence"
  }'
```

```bash
# Question 62: Two-Word Query
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "contract breach"
  }'
```

### Legal Citations

```bash
# Question 63: With Case Name
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Hadley v. Baxendale foreseeability consequential damages"
  }'
```

```bash
# Question 64: With Statute Reference
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Section 1983 civil rights violation under color of law"
  }'
```

---

## 📊 **QUICK TEST SCRIPT**

Save this as `quick_test.sh`:

```bash
#!/bin/bash

echo "=== Quick Legal Research API Test ==="
echo ""

# Test 1: Tort Law
echo "Test 1: Negligence elements"
curl -s -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the elements of negligence in tort law?"}' | jq -r '.total_results'

# Test 2: Contract Law
echo "Test 2: Promissory estoppel"
curl -s -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "Explain the doctrine of promissory estoppel in contract law"}' | jq -r '.total_results'

# Test 3: Property Law
echo "Test 3: Adverse possession"
curl -s -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "adverse possession property rights continuous possession"}' | jq -r '.total_results'

# Test 4: With Filter
echo "Test 4: Federal jurisdiction filter"
curl -s -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{"query": "breach of contract damages", "filters": {"jurisdiction": "federal"}}' | jq -r '.total_results'

echo ""
echo "=== Tests Complete ==="
```

---

## 📖 **QUESTION CATEGORIES SUMMARY**

| Section | Topic | Questions |
|---------|-------|-----------|
| 1 | Tort Law | 5 |
| 2 | Contract Law | 5 |
| 3 | Property Law | 4 |
| 4 | Criminal Law | 4 |
| 5 | Constitutional Law | 4 |
| 6 | Corporate Law | 3 |
| 7 | Civil Procedure | 4 |
| 8 | Filtered Searches | 5 |
| 9 | Family Law | 3 |
| 10 | Employment Law | 3 |
| 11 | Environmental Law | 3 |
| 12 | Evidence Law | 3 |
| 13 | Bankruptcy Law | 2 |
| 14 | Intellectual Property | 3 |
| 15 | Semantic Search | 3 |
| 16 | Case Prediction | 3 |
| 17 | Complex Questions | 3 |
| 18 | Edge Cases | 4 |

**Total: 64 General Legal Questions**

---

## 🎯 **FILTER OPTIONS**

```json
{
  "filters": {
    "jurisdiction": "federal",        // or "state", "all"
    "court_level": "supreme",         // or "circuit", "district", "all"
    "date_from": "2024-01-01",        // YYYY-MM-DD
    "date_to": "2025-12-31",          // YYYY-MM-DD
    "judge_name": "Kavanaugh"         // Judge last name
  }
}
```

---

## ✅ **TESTING CHECKLIST**

Basic Legal Concepts:
- [ ] Tort law (negligence, liability)
- [ ] Contract law (formation, breach)
- [ ] Property law (ownership, rights)
- [ ] Criminal law (intent, defenses)
- [ ] Constitutional law (due process, equal protection)

Procedural Topics:
- [ ] Civil procedure (jurisdiction, discovery)
- [ ] Evidence (hearsay, privilege)
- [ ] Filters (jurisdiction, court level, dates)

Specialized Areas:
- [ ] Corporate law (fiduciary duty, veil piercing)
- [ ] Family law (custody, divorce)
- [ ] Employment law (discrimination, termination)
- [ ] Environmental law (NEPA, Clean Water Act)
- [ ] IP law (copyright, patent, trademark)
- [ ] Bankruptcy law (discharge, reorganization)

Advanced Features:
- [ ] Semantic search
- [ ] Case prediction
- [ ] Multi-part questions
- [ ] Edge cases (short queries, citations)

---

## 💡 **USAGE TIPS**

1. **Start with Basic Concepts:**
   ```bash
   curl ... -d '{"query": "What are the elements of negligence?"}'
   ```

2. **Add Specificity:**
   ```bash
   curl ... -d '{"query": "negligence duty of care breach causation damages"}'
   ```

3. **Use Filters:**
   ```bash
   curl ... -d '{
     "query": "contract breach remedies",
     "filters": {"jurisdiction": "federal"}
   }'
   ```

4. **Test Semantic Understanding:**
   - Use "compensation" instead of "damages"
   - Use "obligation" instead of "duty"
   - Use "wrongdoing" instead of "tort"

5. **Compare Results:**
   - Save responses: `curl ... > tort_question1.json`
   - Compare different phrasings of same question
   - Test with and without filters

---

## 🚀 **QUICK START**

```bash
# Make sure server is running
python manage.py runserver

# Download test data first
python manage.py fetch_judge_complete 1713 --max-opinions 20

# Test a question
curl -X POST "http://localhost:8000/api/legal-research-advanced/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the elements of negligence in tort law?"
  }' | jq .

# Run automated tests
./test_legal_questions.sh
```

---

**All 64 general legal questions ready to test your Legal AI Agent!** 🎓⚖️
