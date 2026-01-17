# Next.js Explained - For Beginners

## What is Next.js?

Imagine you're building a house (a website). You could:
- **Buy raw materials** (plain HTML/CSS/JavaScript) and build everything from scratch
- **Use a toolkit** (React) that gives you pre-made components (like doors, windows)
- **Hire a construction company** (Next.js) that provides the toolkit PLUS the blueprint, plumbing, electrical, and even handles the final inspection

**Next.js** is a React framework that gives you everything you need to build production-ready web applications without the headaches of configuration.

### The Simple Definition:
Next.js = React + Super Powers

**React gives you:**
- Components (reusable UI pieces)
- State management (interactive features)
- Fast rendering

**Next.js adds:**
- File-based routing (no manual setup)
- Automatic code splitting (faster page loads)
- Built-in optimization (images, fonts, performance)
- Multiple rendering modes (static, server, client)
- Production-ready defaults (SEO, performance)

---

## Why Not Just Use Plain React?

### Plain React (Create React App)

**The setup:**
```bash
npx create-react-app my-app
```

**What you get:**
- A single HTML file (`index.html`)
- All JavaScript loaded at once
- Client-side routing (you configure it)
- Manual optimization required
- No built-in SEO

**What you have to do yourself:**
1. Install and configure React Router
2. Set up code splitting manually
3. Configure image optimization
4. Set up build tools (Webpack, Babel)
5. Handle SEO manually (meta tags, etc.)
6. Configure deployment

**The problem:**
Your entire app loads at once. Even if the user only visits the homepage, they download code for every single page. Slow initial load!

### Next.js

**The setup:**
```bash
npx create-next-app my-app
```

**What you get:**
- File-based routing (automatic)
- Automatic code splitting (only load what's needed)
- Built-in image optimization
- Built-in font optimization
- SEO-friendly by default
- Multiple rendering modes
- Production-ready configuration

**What you DON'T have to do:**
1. ❌ No router configuration
2. ❌ No code splitting setup
3. ❌ No build tool configuration
4. ❌ No performance optimization headaches
5. ❌ No SEO configuration
6. ✅ Just build features!

**The benefit:**
Next.js automatically:
- Loads only the code for the current page
- Optimizes images and fonts
- Pre-renders pages for fast loading
- Handles SEO meta tags

---

## Real-World Analogy

### Plain React = DIY Home Building
You buy raw materials and tools. You're responsible for:
- Framing the walls
- Installing plumbing
- Setting up electricity
- Painting
- Landscaping
- Everything!

**Result:** Total control, but lots of work and potential mistakes.

### Next.js = Turnkey Home Construction
You get:
- Pre-approved blueprint (file structure)
- Professional contractors (built-in features)
- Building code compliance (best practices)
- Final inspection passed (production-ready)

**Result:** Focus on design and features, not infrastructure.

---

## How FitTracker AI Uses Next.js

The fitness app uses **Next.js 15** with the new **App Router** and **React 19**.

### Tech Stack:
```json
{
  "next": "15.5.4",         // Next.js framework
  "react": "19.1.0",        // React library
  "react-dom": "19.1.0",    // React DOM rendering
  "tailwindcss": "^4",      // Styling (utility-first CSS)
  "lucide-react": "^0.544.0", // Icon library
  "typescript": "^5"        // Type safety
}
```

### App Structure:

```
frontend/
├── app/                          ← Pages & routes (App Router)
│   ├── layout.tsx                ← Root layout (wraps all pages)
│   ├── page.tsx                  ← Home page (/)
│   ├── globals.css               ← Global styles
│   │
│   ├── calculator/
│   │   └── page.tsx              ← Energy calculator (/calculator)
│   │
│   ├── chatbot/
│   │   └── page.tsx              ← AI chatbot (/chatbot)
│   │
│   ├── workout-planner/
│   │   └── page.tsx              ← Workout planner (/workout-planner)
│   │
│   ├── tracking/
│   │   ├── dashboard/
│   │   │   └── page.tsx          ← Dashboard (/tracking/dashboard)
│   │   ├── nutrition/
│   │   │   └── page.tsx          ← Nutrition tracking (/tracking/nutrition)
│   │   ├── workouts/
│   │   │   └── page.tsx          ← Workout tracking (/tracking/workouts)
│   │   ├── weight/
│   │   │   └── page.tsx          ← Weight tracking (/tracking/weight)
│   │   └── progress/
│   │       └── page.tsx          ← Progress charts (/tracking/progress)
│   │
│   └── demo/
│       └── page.tsx              ← Demo page (/demo)
│
├── components/                   ← Reusable components
│   ├── health-chat.tsx           ← Chatbot UI component
│   ├── energy-calculator.tsx     ← Calculator form component
│   ├── workout-planner.tsx       ← Workout planner component
│   └── navigation.tsx            ← Navigation bar
│
├── public/                       ← Static assets (images, icons)
│   ├── favicon.ico
│   └── *.svg
│
├── next.config.ts                ← Next.js configuration
├── package.json                  ← Dependencies & scripts
├── tsconfig.json                 ← TypeScript configuration
├── tailwind.config.ts            ← Tailwind CSS configuration
├── .env.development              ← Local environment variables
└── .env.production               ← Production environment variables
```

---

## File-Based Routing

One of Next.js's best features: **routes are created automatically based on your file structure**.

### How it works:

**File structure:**
```
app/
├── page.tsx              → Route: /
├── calculator/
│   └── page.tsx          → Route: /calculator
├── chatbot/
│   └── page.tsx          → Route: /chatbot
└── tracking/
    ├── dashboard/
    │   └── page.tsx      → Route: /tracking/dashboard
    └── nutrition/
        └── page.tsx      → Route: /tracking/nutrition
```

**No router configuration needed!**

Compare this to plain React:

```javascript
// Plain React - you have to configure this manually
import { BrowserRouter, Routes, Route } from 'react-router-dom';

<BrowserRouter>
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="/calculator" element={<CalculatorPage />} />
    <Route path="/chatbot" element={<ChatbotPage />} />
    <Route path="/tracking/dashboard" element={<DashboardPage />} />
    <Route path="/tracking/nutrition" element={<NutritionPage />} />
  </Routes>
</BrowserRouter>
```

**Next.js:** Just create a folder and a `page.tsx` file. Done! ✅

---

## Special Files in Next.js

Next.js recognizes special file names for specific purposes:

### 1. `layout.tsx` - Shared Layout

**What it does:** Wraps all pages in a common structure (header, footer, fonts).

**Example:** `app/layout.tsx`
```tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {/* Navigation bar appears on ALL pages */}
        <Navigation />

        {/* Page content goes here */}
        {children}

        {/* Footer appears on ALL pages */}
        <Footer />
      </body>
    </html>
  );
}
```

**FitTracker's layout:**
```tsx
// app/layout.tsx
export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}  {/* Each page's content */}
      </body>
    </html>
  );
}
```

**Metadata (SEO):**
```tsx
export const metadata = {
  title: "Evidence-Based Fitness Coach",
  description: "AI-Powered Training & Nutrition Guide",
};
```

This automatically sets:
```html
<title>Evidence-Based Fitness Coach</title>
<meta name="description" content="AI-Powered Training & Nutrition Guide" />
```

### 2. `page.tsx` - The Actual Page

**What it does:** Defines the content for a specific route.

**Example:** `app/calculator/page.tsx`
```tsx
export default function CalculatorPage() {
  return (
    <main>
      <h1>Energy Calculator</h1>
      <EnergyCalculator />
    </main>
  );
}
```

**URL:** `https://yoursite.com/calculator`

### 3. `loading.tsx` - Loading State (Optional)

**What it does:** Shows a loading spinner while the page loads.

```tsx
// app/loading.tsx
export default function Loading() {
  return <div className="spinner">Loading...</div>;
}
```

### 4. `error.tsx` - Error Boundary (Optional)

**What it does:** Catches errors and shows a fallback UI.

```tsx
// app/error.tsx
export default function Error({ error, reset }) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <button onClick={reset}>Try again</button>
    </div>
  );
}
```

---

## Client vs Server Components

Next.js 13+ (App Router) introduces a new paradigm:

### Server Components (Default)

**What they are:** Components that run ONLY on the server, never in the browser.

**Example:**
```tsx
// app/page.tsx (Server Component by default)
export default function HomePage() {
  // This runs on the SERVER during build
  return <h1>Welcome!</h1>;
}
```

**Benefits:**
- Smaller JavaScript bundle (faster page loads)
- Direct database access (no API needed)
- Better security (secrets stay on server)

**Limitations:**
- No browser APIs (localStorage, window, etc.)
- No event handlers (onClick, onChange, etc.)
- No React hooks (useState, useEffect, etc.)

### Client Components

**What they are:** Components that run in the browser (interactive).

**How to use:** Add `'use client'` at the top of the file.

**Example:**
```tsx
'use client';  // ← This makes it a Client Component

import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}
```

**When to use:**
- Need interactivity (buttons, forms, etc.)
- Need browser APIs (localStorage, fetch, etc.)
- Need React hooks (useState, useEffect, etc.)

**FitTracker examples:**

**Server Component:**
```tsx
// app/chatbot/page.tsx (wrapper)
import HealthChat from '@/components/health-chat';

export default function ChatbotPage() {
  return (
    <main>
      <h1>AI Fitness Coach</h1>
      <HealthChat />  {/* Client component inside */}
    </main>
  );
}
```

**Client Component:**
```tsx
// components/health-chat.tsx
'use client';  // ← Interactive chatbot needs client-side

import { useState, useEffect } from 'react';

export default function HealthChat() {
  const [messages, setMessages] = useState([]);

  const sendMessage = async (text) => {
    // Fetch API call
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message: text })
    });
    // Update state
    setMessages([...messages, response]);
  };

  return (
    <div>
      {messages.map(msg => <div>{msg.content}</div>)}
      <input onSubmit={sendMessage} />
    </div>
  );
}
```

---

## Static Export for S3 Hosting

One of Next.js's coolest features: **export your entire app as static HTML files**.

### The Configuration

**File:** `next.config.ts`
```typescript
const nextConfig = {
  output: 'export',          // ← Export as static files
  trailingSlash: true,       // ← /about → /about/index.html
  images: {
    unoptimized: true        // ← Don't use Next.js image optimization
  }
};
```

### What This Does

**Without `output: 'export'`:**
- Next.js runs as a Node.js server
- Pages generated on request
- Requires a server to run

**With `output: 'export'`:**
- Next.js generates static HTML at build time
- All pages pre-rendered
- Can host on S3, Netlify, Vercel, GitHub Pages

### The Build Process

**Local development:**
```bash
npm run dev
# Starts development server at http://localhost:3000
# Hot reload (changes appear instantly)
```

**Production build:**
```bash
npm run build
# Outputs static files to `out/` directory
```

**Output structure:**
```
out/
├── index.html                    ← Home page (/)
├── 404.html                      ← Error page
├── calculator/
│   └── index.html                ← Calculator page
├── chatbot/
│   └── index.html                ← Chatbot page
├── tracking/
│   ├── dashboard/
│   │   └── index.html            ← Dashboard
│   └── nutrition/
│       └── index.html            ← Nutrition tracking
├── _next/
│   ├── static/
│   │   ├── chunks/               ← JavaScript bundles
│   │   └── css/                  ← CSS files
└── favicon.ico, *.svg            ← Static assets
```

**Result:** Pure static files that can be hosted anywhere!

---

## Local Development vs Cloud Deployment

### Local Development

**Start the dev server:**
```bash
cd frontend
npm run dev
```

**What happens:**
1. Next.js starts a development server on `http://localhost:3000`
2. Hot Module Replacement (HMR) enabled (changes appear instantly)
3. Uses `.env.development` for environment variables
4. Backend API: `http://localhost:8000` (local FastAPI server)

**Environment variables:**
```bash
# .env.development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**How it works:**
```
Browser
  ↓
Next.js Dev Server (localhost:3000)
  ↓
Local Backend API (localhost:8000)
  ↓
JSON files (data/tracking/*.json)
```

**Features:**
- ✅ Instant page refresh on code changes
- ✅ Detailed error messages
- ✅ React DevTools support
- ✅ No need to rebuild

**When to use:**
- Building new features
- Testing changes
- Debugging issues

---

### Cloud Deployment (Production)

**Build the static site:**
```bash
cd frontend
npm run build
```

**What happens:**
1. Next.js reads `.env.production` for environment variables
2. Pre-renders all pages as static HTML
3. Optimizes JavaScript bundles
4. Outputs to `out/` directory

**Environment variables:**
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://qj0nsm3f9a.execute-api.us-east-1.amazonaws.com
```

**Deploy to S3:**
```bash
# scripts/deploy.sh handles this
aws s3 sync out/ s3://health-chatbot-dev-frontend-123456789/
```

**How it works:**
```
Browser
  ↓
CloudFront CDN (caches static files)
  ↓
S3 Bucket (serves HTML, CSS, JS)

Separate API calls:
Browser → API Gateway → Lambda (Python FastAPI)
```

**Features:**
- ✅ Lightning-fast page loads (served from CDN)
- ✅ Global distribution (low latency worldwide)
- ✅ Cheap hosting (~$0.50/month for S3 + CloudFront free tier)
- ✅ No server maintenance

**When to use:**
- Production deployments
- Sharing with users
- Testing on real infrastructure

---

## Environment Variables

Next.js has built-in support for environment variables.

### How It Works

**Two types:**

1. **Server-only variables** (available only during build)
   ```
   DATABASE_URL=...
   SECRET_KEY=...
   ```

2. **Client-side variables** (exposed to browser, must start with `NEXT_PUBLIC_`)
   ```
   NEXT_PUBLIC_API_URL=https://api.example.com
   ```

### FitTracker's Environment Variables

**Local development (.env.development):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Production (.env.production):**
```bash
NEXT_PUBLIC_API_URL=https://qj0nsm3f9a.execute-api.us-east-1.amazonaws.com
```

### Using in Code

```tsx
// components/health-chat.tsx
'use client';

export default function HealthChat() {
  // Automatically uses the right URL based on environment
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const sendMessage = async (text) => {
    const response = await fetch(`${apiUrl}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message: text })
    });
  };
}
```

**What happens:**

| Environment | API URL |
|-------------|---------|
| Local (npm run dev) | `http://localhost:8000` (local backend) |
| Production (npm run build) | `https://qj0nsm3f9a...` (Lambda API Gateway) |

**The magic:** Same code works in both environments!

---

## Page Examples from FitTracker

### 1. Home Page (app/page.tsx)

**What it does:**
- Checks if user has completed setup (profile, workout plan)
- Shows progress indicators
- Recommends next action
- Displays feature cards (chatbot, calculator, planner, tracking)

**Key features:**
```tsx
'use client';  // ← Client component (uses useState, useEffect, localStorage)

export default function HomePage() {
  const [progress, setProgress] = useState({
    hasProfile: false,
    hasWorkoutPlan: false
  });

  useEffect(() => {
    // Check user progress on load
    const userId = localStorage.getItem('fit_tracker_user_id');
    // Fetch profile and workout plan status
  }, []);

  // Show recommended next step
  const getRecommendedAction = () => {
    if (!progress.hasProfile) return 'Calculate My Targets';
    if (!progress.hasWorkoutPlan) return 'Generate Workout Plan';
    return 'Go to Dashboard';
  };

  return (
    <div>
      <h1>Evidence-Based Fitness Tracking</h1>
      {/* Feature cards */}
    </div>
  );
}
```

**URL:** `https://yoursite.com/`

---

### 2. Chatbot Page (app/chatbot/page.tsx)

**What it does:**
- Imports the `HealthChat` component
- Wraps it in a layout with title and description

**Code:**
```tsx
import HealthChat from '@/components/health-chat';
import Navigation from '@/components/navigation';

export default function ChatbotPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-emerald-50 to-teal-50">
      <Navigation />
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold">AI Fitness Coach</h1>
        <p>Personalized coaching powered by your data</p>

        <HealthChat />  {/* The actual chatbot component */}

        <footer>
          Powered by OpenAI GPT-4, RAG (4,484 fitness documents)
        </footer>
      </div>
    </main>
  );
}
```

**URL:** `https://yoursite.com/chatbot`

---

### 3. Calculator Page (app/calculator/page.tsx)

**What it does:**
- Renders the energy calculator component
- Calculates TDEE, BMR, and macro targets

**Structure:**
```tsx
import EnergyCalculator from '@/components/energy-calculator';

export default function CalculatorPage() {
  return (
    <main>
      <h1>Energy Calculator</h1>
      <EnergyCalculator />
    </main>
  );
}
```

**URL:** `https://yoursite.com/calculator`

---

## Component Organization

FitTracker separates **pages** from **components**.

### Pages (app/)
- Define routes
- Import and compose components
- Usually simple wrappers

### Components (components/)
- Reusable UI elements
- Business logic
- Complex interactions

**Example:**

**Page (simple wrapper):**
```tsx
// app/chatbot/page.tsx
import HealthChat from '@/components/health-chat';

export default function ChatbotPage() {
  return (
    <main>
      <h1>AI Fitness Coach</h1>
      <HealthChat />  {/* Component does the work */}
    </main>
  );
}
```

**Component (complex logic):**
```tsx
// components/health-chat.tsx
'use client';

import { useState, useEffect } from 'react';

export default function HealthChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    setLoading(true);
    const response = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      body: JSON.stringify({ message: input })
    });
    const data = await response.json();
    setMessages([...messages, data]);
    setLoading(false);
  };

  return (
    <div className="chat-container">
      {messages.map(msg => (
        <div key={msg.id}>{msg.content}</div>
      ))}
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
```

---

## Styling with Tailwind CSS

FitTracker uses **Tailwind CSS 4** for styling.

### What is Tailwind?

**Traditional CSS:**
```css
/* styles.css */
.button {
  background-color: blue;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
}
```

```html
<button class="button">Click me</button>
```

**Tailwind CSS (utility-first):**
```html
<button class="bg-blue-600 text-white px-6 py-3 rounded-lg">
  Click me
</button>
```

**Benefits:**
- No need to name classes
- Styles are scoped to the element
- Faster development (no context switching)
- Automatic purging (removes unused CSS)

**FitTracker example:**
```tsx
export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <h1 className="text-5xl font-bold text-gray-900 mb-6">
        Evidence-Based Fitness Tracking
      </h1>
      <button className="bg-blue-600 text-white px-8 py-4 rounded-xl hover:shadow-lg">
        Get Started
      </button>
    </div>
  );
}
```

**Class meanings:**
- `min-h-screen` = minimum height: 100vh
- `bg-gradient-to-br` = background gradient (bottom-right)
- `from-blue-50` = gradient start color
- `text-5xl` = font size: 3rem
- `font-bold` = font weight: 700
- `px-8` = padding left/right: 2rem
- `py-4` = padding top/bottom: 1rem
- `rounded-xl` = border radius: 0.75rem
- `hover:shadow-lg` = large shadow on hover

---

## TypeScript Integration

FitTracker uses **TypeScript** for type safety.

### What is TypeScript?

**JavaScript (no types):**
```javascript
function greet(name) {
  return "Hello, " + name;
}

greet(123);  // No error, but wrong!
```

**TypeScript (with types):**
```typescript
function greet(name: string): string {
  return "Hello, " + name;
}

greet(123);  // ❌ Error: Argument of type 'number' is not assignable to 'string'
greet("John");  // ✅ Correct
```

**Benefits:**
- Catch errors before runtime
- Better IDE autocomplete
- Self-documenting code

**FitTracker example:**
```typescript
// components/health-chat.tsx
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface UserProgress {
  hasProfile: boolean;
  hasWorkoutPlan: boolean;
  userId: string | null;
}

export default function HomePage() {
  const [progress, setProgress] = useState<UserProgress>({
    hasProfile: false,
    hasWorkoutPlan: false,
    userId: null
  });

  // TypeScript knows `progress.hasProfile` is a boolean
  if (progress.hasProfile) {
    // ...
  }
}
```

---

## Build and Deployment Process

### Complete Deployment Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DEVELOPER: npm run build                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. NEXT.JS READS:                                           │
│    • .env.production (API_URL)                              │
│    • next.config.ts (output: 'export')                      │
│    • All pages and components                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. NEXT.JS BUILDS:                                          │
│    ① Pre-render all pages to static HTML                    │
│    ② Optimize JavaScript (minify, tree-shake)               │
│    ③ Optimize CSS (remove unused, minify)                   │
│    ④ Generate unique file hashes for caching                │
│    ⑤ Create _next/ directory with assets                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. OUTPUT TO out/ DIRECTORY:                                │
│    • index.html (home page)                                 │
│    • calculator/index.html                                  │
│    • chatbot/index.html                                     │
│    • _next/static/chunks/*.js (JavaScript bundles)          │
│    • _next/static/css/*.css (stylesheets)                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. DEPLOYMENT SCRIPT: scripts/deploy.sh                     │
│    • Sets NEXT_PUBLIC_API_URL from Terraform output         │
│    • Runs npm run build                                     │
│    • Syncs out/ to S3 bucket                                │
│    • Invalidates CloudFront cache                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. AWS INFRASTRUCTURE:                                      │
│    S3 Bucket (serves static files)                          │
│      ↓                                                       │
│    CloudFront CDN (caches globally)                         │
│      ↓                                                       │
│    Users worldwide (fast access)                            │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Script Snippet

**File:** `scripts/deploy.sh`
```bash
#!/bin/bash

# 1. Build backend (Lambda deployment package)
cd backend
python deploy.py
cd ..

# 2. Deploy infrastructure with Terraform
cd terraform
terraform apply -auto-approve
API_URL=$(terraform output -raw api_gateway_url)
FRONTEND_BUCKET=$(terraform output -raw s3_frontend_bucket)
cd ..

# 3. Build frontend with production API URL
cd frontend
echo "NEXT_PUBLIC_API_URL=${API_URL}" > .env.production
npm run build  # ← Generates static files in out/

# 4. Upload to S3
aws s3 sync out/ s3://${FRONTEND_BUCKET}/ --delete

# 5. Invalidate CloudFront cache
CLOUDFRONT_ID=$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[?DomainName=='${FRONTEND_BUCKET}.s3.amazonaws.com']].Id | [0]" --output text)
aws cloudfront create-invalidation --distribution-id ${CLOUDFRONT_ID} --paths "/*"

echo "✅ Deployment complete!"
echo "Frontend: https://$(terraform output -raw cloudfront_url)"
```

---

## Performance Optimizations

Next.js includes many automatic optimizations:

### 1. Automatic Code Splitting

**What it does:** Each page gets its own JavaScript bundle.

**Without code splitting:**
```
User visits home page → Downloads ALL JavaScript (1MB)
  ↓
Slow initial load (3+ seconds)
```

**With code splitting (Next.js):**
```
User visits home page → Downloads only home page JS (50KB)
  ↓
Fast initial load (<1 second)

User navigates to chatbot → Downloads chatbot JS (100KB)
  ↓
Fast subsequent page loads
```

**Result:** Pages load 10-20x faster!

### 2. Font Optimization

**What it does:** Automatically optimizes Google Fonts.

**Code:**
```tsx
// app/layout.tsx
import { Geist, Geist_Mono } from "next/font/google";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});
```

**What Next.js does:**
1. Downloads fonts at build time
2. Self-hosts them (no external requests)
3. Eliminates layout shift (reserves space)
4. Reduces page load time

**Result:** Fonts load instantly, no FOUT (Flash of Unstyled Text).

### 3. Image Optimization (Disabled for Static Export)

**Note:** FitTracker disables this because static export doesn't support it.

```typescript
// next.config.ts
images: {
  unoptimized: true  // Required for static export
}
```

**Why disabled:**
Next.js image optimization requires a server. Since we're exporting static files for S3, we can't use it.

**Alternative:**
Pre-optimize images before adding them to `public/`.

### 4. Route Prefetching

**What it does:** Automatically preloads pages when links are visible.

**Code:**
```tsx
<Link href="/chatbot">
  Go to Chatbot
</Link>
```

**What Next.js does:**
1. Detects the link is visible in viewport
2. Prefetches `/chatbot` JavaScript in background
3. When user clicks, page loads instantly

**Result:** Navigation feels instant!

---

## Common Next.js Concepts

### 1. The `<Link>` Component

**Never use `<a>` tags for internal navigation!**

**Bad (full page reload):**
```tsx
<a href="/calculator">Go to Calculator</a>
```

**Good (client-side navigation):**
```tsx
import Link from 'next/link';

<Link href="/calculator">Go to Calculator</Link>
```

**Benefits:**
- No page reload
- Instant navigation
- Automatic prefetching
- Preserves scroll position

### 2. The `useRouter` Hook

**What it does:** Access Next.js router programmatically.

```tsx
'use client';

import { useRouter } from 'next/navigation';

export default function MyComponent() {
  const router = useRouter();

  const navigateToCalc = () => {
    router.push('/calculator');
  };

  return <button onClick={navigateToCalc}>Go to Calculator</button>;
}
```

**Common methods:**
- `router.push('/path')` - Navigate to page
- `router.back()` - Go back
- `router.refresh()` - Reload current page

### 3. The `@` Import Alias

**What it does:** Shortcut for imports from project root.

**Configuration:** `tsconfig.json`
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

**Without alias:**
```tsx
import HealthChat from '../../../components/health-chat';
```

**With alias:**
```tsx
import HealthChat from '@/components/health-chat';
```

**Benefits:**
- Cleaner imports
- No relative path confusion
- Easy to refactor

---

## Development Workflow

### Starting Development

```bash
# Terminal 1: Start backend
cd backend
uv run uvicorn server:app --reload
# Backend running at http://localhost:8000

# Terminal 2: Start frontend
cd frontend
npm run dev
# Frontend running at http://localhost:3000
```

**What happens:**
1. Backend serves API at `localhost:8000`
2. Frontend serves pages at `localhost:3000`
3. Frontend calls backend API (CORS enabled)
4. Changes to code reload automatically

### Making Changes

**Scenario:** Add a new page for "Settings"

**Step 1:** Create the page
```bash
mkdir -p frontend/app/settings
touch frontend/app/settings/page.tsx
```

**Step 2:** Write the component
```tsx
// app/settings/page.tsx
'use client';

export default function SettingsPage() {
  return (
    <main>
      <h1>Settings</h1>
      <p>Configure your preferences</p>
    </main>
  );
}
```

**Step 3:** Navigate to it
```
http://localhost:3000/settings
```

**That's it!** Next.js automatically:
- Creates the `/settings` route
- Hot-reloads the page
- Adds code splitting

### Building for Production

```bash
cd frontend
npm run build
```

**Output:**
```
✓ Generating static pages (11/11)
✓ Finalizing page optimization

Route (app)                Size     First Load JS
┌ ○ /                      10.2 kB        95.4 kB
├ ○ /calculator           5.8 kB         90.2 kB
├ ○ /chatbot              6.1 kB         91.5 kB
├ ○ /tracking/dashboard   7.3 kB         92.7 kB
└ ○ /workout-planner      8.5 kB         93.9 kB

○ (Static) prerendered as static content
```

**What it means:**
- All pages pre-rendered as HTML
- JavaScript bundles optimized
- Ready to deploy to S3

---

## Comparison: Next.js vs Other Frameworks

| Framework | Type | Rendering | Deployment | Best For |
|-----------|------|-----------|------------|----------|
| **Next.js** | React | Static / SSR / SSG | Vercel, S3, anywhere | Full-stack apps |
| **Create React App** | React | Client-side only | S3, Netlify | Simple SPAs |
| **Gatsby** | React | Static only | S3, Netlify | Blogs, marketing sites |
| **Remix** | React | SSR | Node.js server | Dynamic apps |
| **Vue + Nuxt** | Vue | Static / SSR / SSG | Vercel, S3 | Vue apps |
| **SvelteKit** | Svelte | Static / SSR / SSG | Vercel, S3 | Modern SPAs |

**Next.js advantages:**
- Multiple rendering modes (flexible)
- Best-in-class developer experience
- Automatic optimizations
- Large ecosystem
- Excellent documentation

---

## Cost Breakdown

### Hosting Costs

**S3 + CloudFront (Static Export):**
```
S3 Storage:
- 100 MB website = $0.002/month

S3 Requests:
- 10,000 page views = 10,000 GET requests = $0.004

CloudFront:
- First 1 TB/month: FREE (AWS Free Tier)

Total: ~$0.01/month (essentially free!)
```

**Compare to:**
- Vercel Hobby Plan: $0/month (generous free tier)
- Netlify Free Plan: $0/month (100GB bandwidth)
- Traditional VPS: $5-10/month

**FitTracker uses S3 + CloudFront because:**
- Already using AWS (Lambda, DynamoDB)
- Full control over infrastructure
- Unlimited bandwidth with CloudFront free tier
- Terraform manages everything

---

## Troubleshooting Common Issues

### Issue 1: "Module not found" Error

**Error:**
```
Module not found: Can't resolve '@/components/health-chat'
```

**Cause:** TypeScript path alias not configured or wrong import.

**Solution:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

---

### Issue 2: "window is not defined"

**Error:**
```
ReferenceError: window is not defined
```

**Cause:** Trying to use browser APIs in a Server Component.

**Solution:** Add `'use client'` to the component.

```tsx
'use client';  // ← Add this

export default function MyComponent() {
  const data = localStorage.getItem('key');  // Now works!
}
```

---

### Issue 3: Static Export Doesn't Update

**Problem:** Changes not appearing after `npm run build`.

**Cause:** Old `out/` directory still cached.

**Solution:**
```bash
rm -rf out .next
npm run build
```

---

### Issue 4: API Calls Fail in Production

**Error:**
```
Failed to fetch: http://localhost:8000/api/...
```

**Cause:** Using wrong API URL (still using localhost).

**Solution:** Check `.env.production`:
```bash
# .env.production
NEXT_PUBLIC_API_URL=https://qj0nsm3f9a.execute-api.us-east-1.amazonaws.com
```

Rebuild:
```bash
npm run build
```

---

## Summary

**Next.js** is a React framework that provides everything you need to build modern web applications.

### Key Takeaways:

1. **File-Based Routing**: Create a file → Get a route (no configuration)
2. **Server + Client Components**: Best of both worlds (performance + interactivity)
3. **Static Export**: Deploy anywhere (S3, Netlify, Vercel, GitHub Pages)
4. **Automatic Optimizations**: Code splitting, font optimization, prefetching
5. **Developer Experience**: Fast refresh, TypeScript, great tooling

### FitTracker AI's Usage:

**What we built:**
- 11 pages (home, calculator, chatbot, planner, 5 tracking pages, demo)
- File-based routing (no router configuration)
- Static export to S3 (no server needed)
- Environment-based API URLs (local vs production)
- Tailwind CSS for styling
- TypeScript for type safety

**Deployment:**
```
Local Development:
  npm run dev → localhost:3000 → localhost:8000 API

Production:
  npm run build → out/ → S3 → CloudFront → Users
```

**Costs:**
- Development: $0 (localhost)
- Hosting: ~$0.01/month (S3 + CloudFront free tier)

**Performance:**
- Initial load: <1 second
- Navigation: Instant (prefetched)
- Global CDN: <100ms latency worldwide

Think of Next.js as **"React, but with all the hard parts solved for you."** You get file-based routing, automatic optimization, multiple rendering modes, and production-ready defaults—all without configuration headaches!
