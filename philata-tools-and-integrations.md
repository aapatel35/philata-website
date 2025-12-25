# 🔧 PHILATA TECHNICAL ARCHITECTURE & TOOLS BREAKDOWN

---

## 📦 TOOLS YOU NEED TO BUILD/INTEGRATE

### **TIER 1: CRITICAL (Build Immediately)**

#### 1️⃣ **Web Application (Frontend + Backend)**
```
OPTION A: Start Simple (Recommended)
├─ Next.js 14 (full-stack framework)
├─ TypeScript (type safety)
├─ Tailwind CSS (styling)
├─ Shadcn UI (component library)
├─ PostgreSQL (database)
└─ Vercel (deployment)

OPTION B: Microservices (Only if scaling fast)
├─ React 19 (frontend)
├─ Node.js + Express (backend)
├─ PostgreSQL (database)
├─ Docker (containerization)
└─ Railway/Render (deployment)

RECOMMENDATION: Use Option A for MVP (faster, fewer moving parts)
```

**Estimated Build Time:** 16 weeks (as per roadmap)
**Cost to Build:** $15-25k (contractors)
**Monthly Hosting:** $100-500 (scales with users)

---

#### 2️⃣ **Browser Extension (Auto-Fill IRCC Forms)**
```
Technology: Manifest V3 (Chrome Extension)
├─ Frontend: HTML + JavaScript
├─ Communication: Message passing to Philata website
├─ Storage: Chrome Storage API (encrypted)
└─ Target: IRCC portal forms (IMM5709, IMM5710, etc.)

What It Does:
• User logs into IRCC.gc.ca
• Extension detects form fields
• Shows "Auto-fill with Philata?" popup
• Fills fields from user's data
• User reviews + submits (they control final submission)

Estimated Build Time:** 2-3 weeks
Cost: Free (you build it)

Code Structure:
├─ manifest.json (permissions, config)
├─ popup.html (UI when user clicks extension icon)
├─ popup.js (logic for popup)
├─ content-script.js (injects into IRCC website)
└─ background.js (handles communication with website)
```

---

#### 3️⃣ **AI Chatbot (RAG-Powered)**
```
Technology: OpenAI GPT-4 + LangChain + Vector Database

Architecture:
Step 1: User Reads Article on Philata
Step 2: User Asks Question (e.g., "Do I qualify?")
Step 3: System Retrieves Article Context
Step 4: GPT-4 Generates Answer Using Context
Step 5: Answer Appears in Chat Bubble

Setup:
1. Use OpenAI API (gpt-4-turbo or gpt-4)
2. Embed article text with OpenAI Embeddings
3. Store embeddings in Supabase Vector Database
4. On user question, find similar articles (semantic search)
5. Feed article + question to GPT-4
6. Return answer

Cost:
• GPT-4 API: ~$0.01-0.05 per question
• Vector storage (Supabase): Free tier includes 1M vectors
• For 10k questions/day: ~$50-200/month

Code Example:
const response = await openai.createChatCompletion({
  model: "gpt-4-turbo",
  messages: [
    {
      role: "system",
      content: `You are a Canadian immigration expert. Answer based on this article: ${articleContext}`
    },
    { role: "user", content: userQuestion }
  ],
  temperature: 0.7,
  max_tokens: 150
});
```

**Estimated Build Time:** 1-2 weeks
**Cost:** $100-300/month at scale

---

#### 4️⃣ **OCR (Document Data Extraction)**
```
Technology: Tesseract.js + Paddle OCR

Use Cases:
• Extract data from passport images
• Extract data from offer letters
• Extract data from degree certificates
• Extract data from language test results

Setup:
1. User uploads image/PDF
2. Tesseract.js processes image (client-side)
3. Extracts text
4. Regular expressions parse text for key fields
5. User verifies extracted data
6. Data saved to database

Code Example:
import Tesseract from 'tesseract.js';

async function extractPassportData(imageFile) {
  const { data: { text } } = await Tesseract.recognize(
    imageFile,
    'eng',
    { logger: m => console.log(m) }
  );
  
  // Parse OCR output
  const passportNumber = text.match(/[A-Z]{2}\d{7}/)?.[0];
  const expiryDate = text.match(/(\d{2}\/\d{2}\/\d{4})/)?.[0];
  
  return { passportNumber, expiryDate };
}

Accuracy: ~92-97% (varies by image quality)
Cost: Free (Tesseract is open-source)
```

**Estimated Build Time:** 1-2 weeks
**Cost:** Free (open-source)

---

#### 5️⃣ **Document Storage & Encryption (AWS S3)**
```
What You Need:
• S3 bucket for file storage (encrypted)
• CloudFront CDN for fast retrieval
• AWS KMS for encryption keys
• Virus scanning (ClamAV)

Setup:
1. Create S3 bucket (private, not public)
2. Enable encryption with AWS KMS
3. Enable versioning (track document updates)
4. Set lifecycle policies (delete after 7 years)
5. Enable logging (audit trail)

Cost:
• S3 storage: $0.023 per GB/month
• At 10k users × 5 documents × 2MB = 100GB = $2.30/month
• Data transfer: $0.12 per GB out

Code Example:
const s3 = new AWS.S3();

await s3.upload({
  Bucket: 'philata-documents',
  Key: `users/${userId}/passport_${Date.now()}.pdf`,
  Body: encryptedFileBuffer,
  ServerSideEncryption: 'aws:kms',
  SSEKMSKeyId: process.env.AWS_KMS_KEY_ID,
  Metadata: {
    'user-id': userId,
    'document-type': 'passport'
  }
}).promise();
```

**Estimated Build Time:** 2-3 days
**Cost:** <$10/month for MVP scale

---

### **TIER 2: IMPORTANT (Add in Weeks 3-4)**

#### 6️⃣ **Authentication & Authorization (NextAuth.js)**
```
What It Does:
• Google OAuth sign-in
• Email/password authentication
• Session management (JWT)
• Multi-user access control

Setup:
1. Install NextAuth.js
2. Configure Google OAuth (get Client ID from Google Cloud Console)
3. Set up JWT secret
4. Create user session database table

Code Example:
import NextAuth from 'next-auth';
import GoogleProvider from 'next-auth/providers/google';

export const authOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) token.id = user.id;
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.id;
      return session;
    }
  }
};

Cost: Free (NextAuth.js is open-source)
```

**Estimated Build Time:** 3-5 days
**Cost:** Free

---

#### 7️⃣ **Payment Processing (Stripe)**
```
What You Need:
• Stripe account
• Payment integration in checkout
• Invoice generation
• Webhook handling (payment confirmation)

Setup:
1. Create Stripe account
2. Get API keys
3. Create Stripe products (Work Permit form $99, PR form $199, etc.)
4. Implement checkout button
5. Handle payment webhooks

Code Example:
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY);

// Create checkout session
const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: [
    {
      price: 'price_work_permit', // Replace with actual price ID
      quantity: 1
    }
  ],
  mode: 'payment',
  success_url: 'https://philata.com/success',
  cancel_url: 'https://philata.com/cancel'
});

Webhook Handling:
app.post('/api/webhooks/stripe', (req, res) => {
  const event = stripe.webhooks.constructEvent(
    req.body,
    req.headers['stripe-signature'],
    process.env.STRIPE_WEBHOOK_SECRET
  );
  
  if (event.type === 'payment_intent.succeeded') {
    // Mark application as paid
    // Send confirmation email
  }
});

Cost: 2.9% + $0.30 per transaction
```

**Estimated Build Time:** 3-5 days
**Cost:** Pay-per-transaction (2.9%)

---

#### 8️⃣ **Email Delivery (SendGrid)**
```
What You Need:
• SendGrid account
• Email templates
• Webhook handling
• Unsubscribe list management

Use Cases:
• Welcome email on signup
• Form saved reminder
• Application submitted confirmation
• Status update notifications
• Bill receipts

Code Example:
const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

await sgMail.send({
  to: 'user@example.com',
  from: 'hello@philata.com',
  subject: 'Your PGWP Application is Ready!',
  html: '<h1>Your PGWP form is complete. Ready to submit?</h1>...'
});

Cost: $9.95/month for 15k emails (or $0.0001 per email for pay-as-you-go)
```

**Estimated Build Time:** 2-3 days
**Cost:** $10-50/month

---

#### 9️⃣ **Analytics & Monitoring (PostHog)**
```
What You Track:
• User signup flow completion
• Form abandonment (which screen?)
• Document upload success rate
• Payment success/failure
• Chatbot usage stats
• Page performance metrics

Code Example:
import { PostHog } from 'posthog-js';

const posthog = new PostHog(process.env.POSTHOG_API_KEY);

// Track user sign up
posthog.capture('user_signed_up', {
  source: 'google_oauth'
});

// Track form screen viewed
posthog.capture('form_screen_viewed', {
  screenNumber: 3,
  formType: 'pgwp'
});

// Track payment
posthog.capture('payment_completed', {
  amount: 99,
  currency: 'CAD',
  productType: 'work_permit'
});

Cost: Free for up to 1M events/month
```

**Estimated Build Time:** 1 day
**Cost:** Free tier sufficient for MVP

---

### **TIER 3: NICE TO HAVE (Add in Weeks 11-16)**

#### 🔟 **IRCC GCKey OAuth Integration**
```
What It Does:
• User logs in with their IRCC GCKey
• You get read-only access to their application status
• Show real-time updates in Philata dashboard

Process:
1. Contact IRCC (email: innovation@ircc.gc.ca)
2. Request OAuth sandbox access
3. They'll give you Client ID + Client Secret
4. Implement OAuth flow in your app

Code Example:
const irccConfig = {
  client_id: process.env.IRCC_CLIENT_ID,
  client_secret: process.env.IRCC_CLIENT_SECRET,
  redirect_uri: 'https://philata.com/auth/ircc/callback',
  authorization_endpoint: 'https://ircc-sandbox.canada.ca/oauth/authorize',
  token_endpoint: 'https://ircc-sandbox.canada.ca/oauth/token'
};

// 1. Redirect user to IRCC login
app.get('/auth/ircc', (req, res) => {
  const authUrl = new URL(irccConfig.authorization_endpoint);
  authUrl.searchParams.append('client_id', irccConfig.client_id);
  authUrl.searchParams.append('response_type', 'code');
  authUrl.searchParams.append('redirect_uri', irccConfig.redirect_uri);
  authUrl.searchParams.append('scope', 'applications:read');
  res.redirect(authUrl.toString());
});

// 2. Handle callback
app.get('/auth/ircc/callback', async (req, res) => {
  const { code } = req.query;
  
  // Exchange code for token
  const tokenResponse = await fetch(irccConfig.token_endpoint, {
    method: 'POST',
    body: JSON.stringify({
      grant_type: 'authorization_code',
      code,
      client_id: irccConfig.client_id,
      client_secret: irccConfig.client_secret
    })
  });
  
  const { access_token } = await tokenResponse.json();
  
  // Store token (encrypted)
  // Use token to fetch application status
  const applicationsResponse = await fetch('https://ircc-sandbox.canada.ca/api/applications', {
    headers: { Authorization: `Bearer ${access_token}` }
  });
  
  const applications = await applicationsResponse.json();
  // Save to user's Philata dashboard
});

IMPORTANT: IRCC often rejects these requests. Have a lawyer/consultant help.
Cost: Free (if approved)
Difficulty: HIGH (requires regulatory approval)
```

**Estimated Build Time:** 2-4 weeks (IF approved by IRCC)
**Cost:** Free
**Risk:** IRCC may reject (have backup plan)

---

#### 1️⃣1️⃣ **Community Timeline Data (Crowdsourcing)**
```
What It Does:
• Users anonymously share: "I applied Dec 1, got decision Jan 15"
• You aggregate & analyze: "Average PGWP processing is 45 days"
• Display on dashboard to keep users engaged

Database Table:
CREATE TABLE timeline_submissions (
  id SERIAL PRIMARY KEY,
  user_id INT,
  program_type VARCHAR (e.g., 'pgwp'),
  submitted_date DATE,
  decision_date DATE,
  decision_result VARCHAR (e.g., 'approved'),
  processing_days INT,
  province VARCHAR,
  created_at TIMESTAMP
);

Query:
SELECT 
  AVG(processing_days) as avg_processing,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY processing_days) as median,
  COUNT(*) as sample_size
FROM timeline_submissions
WHERE program_type = 'pgwp'
AND submitted_date > NOW() - INTERVAL '6 months';

Cost: Free (uses existing database)
```

**Estimated Build Time:** 1-2 weeks
**Cost:** Free

---

#### 1️⃣2️⃣ **RCIC Marketplace**
```
What You Need:
• Database of licensed RCICs
• Booking system
• Payment split (30% Philata, 70% RCIC)
• Review system (star ratings)

Workflow:
1. User completes application in Philata
2. Sees button: "Have an RCIC review your file? $50"
3. Clicks button → Browse RCICs
4. Selects RCIC → Booking calendar
5. Schedules call/review
6. Sends application data to RCIC securely
7. RCIC reviews, sends feedback
8. Philata takes 30%, RCIC gets 70%

Code Example:
CREATE TABLE rcic_partners (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  email VARCHAR,
  license_number VARCHAR (unique, verified),
  specialties JSONB (e.g., ['PR', 'Work Permits']),
  hourly_rate INT,
  review_rating FLOAT,
  review_count INT,
  stripe_account_id VARCHAR,
  created_at TIMESTAMP
);

Cost: Free (you'll split Stripe fees)
```

**Estimated Build Time:** 2-3 weeks
**Cost:** Free (commission-based)

---

## 📋 COMPLETE TOOLS LIST & COSTS

| Tool | Purpose | Cost | Time to Setup |
|------|---------|------|----------------|
| **Next.js** | Web framework | Free | 1 day |
| **Supabase** | Database + Auth | $25/month | 1 day |
| **Vercel** | Deployment | Free | 1 hour |
| **OpenAI API** | Chatbot | $100-300/month | 1 day |
| **Tesseract.js** | OCR | Free | 2-3 days |
| **AWS S3** | Document storage | $5-20/month | 1 day |
| **Stripe** | Payments | 2.9% + $0.30 | 2 days |
| **SendGrid** | Email | $10-50/month | 1 day |
| **PostHog** | Analytics | Free | 1 day |
| **Chrome Extension** | Auto-fill | Free (you build) | 2-3 weeks |
| **IRCC OAuth** | Case tracking | Free (if approved) | 2-4 weeks |
| **Figma** | Design | $12/month | Ongoing |
| **GitHub** | Version control | Free | 1 hour |
| **Sentry** | Error tracking | Free | 1 hour |

**TOTAL MONTHLY COSTS (MVP):** ~$150-500/month (scales with usage)

---

## 🔐 SECURITY CHECKLIST

- [ ] All user data encrypted at rest (AES-256)
- [ ] HTTPS everywhere (Vercel provides free SSL)
- [ ] Passwords hashed with bcrypt
- [ ] No passwords stored in database (use NextAuth)
- [ ] API keys in environment variables (never in code)
- [ ] Document URLs signed (expire after 24 hours)
- [ ] Rate limiting on login (prevent brute force)
- [ ] CSRF protection (NextAuth includes)
- [ ] SQL injection prevention (use Prisma ORM)
- [ ] XSS protection (React escapes by default)
- [ ] Regular security audits (use OWASP checklist)

---

## 🚀 DEPLOYMENT CHECKLIST

**Week 15:**
- [ ] Test all features on Vercel staging
- [ ] Security audit with OWASP checklist
- [ ] Load test (can handle 1,000 concurrent users?)
- [ ] Email all beta users (beta.philata.com)
- [ ] Set up monitoring alerts (Sentry)

**Week 16:**
- [ ] Soft launch to 100 beta users
- [ ] Collect feedback for 2-3 days
- [ ] Fix critical bugs
- [ ] Public launch (philata.com)
- [ ] Press release + social announcement

---

## 💾 DATABASE SCHEMA (Start Here)

```sql
-- Users Table
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  phone VARCHAR(20),
  country VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Applications Table
CREATE TABLE applications (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  program_type VARCHAR(50), -- 'pgwp', 'pr', 'study_permit'
  status VARCHAR(50), -- 'in_progress', 'submitted', 'approved', 'rejected'
  form_data JSONB, -- Stores all form fields
  documents JSONB, -- Array of document URLs
  submitted_at TIMESTAMP,
  paid_at TIMESTAMP,
  payment_amount DECIMAL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Documents Table
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  application_id INT REFERENCES applications(id),
  document_type VARCHAR(50), -- 'passport', 'offer_letter', 'degree'
  s3_url TEXT,
  extracted_data JSONB, -- OCR extracted data
  verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Timeline Data (for community insights)
CREATE TABLE timeline_submissions (
  id SERIAL PRIMARY KEY,
  application_id INT REFERENCES applications(id),
  submitted_date DATE,
  decision_date DATE,
  processing_days INT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

**You're ready to build. Start with Week 1-2 foundation. The entire system is achievable in 16 weeks by 1 developer + 2 part-time contractors.**

**Questions? Let me build the code repository template next.**
