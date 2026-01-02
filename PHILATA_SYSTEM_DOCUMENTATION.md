# Philata System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Website Pages](#website-pages)
3. [Backend Components](#backend-components)
4. [API Endpoints](#api-endpoints)
5. [Automation Workflow](#automation-workflow)
6. [Database & Storage](#database--storage)
7. [Deployment](#deployment)
8. [Checklist](#checklist)

---

## System Overview

Philata is a Canadian immigration news and content platform that:
- Monitors IRCC and official sources for immigration updates
- Generates articles and social media content using AI
- Provides educational guides and resources
- Offers tools like CRS Calculator

---

## Website Pages

### Public Pages

| # | Page | Template File | Route | Template Exists | Route Implemented | Description |
|---|------|---------------|-------|-----------------|-------------------|-------------|
| 1 | Homepage | `index.html` | `/` | ✅ | ✅ | Hero section, stats, quick links |
| 2 | News Feed | `dashboard.html` | `/dashboard` | ✅ | ✅ | All generated content with filters |
| 3 | Articles List | `articles.html` | `/articles` | ✅ | ✅ | Published articles with category filters |
| 4 | Article Detail | `article_detail.html` | `/articles/<slug>` | ✅ | ✅ | Full article view with sidebar |
| 5 | Short URL | N/A | `/a/<short_id>` | N/A | ✅ | Redirects to full article URL |
| 6 | Browse Categories | `browse.html` | `/browse` | ✅ | ✅ | Category navigation |
| 7 | Category Detail | `browse_category.html` | `/browse/<category>` | ✅ | ✅ | Articles in category |
| 8 | Learning Hub | `learning_hub.html` | `/learn` | ✅ | ✅ | Educational resources |
| 9 | Guides List | `guides.html` | `/guides` | ✅ | ✅ | All guide categories |
| 10 | Guide Category | `guides.html` | `/guides/<category_id>` | ✅ | ✅ | Guides in category |
| 11 | Guide Detail | `guide_detail.html` | `/guides/<cat>/<guide>` | ✅ | ✅ | Individual guide content |
| 12 | Province Detail | `province_detail.html` | `/guides/pnp/<province>` | ✅ | ✅ | Province PNP details |
| 13 | CRS Calculator | `crs_calculator.html` | `/tools/crs-calculator` | ✅ | ✅ | Express Entry points calculator |
| 14 | Practice Tests | `practice_tests.html` | `/practice-tests` | ✅ | ✅ | Language exam practice |
| 15 | About | `about.html` | `/about` | ✅ | ✅ | Mission, vision, values |
| 16 | Features | `features.html` | `/features` | ✅ | ✅ | Platform features |
| 17 | Contact | `contact.html` | `/contact` | ✅ | ✅ | Contact form and info |
| 18 | Content Detail | `content_detail.html` | `/content/<id>` | ✅ | ✅ | Single content item view |

### Legal Pages

| # | Page | Template File | Route | Template Exists | Route Implemented |
|---|------|---------------|-------|-----------------|-------------------|
| 1 | Terms | `terms.html` | `/terms` | ✅ | ✅ |
| 2 | Privacy Policy | `privacy.html` | `/privacy-policy` | ✅ | ✅ |
| 3 | Cookie Policy | `cookies.html` | `/cookie-policy` | ✅ | ✅ |
| 4 | Refund Policy | `refund.html` | `/refund-policy` | ✅ | ✅ |
| 5 | Disclaimer | `disclaimer.html` | `/disclaimer` | ✅ | ✅ |

### Base Template

| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | `base.html` | Main layout with sidebar, CSS variables, fonts | ✅ |

---

## Backend Components

### Flask Application (`app.py`)

| # | Route | Method | Handler Function | Status | Description |
|---|-------|--------|------------------|--------|-------------|
| 1 | `/` | GET | `home()` | ✅ | Homepage |
| 2 | `/about` | GET | `about()` | ✅ | About page |
| 3 | `/features` | GET | `features()` | ✅ | Features page |
| 4 | `/contact` | GET | `contact()` | ✅ | Contact page |
| 5 | `/terms` | GET | `terms()` | ✅ | Terms page |
| 6 | `/privacy-policy` | GET | `privacy_policy()` | ✅ | Privacy page |
| 7 | `/cookie-policy` | GET | `cookie_policy()` | ✅ | Cookies page |
| 8 | `/refund-policy` | GET | `refund_policy()` | ✅ | Refund page |
| 9 | `/disclaimer` | GET | `disclaimer()` | ✅ | Disclaimer page |
| 10 | `/tools/crs-calculator` | GET | `crs_calculator()` | ✅ | CRS Calculator |
| 11 | `/learn` | GET | `learning_hub()` | ✅ | Learning Hub |
| 12 | `/practice-tests` | GET | `practice_tests()` | ✅ | Practice Tests |
| 13 | `/dashboard` | GET | `dashboard()` | ✅ | Content dashboard |
| 14 | `/browse` | GET | `browse_categories()` | ✅ | Category browser |
| 15 | `/browse/<category>` | GET | `browse_category()` | ✅ | Category articles |
| 16 | `/articles` | GET | `articles()` | ✅ | Article listing |
| 17 | `/a/<short_id>` | GET | `short_url_redirect()` | ✅ | Short URL redirect |
| 18 | `/articles/<slug>` | GET | `article_detail()` | ✅ | Article detail |
| 19 | `/guides` | GET | `guides()` | ✅ | Guides main page |
| 20 | `/guides/<category_id>` | GET | `guides_category()` | ✅ | Guide category |
| 21 | `/guides/<cat>/<guide>` | GET | `guide_detail()` | ✅ | Guide detail |
| 22 | `/guides/pnp/<province>` | GET | `province_detail()` | ✅ | Province detail |
| 23 | `/content/<content_id>` | GET | `view_content()` | ✅ | Content item |

---

## API Endpoints

| # | Endpoint | Method | Description | Status |
|---|----------|--------|-------------|--------|
| 1 | `/api/health` | GET | Health check | ✅ |
| 2 | `/api/stats` | GET | Content statistics | ✅ |
| 3 | `/api/results` | GET | All content results | ✅ |
| 4 | `/api/results` | POST | Add new result (legacy) | ✅ |
| 5 | `/api/articles` | POST | Add new article (enhanced) | ✅ |
| 6 | `/api/results/<id>/approve` | POST | Approve content | ✅ |
| 7 | `/api/results/<id>/reject` | POST | Reject content | ✅ |
| 8 | `/api/results/<id>/posted` | POST | Mark as posted | ✅ |
| 9 | `/api/results/clear` | POST | Clear all results | ✅ |
| 10 | `/api/approved` | GET | Get approved content | ✅ |
| 11 | `/api/upload-image` | POST | Upload image | ✅ |
| 12 | `/images/<filename>` | GET | Serve images | ✅ |

### External API (Post API)

| # | Endpoint | Description | Status |
|---|----------|-------------|--------|
| 1 | `/results/list` | GET all results from Post API | ✅ |
| 2 | `/results/log` | POST new content to Post API | ✅ |

---

## Automation Workflow (n8n)

### Content Tracks

| Track | Trigger Interval | Source | Description |
|-------|------------------|--------|-------------|
| Breaking | Every 20 min | Perplexity AI (IRCC search) | Express Entry draws, urgent news |
| Regular | Every 2 hours | Perplexity AI (news search) | General immigration news |
| Educational | Every 30 min | Post API `/educational/daily` | 365-day calendar topics |
| Forms | Every 30 min | Post API `/forms/daily` | IRCC forms guides |

### Workflow Steps (Per Track)

| # | Step | Node Type | Description | Status |
|---|------|-----------|-------------|--------|
| 1 | Fetch Content | HTTP Request | Query Perplexity AI or Post API | ✅ |
| 2 | Parse Response | Code | Extract JSON, validate content | ✅ |
| 3 | Filter | Filter | Check if has valid news/topic | ✅ |
| 4 | Caption Check | Code | Prepare captions for platforms | ✅ |
| 4.5 | Verify Content | Code | (Edu/Forms) Verify accuracy | ✅ |
| 5 | Art Director | Code | Generate image prompt | ✅ |
| 5.5 | Gemini Image | Code | Generate image with Gemini Imagen | ✅ |
| 6 | Generate Image | HTTP Request | Create social media graphic | ✅ |
| 7 | Result | Code | Prepare final payload | ✅ |
| 8 | Discord | Code | Send notification to Discord | ✅ |
| 9 | Log Results | HTTP Request | POST to `/results/log` | ✅ |
| 10 | Send to Website | Code | POST to `philata.com/api/results` | ✅ |

### API Integrations

| Service | Purpose | Endpoint |
|---------|---------|----------|
| Perplexity AI | News search/research | `api.perplexity.ai/chat/completions` |
| Claude (Anthropic) | Article writing (Breaking) | `api.anthropic.com/v1/messages` |
| Gemini Imagen | AI image generation | `generativelanguage.googleapis.com` |
| Unsplash | Stock photos | `api.unsplash.com/search/photos` |
| Discord Webhook | Notifications | `discord.com/api/webhooks/...` |
| Post API | Image generation, logging | `web-production-35219.up.railway.app` |
| Philata Website | Article storage | `philata.com/api/results` |

### n8n Workflow Files

| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | `philata_v2.5_export.json` | Main workflow (original) | ✅ Verified |
| 2 | `philata_v2.6_gemini.json` | Gemini-based workflow (current) | ✅ Verified |
| 3 | `philata_import.json` | Import workflow | ⬜ Review |

---

## Database & Storage

### Data Storage

| # | Component | Location | Description | Status |
|---|-----------|----------|-------------|--------|
| 1 | Content Results | `data/results.json` | Generated articles and captions | ✅ |
| 2 | Approved Content | `data/approved.json` | Approved for posting | ✅ |
| 3 | Guides Data | `data/guides.json` | Educational guide content | ✅ |
| 4 | Articles Data | `data/articles.json` | Published articles | ✅ |
| 5 | Images | `static/images/` | Generated social media images | ✅ |

---

## Deployment

### Hosting

| # | Service | Purpose | URL | Status |
|---|---------|---------|-----|--------|
| 1 | Railway | Flask App | `web-production-35219.up.railway.app` | ✅ Active |
| 2 | Railway | n8n Automation | `philata-n8n-production.up.railway.app` | ✅ Active |
| 3 | GitHub | Source Code | `github.com/aapatel35/philata-website` | ✅ Active |

### Environment Variables

| # | Variable | Description | Required |
|---|----------|-------------|----------|
| 1 | `PORT` | Flask port (default: 5000) | ✅ |
| 2 | `POST_API_URL` | Post API base URL | ✅ |
| 3 | `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | Optional |
| 4 | `FLASK_DEBUG` | Enable debug mode | Optional |

---

## Checklist

### Phase 1: Website Templates ✅ COMPLETE
- [x] base.html - Core design system with sidebar
- [x] index.html - Homepage with hero, stats, quick links
- [x] dashboard.html - News feed with filters
- [x] articles.html - Article listing with categories
- [x] article_detail.html - Article view with sidebar
- [x] browse.html - Category browser
- [x] browse_category.html - Category articles
- [x] crs_calculator.html - CRS tool
- [x] about.html - About page
- [x] contact.html - Contact page
- [x] guide_detail.html - Guide pages
- [x] guides.html - Guides listing
- [x] learning_hub.html - Learning center
- [x] practice_tests.html - Practice tests
- [x] province_detail.html - Province PNP info
- [x] features.html - Features page
- [x] Legal pages (terms, privacy, cookies, refund, disclaimer)

### Phase 2: Backend Routes ✅ COMPLETE
- [x] All 23 page routes implemented
- [x] All 12 API endpoints implemented
- [x] Image serving configured
- [x] CORS enabled

### Phase 3: Automation (n8n) ✅ VERIFIED
- [x] Review n8n workflow structure (4 tracks: Breaking, Regular, Educational, Forms)
- [x] Verify source monitoring (Perplexity AI + Post API endpoints)
- [x] Verify content generation (Claude + Gemini Imagen)
- [x] Verify API integration (Discord, Post API, Philata Website)
- [ ] Test live execution (pending)

### Phase 4: Content
- [ ] Review existing articles
- [ ] Populate guides.json with content
- [ ] Verify category structure
- [ ] Test search functionality

### Phase 5: Deployment
- [ ] Verify Railway Flask deployment
- [ ] Verify Railway n8n deployment
- [ ] Check environment variables
- [ ] Test production URLs
- [ ] Monitor for errors

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         n8n WORKFLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │ Monitor │ -> │ Detect  │ -> │ Scrape  │ -> │   AI    │     │
│  │ Sources │    │ Changes │    │ Content │    │ Process │     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│                                                    │            │
│                                                    v            │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │ Social  │ <- │ Generate│ <- │ Caption │ <- │ Article │     │
│  │ Post    │    │ Image   │    │ Create  │    │ Write   │     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│       │                                            │            │
└───────│────────────────────────────────────────────│────────────┘
        │                                            │
        │                                            v
        │                                    ┌─────────────┐
        │                                    │  POST API   │
        │                                    │ /results/log│
        │                                    └─────────────┘
        │                                            │
        │                                            v
        │                                    ┌─────────────┐
        │                                    │   FLASK     │
        │                                    │   Website   │
        │                                    └─────────────┘
        │                                            │
        v                                            v
┌─────────────┐                              ┌─────────────┐
│  Instagram  │                              │   Browser   │
│  Facebook   │                              │   Users     │
│  LinkedIn   │                              │             │
│  Twitter/X  │                              │             │
└─────────────┘                              └─────────────┘
```

---

## Notes

_Add any notes or issues discovered during review:_

1. All templates exist and are styled with new gradient design system
2. All Flask routes are implemented and functional
3. n8n workflow needs verification

---

**Last Updated:** 2026-01-01
**Version:** 2.0
