# Philata Immigration Website - Comprehensive Report

## Document Overview
**Generated:** January 11, 2026
**Purpose:** Complete documentation of all website sections, inputs collected, calculations performed, and outcomes provided

---

# TABLE OF CONTENTS

1. [Eligibility Checker (RCIC-Style Consultation Tool)](#1-eligibility-checker)
2. [CRS Score Calculator](#2-crs-score-calculator)
3. [PNP Calculator](#3-pnp-calculator)
4. [NOC Code Finder](#4-noc-code-finder)
5. [Language Score Converter](#5-language-score-converter)
6. [Document Checklist Generator](#6-document-checklist-generator)
7. [Cost Calculator](#7-cost-calculator)
8. [Immigration Targets Display](#8-immigration-targets-display)
9. [Processing Times](#9-processing-times)
10. [CRS Score Prediction](#10-crs-score-prediction)
11. [Express Entry Pool Statistics](#11-express-entry-pool-statistics)

---

# 1. ELIGIBILITY CHECKER

## Purpose
Comprehensive RCIC-style consultation tool that assesses immigration pathways and provides personalized recommendations.

## Information Collected (10 Steps, 50+ Questions)

### Step 1: Personal Information
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Age | What is your age? | 18-24, 25-29, 30-34, 35-39, 40-44, 45-49, 50+ | Age affects CRS score - peaks at 20-29 |
| Marital Status | Are you married or common-law? | Single, Married/Common-law, Divorced/Separated | Determines if spouse factors apply |
| Spouse Accompanying | Will spouse come to Canada? | Yes, No | Affects CRS calculation method |
| Country of Citizenship | What is your citizenship? | Dropdown of countries | Affects visa requirements |
| Current Location | Where do you currently live? | In Canada, Outside Canada | Determines inland vs outland streams |

### Step 2: Status in Canada (if applicable)
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Immigration Status | Current status in Canada? | Work Permit (Employer-specific), Work Permit (Open/PGWP), Study Permit, Visitor, Implied Status, No valid status | Determines available programs |
| Permit Expiry | When does permit expire? | Date picker | Urgency affects strategy |
| Time in Canada | How long in Canada continuously? | <6 months, 6-12 months, 1-2 years, 2-3 years, 3+ years | Affects Canadian experience counting |

### Step 3: Education
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Education Level | Highest completed education? | Less than high school, High school, 1-year post-secondary, 2-year diploma, 3-year bachelor's, Two+ degrees, Master's, PhD | Worth up to 150 CRS points |
| Education Country | Where completed? | Canada, Outside Canada | Canadian education provides bonus points |
| Canadian Education Level | Canadian credential type? | 1-year certificate, 2-year diploma, Bachelor's, Master's, PhD | Adds 15-30 bonus CRS points |
| Field of Study | What field? | Computer Science/IT, Engineering, Healthcare, Trades, Business, Science, Education, Agriculture, Transport, Hospitality, Arts, Social Sciences, Law, Other | Determines category-based draw eligibility |
| ECA Status | Have Educational Credential Assessment? | Yes (completed), In progress, No (not started) | REQUIRED for Express Entry |
| Professional Certifications | Any professional licenses? | CPA, P.Eng, Nursing License, Medical License, Red Seal, Teaching Certificate, PMP, IT Certs, None | Helps with job offers and PNP streams |

### Step 4: Work Experience & Occupation
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Current Occupation | Job title? | Searchable NOC database (200+ occupations) | Determines NOC code and TEER level |
| Years in Occupation | How long in this occupation? | <1 year, 1-5+ years | Worth up to 80 CRS points |
| Foreign Work Experience | Skilled work outside Canada? | None, 1-6+ years | Adds up to 50 CRS points |
| Canadian Work Experience | Skilled work in Canada? | None, 1-5+ years | Adds up to 80 CRS points, required for CEC |
| Work Province | Province worked in? | All provinces | Required for PNP eligibility |
| Trade Certification | Canadian trade certificate? | Red Seal, Provincial, No | Qualifies for FST program |

### Step 5: Language Proficiency
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| English Test Taken | Which test? | IELTS General, CELPIP General, PTE Core, Not yet | REQUIRED for Express Entry |
| English Speaking | Speaking CLB score? | CLB 4-10+ | Language worth up to 136 CRS points |
| English Listening | Listening CLB score? | CLB 4-10+ | |
| English Reading | Reading CLB score? | CLB 4-10+ | |
| English Writing | Writing CLB score? | CLB 4-10+ | |
| French Proficiency | French language level? | NCLC 7+, NCLC 5-6, Below NCLC 5, None | French bonus + French category draws |
| Test Expiry Date | When was test taken? | Date picker | Tests valid for 2 years only |

### Step 6: Job Offer & Provincial Connections
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Has Job Offer | Valid job offer from Canadian employer? | Yes, No, In discussion | Adds 50-200 CRS points |
| Job Offer LMIA | Is offer LMIA-supported? | LMIA-approved, LMIA-exempt, Not sure, No LMIA | Only LMIA offers count for points |
| Job Offer NOC | NOC TEER level of offer? | TEER 0-5 | Senior management gets 200 points |
| Job Offer Province | Province of job offer? | All provinces | Determines PNP stream eligibility |
| Provincial Connection | Connections to a province? | Previous work, Previous study, Family, Job offer, Currently living, None | Often required for PNP |
| Target Province | Preferred province? | All provinces + Open to any | Some provinces have easier pathways |

### Step 7: Family & Financial
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Family in Canada | Close family who are citizens/PRs? | Sibling, Parent/grandparent, Adult child, Aunt/Uncle/Cousin, None | Sibling adds 15 CRS points |
| Settlement Funds | Proof of funds available? | Yes (meet minimum), Yes (exceed), Can arrange, Difficult | REQUIRED for FSW/FST |

### Step 8: Spouse/Partner Details (if applicable)
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Spouse Education | Spouse's education level? | Same as main applicant | Adds up to 10 CRS points |
| Spouse Language | Spouse's English CLB? | CLB 4-9+ | Spouse CLB 5+ adds up to 20 points |
| Spouse Canadian Experience | Spouse's Canadian work? | None, 1-2+ years | Adds up to 10 CRS points |

### Step 9: Previous Applications & Admissibility
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Previous Refusals | Ever refused a Canadian visa? | No, Yes once, Yes multiple times | Affects strategy, may need explanation |
| Medical Issues | Medical conditions affecting admissibility? | No, Yes but manageable, Yes significant, Not sure | Medical inadmissibility can prevent PR |
| Criminal History | Any criminal history? | No, Minor offense, Serious offense | Criminal inadmissibility is major barrier |

### Step 10: Goals & Timeline
| Field | Question | Options | Why It Matters |
|-------|----------|---------|----------------|
| Primary Goal | Main immigration goal? | PR ASAP, Work then PR, Study then PR, Not sure | Determines direct PR vs staged pathway |
| Timeline | Ideal timeline? | ASAP, 1 year, 2 years, 2-3 years, Flexible | Affects whether to wait or apply now |

---

## Calculations Performed

### CRS Score Calculation
- **Age Points:** 0-110 (single) / 0-100 (married)
- **Education Points:** 0-150 (single) / 0-140 (married)
- **Language Points:** 0-136 per ability (first language)
- **Second Language Points:** 0-24 (max)
- **Canadian Work Experience:** 0-80 points
- **Spouse Factors:** Up to 40 points total
- **Skill Transferability:** Up to 100 points
- **Additional Factors:** Provincial nomination (+600), Sibling (+15), French bonus (+25-50), Canadian education (+15-30)

### FSW 67-Point Assessment
- Education: up to 25 points
- Language (English): up to 24 points
- Language (French): up to 24 points
- Work Experience: up to 15 points
- Age: up to 12 points
- Arranged Employment: up to 10 points
- Adaptability: up to 10 points

### Provincial Scoring (7 Provinces)
1. **BC PNP SIRS** (0-200 points): Job offer, wage, NOC, experience, education, language, regional bonus
2. **Saskatchewan SINP** (0-100 points): Education, experience, language, age, connections
3. **Manitoba MPNP** (0-1000 points): Connections, language, experience, education, age, regional
4. **Alberta AAIP** (0-100 points): Language, education, Alberta connection, experience
5. **New Brunswick NBPNP** (0-100 points): Language, education, experience, connection, age
6. **PEI PNP** (0-100 points): Age, language, education, experience, connection, employment
7. **Newfoundland NLPNP** (0-100 points): Job offer, language, education, experience, connection

---

## Outcomes Provided

### 1. Program Eligibility Assessment
- **Programs Evaluated:** FSW, CEC, FST, PNP streams, AIP, RNIP
- **For Each Program:**
  - Eligible/Not Eligible status
  - Detailed requirement checklist (met/not met)
  - Specific recommendation text

### 2. CRS Score Estimate
- Total estimated CRS score
- Breakdown by category (Core, Spouse, Skill Transferability, Additional)
- Comparison to recent draw cutoffs

### 3. Provincial Pathway Recommendations
- Ranked list of best provinces for the profile
- Match quality (Excellent/Good/Moderate/Low)
- Specific stream recommendations
- Provincial score estimates

### 4. Score Improvement Suggestions
- Personalized tips with point gains
- Actions like: improve language, get Canadian experience, learn French, get PNP nomination
- Estimated point increase for each action

### 5. Career Transition Recommendations
- If current occupation has TEER issues
- Suggested target occupations with higher TEER
- Path to transition
- Benefit explanation

### 6. Alternative Pathways
- Study → PGWP → CEC pathway
- Atlantic Immigration Program
- Rural and Northern Immigration Pilot
- Each with pros/cons and timeline

### 7. Red Flags & Warnings
- Urgent issues (expiring documents)
- Concerns (gaps in history)
- Informational alerts (score below cutoff)

---

# 2. CRS SCORE CALCULATOR

## Purpose
Calculate Comprehensive Ranking System (CRS) score for Express Entry with detailed breakdown.

## Information Collected

| Section | Fields | Options |
|---------|--------|---------|
| Marital Status | Single/Married, Spouse coming | Radio buttons |
| Age | Age selection | 17-45+ dropdown |
| Education | Highest education, Canadian credentials | Education levels, None/1-2yr/3yr+ |
| First Language | Test type, Speaking/Listening/Reading/Writing | IELTS/CELPIP/PTE/TEF/TCF, CLB 4-10+ |
| Second Language | Speaking/Listening/Reading/Writing | CLB 5-9+ or None |
| Work Experience | Canadian years, Foreign years | 0-5+ years each |
| Spouse Factors | Education, Language, Canadian experience | Same scales |
| Additional | Provincial nomination, Sibling in Canada, French bonus | Yes/No, Bonus levels |

## Calculations
- Age points (single vs married tables)
- Education points (single vs married tables)
- Language points per ability
- Canadian work experience points
- Foreign work experience (for skill transferability)
- Skill transferability combinations
- Additional factors (PNP +600, Sibling +15, French +25-50)

## Outcomes
- **Total CRS Score** (out of 1,200)
- **Score Breakdown:**
  - Core/Human Capital points
  - Spouse Factors points
  - Skill Transferability points
  - Additional Points
- **Score Status:** Excellent/Good/Needs Improvement
- **ITA Prediction Panel:**
  - Chance percentage
  - Predicted next cutoff
  - Points needed to improve
  - Recent draws display
  - Personalized improvement tips

---

# 3. PNP CALCULATOR

## Purpose
Calculate points for Provincial Nominee Programs across all Canadian provinces.

## Provinces Covered

### Points-Based Calculators (with scoring)
1. **BC PNP (SIRS)** - 0-200 points
2. **Ontario OINP (EOI)** - 0-66 points

### Eligibility Checkers (stream-based)
3. **Alberta** - 4 streams
4. **Saskatchewan** - 4 streams
5. **Manitoba** - 3 streams
6. **Nova Scotia** - 3 streams
7. **New Brunswick** - 3 streams
8. **PEI** - 3 streams
9. **Newfoundland** - 3 streams
10. **NWT** - 3 streams
11. **Yukon** - 2 streams

## Information Collected
| Section | Fields |
|---------|--------|
| Job Offer | Has offer, Hourly wage/Salary, NOC TEER, Regional location |
| Work Experience | Total years, Canadian years, Months in province |
| Education | Level, Canadian credential, BC/Provincial credential |
| Language | English CLB, French NCLC |
| Immigration Status | Work permit, Express Entry profile, CRS score |

## Calculations

### BC PNP SIRS (example)
- Job Offer: 0-60 points (wage-based + NOC bonus)
- Work Experience: 0-35 points
- Education: 0-30 points
- Language: 0-30 points
- Regional bonus: 0-10 points

### Ontario OINP EOI (example)
- Job Offer NOC: 0-10 points
- Earnings: 0-3 points
- Canadian Experience: 0-4 points
- Education: 0-10 points
- Language: 0-10 points
- Outside GTA: 0-10 points
- French bonus: 0-10 points

## Outcomes
- **For Points-Based:** Total provincial score, breakdown, competitive status
- **For Eligibility:** Stream-by-stream eligibility with requirement checklist
- **Tips to Improve** personalized suggestions
- **Compare All Provinces** - check eligibility across all provinces at once

---

# 4. NOC CODE FINDER

## Purpose
Find National Occupational Classification (NOC) code for any occupation.

## Information Collected
- Search query (job title, keywords, or NOC code)

## Database
- 200+ occupations across all TEER levels (0-5)
- Categories: Management, Natural Sciences, Health, Education, Business, Law, Sales, Service, Trades, Transport, Labour, Manufacturing, Agriculture

## Outcomes

### For Each Matching Occupation:
- **NOC Code** (5-digit)
- **Title** (official occupation name)
- **TEER Level** (0-5 with color coding)
- **Category** (broad classification)
- **Program Eligibility Badges:**
  - FSW (TEER 0-1 only)
  - CEC (TEER 0-3)
  - FST (TEER 3 trades)
  - PNP (all)
  - LMIA Work Permit (all)
- **Details:**
  - Education level required
  - Express Entry points eligibility
  - LMIA eligibility

### TEER Guide Reference
- TEER 0: Management (university degree + experience)
- TEER 1: Professional (university degree)
- TEER 2: Technical (college diploma, 2+ years training)
- TEER 3: Skilled Trades (apprenticeship)
- TEER 4: Intermediate (high school)
- TEER 5: Labour (short-term training)

---

# 5. LANGUAGE SCORE CONVERTER

## Purpose
Convert language test scores (IELTS, CELPIP, TEF, TCF) to CLB/NCLC levels.

## Information Collected

| Test Type | Abilities | Score Ranges |
|-----------|-----------|--------------|
| IELTS General Training | Listening, Reading, Writing, Speaking | 0-9 bands |
| CELPIP General | Listening, Reading, Writing, Speaking | 4-12 |
| TEF Canada | Listening (0-360), Reading (0-300), Writing (0-450), Speaking (0-450) | Score ranges |
| TCF Canada | Listening (331-699), Reading (331-699), Writing (0-20), Speaking (0-20) | Score ranges |

## Calculations
- Conversion tables mapping each test score to CLB 4-10+
- Different conversion for each ability
- Minimum CLB calculation (lowest across all abilities)

## Outcomes
- **CLB Level for Each Ability:** Listening, Reading, Writing, Speaking
- **Minimum CLB:** Lowest of the four (used for program eligibility)
- **CRS Points Estimate:**
  - Single applicant points
  - Married applicant points
- **Reference Tables:** Full conversion charts for each test type
- **Test Validity Reminder:** 2-year validity notice

---

# 6. DOCUMENT CHECKLIST GENERATOR

## Purpose
Generate personalized document checklists for immigration applications.

## Information Collected
- **Program Selection:**
  - Federal Skilled Worker (FSW)
  - Canadian Experience Class (CEC)
  - Federal Skilled Trades (FST)
  - Provincial Nominee Program (PNP)
  - Study Permit
  - Work Permit

## Document Categories

### Identity Documents
- Valid passport (all pages)
- National ID card
- Birth certificate
- Marriage certificate (if applicable)
- Divorce certificate (if applicable)

### Education Documents
- Educational credentials (degrees, diplomas)
- Transcripts
- Educational Credential Assessment (ECA) report
- Professional licenses/certifications

### Work Experience Documents
- Reference letters from employers
- Employment contracts
- Pay stubs / tax documents
- Business registration (if self-employed)

### Language Documents
- IELTS/CELPIP/PTE/TEF/TCF results
- Test result validity check

### Financial Documents
- Bank statements (6+ months)
- Proof of settlement funds
- Investment statements
- Property documents (if applicable)

### Additional Documents
- Police certificates (all countries lived 6+ months)
- Medical examination results
- Photos (IRCC specifications)
- Proof of Canadian ties (job offer, family, etc.)

## Outcomes
- **Personalized Checklist** based on program
- **Document Status Tracking:** Required, Optional, If Applicable
- **Progress Indicator:** Percentage complete
- **Print/PDF Export** functionality
- **Notes Section** for each document

---

# 7. COST CALCULATOR

## Purpose
Estimate total immigration costs including government fees, third-party fees, and settlement costs.

## Information Collected
| Field | Options |
|-------|---------|
| Program Type | Express Entry, PNP, Study Permit, Work Permit |
| Number of Adults | 1-5 |
| Number of Children | 0-5 |
| Optional Services | ECA, Language test, Medical exam, Police certificates, Legal fees, etc. |

## Fee Database

### Government Fees (CAD)
| Fee Type | Amount |
|----------|--------|
| PR Processing Fee (adult) | $950 |
| Right of Permanent Residence Fee | $575 |
| PR Processing Fee (child) | $260 |
| Provincial Nomination Fee | ~$300 (varies) |
| Study Permit | $150 |
| Work Permit | $155 |
| Biometrics | $85 (individual) / $170 (family max) |
| Visitor Visa | $100 |

### Third-Party Fees (estimated)
| Service | Cost Range |
|---------|------------|
| ECA Assessment | $200-400 |
| Language Test (IELTS/CELPIP) | $300-350 |
| Medical Exam | $200-450 |
| Police Certificates | $50-150 per country |
| Document Translation | $50-150 per document |

### Settlement Funds Requirements
| Family Size | Minimum Funds (CAD) |
|-------------|---------------------|
| 1 person | $14,690 |
| 2 people | $18,288 |
| 3 people | $22,483 |
| 4 people | $27,315 |
| 5 people | $30,980 |
| 6 people | $34,942 |
| 7 people | $38,905 |

## Outcomes
- **Total Cost Estimate** in CAD
- **Itemized Breakdown:**
  - Government Fees
  - Third-Party Fees
  - Settlement/Travel Costs
- **Per-Person Breakdown**
- **Notes on Fee Exemptions** (CEC doesn't require settlement funds with valid job offer)

---

# 8. IMMIGRATION TARGETS DISPLAY

## Purpose
Display Canada's Immigration Levels Plan with annual targets.

## Information Collected
- Year selection (2024, 2025, 2026)

## Data Displayed

### Overall Targets
| Year | Total PR Target | Express Entry | PNP | Family | Refugees |
|------|-----------------|---------------|-----|--------|----------|
| 2024 | 485,000 | 110,770 | 110,000 | 114,000 | 76,000 |
| 2025 | 500,000 | 124,000 | 117,500 | 118,000 | 76,000 |
| 2026 | 395,000 | 109,000 | 82,000 | 78,000 | 45,000 |

### Provincial Allocations
- Provincial quota distributions
- Year-over-year changes

### Category Breakdowns
- Express Entry subcategories
- Family class subcategories
- Refugee categories

## Outcomes
- **Visual Charts** showing targets
- **Year-over-Year Comparison**
- **Trend Analysis** (increasing/decreasing)
- **Government Reasoning** explanations
- **Impact on Applicants** insights

---

# 9. PROCESSING TIMES

## Purpose
Display current IRCC processing times for all application types.

## Categories Displayed

### Express Entry Programs
| Application | Processing Time | Status |
|-------------|-----------------|--------|
| FSW | 6 months | On Track |
| CEC | 5 months | On Track |
| FST | 6 months | On Track |

### Temporary Residence
| Application | Processing Time | Status |
|-------------|-----------------|--------|
| Visitor Visa (TRV) | 45 days | Delays |
| Study Permit | 8 weeks | On Track |
| Work Permit (LMIA) | 12 weeks | Delays |
| PGWP | 80 days | On Track |
| Visitor Extension | 120 days | Backlog |

### Family Sponsorship
| Application | Processing Time | Status |
|-------------|-----------------|--------|
| Spouse (Inland) | 12 months | On Track |
| Spouse (Outland) | 12 months | On Track |
| Parents & Grandparents | 24 months | Backlog |
| Super Visa | 60 days | On Track |

### PNP Programs
| Application | Processing Time | Status |
|-------------|-----------------|--------|
| PNP Express Entry | 6 months | On Track |
| PNP Paper-based | 18 months | Delays |
| Ontario PNP | 3-6 months | On Track |
| BC PNP | 2-4 months | On Track |
| Alberta PNP | 3-5 months | On Track |

### Country-Specific Processing Times
- 16 countries displayed with visitor/study/work times
- Regions: Asia, Americas, Europe, Africa, Oceania

## Outcomes
- **Processing Time Display** with progress bars
- **Status Indicators:** On Track, Delays, Backlog
- **Country Filter** by region
- **Immigration Statistics:**
  - 2025 targets
  - Average CRS cutoff
  - Pool size
- **Application Fees Table**
- **Important Dates & Deadlines:**
  - Profile validity (12 months)
  - ITA response time (60 days)
  - Document validity periods
  - Status restoration deadline (90 days)

---

# 10. CRS SCORE PREDICTION

## Purpose
AI-powered Express Entry draw predictions based on historical IRCC data.

## Information Collected
- User's CRS score (for ITA chances check)

## Predictions Provided

### Next Draw Prediction
- Predicted CRS cutoff
- Expected ITAs to be issued
- Expected date
- Target programs (FSW/CEC/etc.)
- Draw category (General/Healthcare/French/etc.)
- Draw frequency

### Category-Based Predictions
| Category | Predicted Cutoff | Likelihood |
|----------|-----------------|------------|
| General | ~520 | Likely Next |
| Healthcare | ~430 | Possible |
| STEM | ~480 | Possible |
| French | ~380 | Possible |
| Trades | ~420 | Possible |
| Transport | ~440 | Possible |

### Analysis Report
- Prediction summary with reasoning
- Key factors affecting prediction:
  - Recent CEC cutoff trends
  - Draw frequency patterns
  - ITA volume analysis
  - 2026 target implications
- Draw pattern table by category
- Confidence meter (percentage)

## Outcomes
- **ITA Chances Calculator:**
  - Input your score
  - Get probability percentage
  - Points above/below cutoff
  - Categories eligible for
- **Recent Draws History** (last 5-10 draws)
- **Prediction Methodology** explanation
- **Official Data Sources** links

---

# 11. EXPRESS ENTRY POOL STATISTICS

## Purpose
Understand your position in the Express Entry pool and ITA chances.

## Information Collected
- User's CRS score (for position calculation)
- Year selection (2024, 2025, 2026)

## Statistics Displayed

### Pool Overview
- Total candidates in pool (~235,000)
- Average pool score (~486)
- Latest CRS cutoff
- Total ITAs issued (year-to-date)

### Pool Distribution
| Score Range | Candidates | Percentage |
|-------------|-----------|------------|
| 601-1200 | ~4,700 | 2% |
| 501-600 | ~35,250 | 15% |
| 451-500 | ~82,250 | 35% |
| 401-450 | ~70,500 | 30% |
| 351-400 | ~28,200 | 12% |
| 0-350 | ~14,100 | 6% |

### Recent Draw History
- Date, Draw Type, CRS Score, ITAs Issued

## Outcomes
- **Pool Position Calculator:**
  - Estimated pool rank
  - Candidates above you
  - Points to latest cutoff
  - ITA probability assessment
- **Visual Pool Distribution** bars
- **Insights:**
  - Best path for low scores
  - Pool growth trends
  - Draw frequency patterns

---

# SUMMARY OF ALL TOOLS

| Tool | Inputs | Main Calculation | Primary Outcome |
|------|--------|------------------|-----------------|
| Eligibility Checker | 50+ questions | CRS, FSW 67-point, Provincial scores | Pathway recommendations |
| CRS Calculator | Age, education, language, work, spouse | CRS score | Score out of 1,200 |
| PNP Calculator | Job, experience, education, language | Provincial points | Provincial eligibility |
| NOC Finder | Job search query | Database lookup | NOC code + TEER level |
| Language Converter | Test scores | CLB conversion tables | CLB levels |
| Document Checklist | Program type | Checklist generation | Required documents |
| Cost Calculator | Program, family size | Fee summation | Total cost estimate |
| Immigration Targets | Year | Data display | Annual targets |
| Processing Times | None (display only) | None | Current wait times |
| CRS Prediction | CRS score (optional) | Trend analysis | Next draw prediction |
| Pool Statistics | CRS score (optional) | Pool position | Rank + probability |

---

# DATA SOURCES

All data is sourced from official government websites:
- IRCC Express Entry Rounds: https://www.canada.ca/en/immigration-refugees-citizenship/services/immigrate-canada/express-entry/submit-profile/rounds-invitations.html
- IRCC Processing Times: https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html
- Immigration Levels Plan: https://www.canada.ca/en/immigration-refugees-citizenship/news/notices/supplementary-immigration-levels-2025-2027.html
- Provincial PNP websites (BC, Ontario, Alberta, Saskatchewan, Manitoba, etc.)

---

**Report Generated:** January 11, 2026
**Version:** 1.0
**For Questions:** Contact website administrator
