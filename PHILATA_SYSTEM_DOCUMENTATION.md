# Philata System Documentation

## Table of Contents
1. [System Overview](#system-overview)
2. [Website Pages](#website-pages)
3. [Backend Components](#backend-components)
4. [Automation Workflow](#automation-workflow)
5. [Database & Storage](#database--storage)
6. [Deployment](#deployment)
7. [Checklist](#checklist)

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

| # | Page | Template File | URL | Status | Description |
|---|------|---------------|-----|--------|-------------|
| 1 | Homepage | `index.html` | `/` | ✅ | Hero section, stats, quick links, latest articles |
| 2 | News Feed | `dashboard.html` | `/dashboard` | ✅ | All generated content with filters |
| 3 | Articles List | `articles.html` | `/articles` | ✅ | Published articles with category filters |
| 4 | Article Detail | `article_detail.html` | `/articles/<slug>` | ✅ | Full article view with sidebar |
| 5 | Browse Categories | `browse.html` | `/browse` | ✅ | Category navigation |
| 6 | Category Detail | `browse_category.html` | `/browse/<category>` | ⬜ | Articles in category |
| 7 | Learning Hub | `learning_hub.html` | `/learn` | ⬜ | Educational resources |
| 8 | Guides List | `guides.html` | `/guides` | ⬜ | All guide categories |
| 9 | Guide Detail | `guide_detail.html` | `/guides/<path>` | ✅ | Individual guide content |
| 10 | CRS Calculator | `crs_calculator.html` | `/tools/crs-calculator` | ✅ | Express Entry points calculator |
| 11 | About | `about.html` | `/about` | ✅ | Mission, vision, values |
| 12 | Contact | `contact.html` | `/contact` | ✅ | Contact form and info |

### Base Template

| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | `base.html` | Main layout with sidebar, CSS variables, fonts | ✅ |

---

## Backend Components

### Flask Application (`app.py`)

| # | Component | Description | Status |
|---|-----------|-------------|--------|
| 1 | Route: `/` | Homepage - loads stats and articles | ⬜ |
| 2 | Route: `/dashboard` | News feed - loads all content | ⬜ |
| 3 | Route: `/articles` | Article listing with filters | ⬜ |
| 4 | Route: `/articles/<slug>` | Single article view | ⬜ |
| 5 | Route: `/browse` | Category browser | ⬜ |
| 6 | Route: `/guides/<path>` | Guide pages | ⬜ |
| 7 | Route: `/tools/crs-calculator` | CRS Calculator page | ⬜ |
| 8 | Route: `/about` | About page | ⬜ |
| 9 | Route: `/contact` | Contact page | ⬜ |

### API Endpoints

| # | Endpoint | Method | Description | Status |
|---|----------|--------|-------------|--------|
| 1 | `/api/stats` | GET | Content statistics | ⬜ |
| 2 | `/api/results` | GET | All content results | ⬜ |
| 3 | `/results/log` | POST | Log new content from n8n | ⬜ |
| 4 | `/api/articles` | GET | Published articles | ⬜ |

---

## Automation Workflow (n8n)

### Workflow Steps

| # | Step | Description | Status |
|---|------|-------------|--------|
| 1 | Source Monitoring | Check IRCC/Canada.ca for updates | ⬜ |
| 2 | Content Detection | Identify new/changed content | ⬜ |
| 3 | AI Processing | Generate article with Gemini/GPT | ⬜ |
| 4 | Caption Generation | Create platform-specific captions | ⬜ |
| 5 | Image Generation | Create social media graphics | ⬜ |
| 6 | Post to Website | Send to Flask API | ⬜ |
| 7 | Social Media Posting | Post to Instagram/Facebook/etc | ⬜ |

### n8n Workflow Files

| # | File | Description | Status |
|---|------|-------------|--------|
| 1 | `philata_v2.5_export.json` | Main workflow export | ⬜ |
| 2 | `philata_v2.6_gemini.json` | Gemini-based workflow | ⬜ |

---

## Database & Storage

### Data Storage

| # | Component | Location | Description | Status |
|---|-----------|----------|-------------|--------|
| 1 | Content Results | SQLite/JSON | Generated articles and captions | ⬜ |
| 2 | Images | Railway/Local | Generated social media images | ⬜ |
| 3 | Guides | Static JSON/MD | Educational guide content | ⬜ |

---

## Deployment

### Hosting

| # | Service | Purpose | URL | Status |
|---|---------|---------|-----|--------|
| 1 | Railway | Flask App | `web-production-35219.up.railway.app` | ⬜ |
| 2 | Railway | n8n Automation | `philata-n8n-production.up.railway.app` | ⬜ |
| 3 | GitHub | Source Code | `github.com/aapatel35/philata-website` | ✅ |

### Environment Variables

| # | Variable | Description | Status |
|---|----------|-------------|--------|
| 1 | `PORT` | Flask port | ⬜ |
| 2 | `DATABASE_URL` | Database connection | ⬜ |
| 3 | `N8N_API_KEY` | n8n API authentication | ⬜ |

---

## Checklist

### Phase 1: Website Templates (COMPLETED)
- [x] base.html - Core design system
- [x] index.html - Homepage redesign
- [x] dashboard.html - News feed
- [x] articles.html - Article listing
- [x] article_detail.html - Article view
- [x] browse.html - Category browser
- [x] crs_calculator.html - CRS tool
- [x] about.html - About page
- [x] contact.html - Contact page
- [x] guide_detail.html - Guide pages

### Phase 2: Backend Verification
- [ ] Verify all Flask routes work
- [ ] Test API endpoints
- [ ] Check database connections
- [ ] Verify image serving

### Phase 3: Automation
- [ ] Review n8n workflow
- [ ] Test content generation
- [ ] Verify API integration
- [ ] Test social media posting

### Phase 4: Content
- [ ] Review existing articles
- [ ] Check guide content
- [ ] Verify category structure
- [ ] Test search functionality

### Phase 5: Deployment
- [ ] Verify Railway deployment
- [ ] Check environment variables
- [ ] Test production URLs
- [ ] Monitor for errors

---

## Notes

_Add any notes or issues discovered during review:_

1.
2.
3.

---

**Last Updated:** 2026-01-01
**Version:** 1.0
