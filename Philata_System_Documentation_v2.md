# Philata Immigration Content System - Documentation v2
## Complete System Analysis & Change Log

**Document Date:** December 31, 2025
**Last Workflow Update:** 2025-12-31T18:25:38 UTC
**Version:** Caption v15 deployed

---

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Content Flow Architecture](#2-content-flow-architecture)
3. [Current Issues Identified](#3-current-issues-identified)
4. [Changes Made (Session Log)](#4-changes-made-session-log)
5. [Caption System (v15)](#5-caption-system-v15)
6. [Article Generation Analysis](#6-article-generation-analysis)
7. [Recommendations for Improvement](#7-recommendations-for-improvement)
8. [Configuration Reference](#8-configuration-reference)

---

## 1. System Overview

### Components
| Component | Technology | Purpose |
|-----------|------------|---------|
| n8n Workflow | Railway | Orchestrates content pipeline |
| Perplexity API | sonar-pro | AI content generation |
| Gemini API | Google | Image generation |
| Website | Flask/Railway | Content display & API |
| Cloudinary | Cloud | Image storage |

### Workflow ID
- **ID:** `JqWgdj9WKWNhPm9H`
- **URL:** `https://philata-n8n-production.up.railway.app`
- **Schedule:** Every 60 minutes (all 4 tracks)

### Content Tracks
| Track | Trigger | Content Type |
|-------|---------|--------------|
| Breaking | Hourly | Real-time news from last 24h |
| Regular | Hourly | General news from last 48h |
| Educational | Hourly | Guides, tips, how-tos |
| Forms | Hourly | IRCC form guides |

---

## 2. Content Flow Architecture

```
[Triggers: 4x Hourly]
       │
       ▼
[1a-1d. Fetch] ─── Perplexity API prompts
       │
       ▼
[2a-2d. Parse] ─── Extract JSON, build article
       │
       ▼
[3a-3d. Filter] ─── has_news = true?
       │
       ▼
[4a-4d. Caption Check v15] ─── Generate social captions
       │
       ▼
[5a-5d. Art Director] ─── Image prompt
       │
       ▼
[5.5a-5.5d. Gemini Image] ─── Generate image description
       │
       ▼
[6a-6d. Generate Image] ─── Create actual image
       │
       ▼
[7a-7d. Result] ─── Compile final output
       │
       ▼
[10a-10d. Send to Website] ─── POST to philata.com/api/results
```

---

## 3. Current Issues Identified

### Issue #1: Articles Too Short
**Problem:** Articles are significantly shorter than requested.

| Track | Requested | Actual (Avg) | Gap |
|-------|-----------|--------------|-----|
| Breaking | 800-1200 words | ~310 words | -62% |
| Regular | 1200-1800 words | ~987 words | -18% |
| Educational | 800-1200 words | ~750 words | -25% |
| Forms | 800-1200 words | ~900 words | -10% |

**Root Cause:**
- Breaking track builds article from JSON fragments instead of getting full article from Perplexity
- Other tracks: Perplexity sometimes returns shorter content despite prompt requirements

**Current Mitigation (Deployed):**
- Updated 1a. Fetch Breaking prompt to request full 800-1200 word article
- Added `full_article` field to JSON response format
- Parse Breaking (2a) now uses Perplexity's article if available

### Issue #2: Caption Sentences Cut Off
**Problem:** Bullet points in captions end mid-sentence.

**Example (Before Fix):**
```
• Proof of funds is essential for Canadian study permits and Express Entry, requiring
• This guide provides step-by-step preparation instructions, acceptable proofs, and
```

**Root Cause:**
- Old truncation logic cut at character limit regardless of sentence structure
- No validation that bullets end with proper punctuation

**Fix Deployed (Caption v15):**
- Only use complete sentences (25-100 chars)
- Skip any bullet over 100 chars entirely instead of cutting
- Ensure all bullets end with `.`, `!`, or `?`

### Issue #3: Spam Hashtags
**Problem:** 15+ hashtags including spam like #viral #trending #fyp

**Before:**
```
#CanadaImmigration #IRCC #ExpressEntry #CanadaPR #CanadaVisa #StudyInCanada
#WorkInCanada #MoveToCanada #ImmigrationNews #viral #trending #explorepage
#fyp #reels #viralreels #trendingnow #viral2025 #mustsee
```

**After (v15):**
```
#CanadaImmigration #IRCC #ExpressEntry #CanadaPR #CanadaVisa #ImmigrationNews
```

### Issue #4: Source Attribution
**Problem:** Educational/Forms articles showed "Philata Educational" as source.

**Fix Deployed:**
- Changed to `source: "canada.ca"` or `source: "IRCC"`
- Always use official government source URLs

---

## 4. Changes Made (Session Log)

### Change 1: Breaking Article Generation
**Files Modified:**
- `1a. Fetch Breaking` (prompt)
- `2a. Parse Breaking` (code)

**Before:**
- Prompt only requested research JSON
- Parse built article from fragments using `buildArticleFromResearch()`

**After:**
- Prompt requests BOTH research AND full_article from Perplexity
- Parse uses `research.full_article` if available
- Falls back to `buildArticleFromResearch()` only if needed
- Added `key_points` extraction for caption generation

### Change 2: Caption Check v15
**Files Modified:**
- `4a. Caption Check`
- `4b. Caption Check`
- `4c. Caption Check`
- `4d. Caption Check`

**Key Changes:**
```javascript
// v15 - Complete sentences only
// Only use bullets 25-100 chars
if (sentence.length >= 25 && sentence.length <= 100) {
  bullets.push(sentence);
}

// Clean hashtags - NO spam
const mainHashtags = '\n\n#CanadaImmigration #IRCC #ExpressEntry #CanadaPR #CanadaVisa #ImmigrationNews';

// Added tracking marker
caption_source: 'v15'
```

### Change 3: Result Nodes Image URL
**Files Modified:**
- `7a. Result` through `7d. Result`

**Fix:**
- Added `article_image_url: imgRes.image_url || null`
- Ensures generated image URL is included in API response

### Change 4: Source Attribution
**Files Modified:**
- `2c. Parse Educational`
- `2d. Parse Forms`

**Fix:**
- Changed `source` from "Philata Educational" to "canada.ca"
- Set `source_url` to official IRCC URLs

---

## 5. Caption System (v15)

### Caption Structure
```
[Emoji] [Title]

📖 Read more: [Article URL]

• [Bullet 1 - complete sentence]
• [Bullet 2 - complete sentence]
• [Bullet 3 - complete sentence]
• [Bullet 4 - complete sentence]
• [Bullet 5 - complete sentence]

💡 Save this post!
🔔 Follow @philata.ca for updates!

[Hashtags]
```

### Bullet Point Extraction Priority
1. **Key Facts** (CRS cutoff, ITAs, Draw number, Program, Deadline)
2. **key_points array** from Perplexity response
3. **Summary sentences** (if <4 bullets)

### Bullet Point Rules (v15)
- Minimum length: 25 characters
- Maximum length: 100 characters
- Must end with `.`, `!`, or `?`
- Skip date-only points like "31 December 2025"
- Skip duration-only points like "60 days"
- No cutting mid-sentence - skip entirely if too long

### Hashtag Sets (v15)
| Platform | Hashtags |
|----------|----------|
| Instagram/Facebook | #CanadaImmigration #IRCC #ExpressEntry #CanadaPR #CanadaVisa #ImmigrationNews |
| LinkedIn | #CanadaImmigration #IRCC #ExpressEntry #CanadaPR #Immigration |
| Twitter | #CanadaImmigration #IRCC #ExpressEntry #CanadaPR |

### Emoji Mapping
| Category | Emoji |
|----------|-------|
| Breaking | 🚨 |
| Educational | 💡 |
| Forms | 📝 |
| Express Entry | 🎯 |
| PNP | 🍁 |
| Study Permit | 📚 |
| Work Permit | 💼 |
| Policy | 📋 |
| Default | 🇨🇦 |

---

## 6. Article Generation Analysis

### Current Perplexity Prompts

#### Breaking (1a)
```
Model: sonar-pro
Temperature: 0.1
Max Tokens: 6000

Request: Search for breaking news from LAST 24 HOURS
- Research official sources (IRCC, canada.ca, PNP sites)
- Write 800-1200 word article with rich HTML
- Include stats-grid, tip-box, info-table elements
```

#### Regular (1b)
```
Model: sonar-pro
Temperature: 0.3
Max Tokens: 8000

Request: Search for ONE content from LAST 48 HOURS
- Find official government source
- Generate 1200-1800 word RICH HTML article
- Include stats-grid, info-table, tip-box, warning-box
```

#### Educational (1c)
```
Model: sonar-pro
Temperature: 0.5
Max Tokens: 6000

Request: Write educational article on immigration topic
- Research IRCC guidelines
- 800-1200 words
- Practical tips and actionable advice
```

#### Forms (1d)
```
Model: sonar-pro
Temperature: 0.5
Max Tokens: 6000

Request: Write guide about IRCC form/process
- Research official guidelines
- 800-1200 words with step-by-step instructions
- Common mistakes to avoid
```

### Why Articles Are Short

1. **Breaking Track Issue:**
   - Old prompt only requested JSON research data
   - `buildArticleFromResearch()` creates minimal article from fragments
   - New prompt requests full article but Perplexity may still return short content

2. **Token Limits:**
   - Perplexity may hit internal limits before reaching word count
   - Response includes JSON structure overhead

3. **Temperature Settings:**
   - Lower temperature (0.1 for Breaking) = more concise
   - Higher temperature (0.5) = more verbose but less focused

---

## 7. Recommendations for Improvement

### Priority 1: Article Length (Immediate)

**Option A: Increase Perplexity Token Limits**
```javascript
// Current
max_tokens: 6000

// Recommended
max_tokens: 8000-10000
```

**Option B: Add Minimum Word Count Validation**
```javascript
// In Parse nodes
const wordCount = article.full_article.replace(/<[^>]*>/g, '').split(/\s+/).length;
if (wordCount < 500) {
  return [{ json: { has_news: false, reason: 'article_too_short' } }];
}
```

**Option C: Two-Stage Generation**
1. First call: Get research/facts
2. Second call: "Expand this into 1200 words..." with facts as context

### Priority 2: Caption Quality (Immediate)

**Option A: Smarter Sentence Splitting**
```javascript
// Instead of skipping long sentences, split at clause boundaries
function smartSplit(text, maxLen) {
  if (text.length <= maxLen) return text;

  const breakPoints = ['; ', ', but ', ', and ', ': '];
  for (const bp of breakPoints) {
    const idx = text.indexOf(bp);
    if (idx > 30 && idx < maxLen) {
      return text.substring(0, idx) + '.';
    }
  }
  return null; // Skip if can't split cleanly
}
```

**Option B: Use AI for Caption Generation**
- Instead of extracting from article, have Perplexity generate captions directly
- Current prompt already requests this but we override with Caption Check
- Consider using Perplexity's captions for Instagram/Facebook

### Priority 3: Content Deduplication (Medium)

**Problem:** Same topics repeated daily (e.g., Start-Up Visa closure)

**Solution:**
1. Track recent article titles in database
2. Before accepting, check similarity to last 7 days
3. Reject if >80% similar title/topic

### Priority 4: Image Quality (Medium)

**Current:** Generic Gemini-generated images

**Improvement Options:**
1. Use news-specific imagery
2. Include key stats overlaid on image
3. Create branded templates with dynamic text

### Priority 5: Scheduling Optimization (Low)

**Current:** All 4 tracks run every 60 minutes

**Recommendation:**
- Breaking: Every 30 minutes (time-sensitive)
- Regular: Every 2 hours
- Educational: Every 4 hours
- Forms: Every 6 hours (evergreen content)

---

## 8. Configuration Reference

### API Endpoints

| Service | Endpoint | Purpose |
|---------|----------|---------|
| n8n API | `https://philata-n8n-production.up.railway.app/api/v1` | Workflow management |
| Website API | `https://www.philata.com/api/results` | Content storage |
| Image Server | `https://web-production-35219.up.railway.app` | Generated images |

### Environment Variables Needed
```
PERPLEXITY_API_KEY=pplx-xxx
GEMINI_API_KEY=xxx
N8N_API_KEY=eyJxxx
```

### n8n API Commands

**Get Workflow:**
```bash
curl -s "https://philata-n8n-production.up.railway.app/api/v1/workflows/JqWgdj9WKWNhPm9H" \
  -H "X-N8N-API-KEY: $API_KEY"
```

**Update Workflow:**
```bash
curl -s -X PUT "https://philata-n8n-production.up.railway.app/api/v1/workflows/JqWgdj9WKWNhPm9H" \
  -H "X-N8N-API-KEY: $API_KEY" \
  -H "Content-Type: application/json" \
  -d @workflow.json
```

**Deactivate/Activate:**
```bash
curl -s -X POST ".../workflows/{id}/deactivate" -H "X-N8N-API-KEY: $API_KEY"
curl -s -X POST ".../workflows/{id}/activate" -H "X-N8N-API-KEY: $API_KEY"
```

**Get Executions:**
```bash
curl -s ".../executions?limit=10&workflowId={id}" -H "X-N8N-API-KEY: $API_KEY"
```

---

## Appendix: Caption v15 Full Code

```javascript
// Caption v15 - FRESH BUILD - Complete sentences only
const article = $input.first().json;
if (!article.has_news && !article.title) return [];

function generateShortId(title) {
  if (!title) return 'news';
  let hash = 0;
  for (let i = 0; i < title.length; i++) {
    hash = ((hash << 5) - hash) + title.charCodeAt(i);
    hash = hash >>> 0;
  }
  const chars = '0123456789abcdefghijklmnopqrstuvwxyz';
  let result = '';
  let val = hash;
  while (val > 0) {
    result = chars[val % 36] + result;
    val = Math.floor(val / 36);
  }
  return result.substring(0, 6) || 'news';
}

function extractBullets(article) {
  const bullets = [];
  const kf = article.key_facts || article.raw_facts || {};

  // Key facts first
  if (kf.crs_cutoff && /^\d+$/.test(String(kf.crs_cutoff))) {
    bullets.push('CRS cutoff: ' + kf.crs_cutoff + ' points.');
  }
  if (kf.invitations_issued || kf.itas_issued) {
    bullets.push('ITAs issued: ' + (kf.invitations_issued || kf.itas_issued) + '.');
  }
  if (kf.draw_number) {
    bullets.push('Express Entry Draw #' + kf.draw_number + '.');
  }
  if (kf.program || kf.program_name) {
    const prog = String(kf.program || kf.program_name);
    bullets.push('Program: ' + (prog.length > 50 ? prog.substring(0, 50) : prog) + '.');
  }

  // Key points - ONLY complete sentences (25-100 chars)
  if (kf.key_points && Array.isArray(kf.key_points)) {
    kf.key_points.forEach(p => {
      let pt = String(p).trim();
      if (pt.length < 25) return;
      if (pt.length <= 100 && bullets.length < 6) {
        if (!pt.match(/[.!?]$/)) pt += '.';
        bullets.push(pt);
      }
    });
  }

  // Extract from summary - complete sentences only
  if (bullets.length < 4 && article.summary) {
    const sentences = article.summary.match(/[^.!?]+[.!?]+/g) || [];
    sentences.forEach(s => {
      const sentence = s.trim();
      if (sentence.length >= 25 && sentence.length <= 100 && bullets.length < 5) {
        bullets.push(sentence);
      }
    });
  }

  return bullets.slice(0, 5);
}

// v15 CLEAN hashtags - NO spam
const mainHashtags = '\n\n#CanadaImmigration #IRCC #ExpressEntry #CanadaPR #CanadaVisa #ImmigrationNews';

// ... rest of caption generation
```

---

## Document History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2025-12-31 | Initial documentation |
| v2 | 2025-12-31 | Added Caption v15, issue analysis, recommendations |

---

**Next Steps:**
1. Wait for 19:00 UTC execution to verify v15 captions
2. Consider implementing Priority 1 recommendations for article length
3. Review and approve before implementing further changes
