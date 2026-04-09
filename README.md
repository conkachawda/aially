# AI Ally — Static Website

A 5-page static site for AI Ally Pty Ltd. Zero dependencies. Deploys to GitHub Pages, Netlify, Cloudflare Pages, or any static host.

## What's in here

```
site/
├── index.html              # Home
├── for-organisations.html  # Service tiers, framework, FAQ
├── for-students.html       # Bootcamp + apply
├── about.html              # Founders, mission, values
├── case-studies.html       # Two example case studies
├── css/style.css           # All styles, ~9 KB
├── js/main.js              # Mobile nav + console signature
├── assets/favicon.svg      # Brand mark favicon
├── robots.txt
├── sitemap.xml
├── CNAME                   # GitHub Pages custom domain
└── README.md
```

**Total weight:** under 30 KB before fonts. Loads in under 1 second on 4G.

## Brand colours used
- Ally Navy `#0A2540`
- Signal Orange `#FF6B35`
- Cloud White `#FAFBFC`
- Ink `#1A1A2E`
- Graphite `#6B7280`

## Fonts
Google Fonts (free, no API key):
- **Headings:** Space Grotesk (700)
- **Body:** Inter (400/500/600)

## Things to find-and-replace before going live

Search and replace across all `.html` files:

| Placeholder | Replace with |
|---|---|
| `[FOUNDER NAME]` | Your founder's full name |
| `[PARTNER NAME]` | Your partner/CEO's full name |
| `[TO BE FILLED]` (in footer ABN) | Your real ABN once registered |
| `hello@aially.com.au` | Confirm or change to your real address |
| `apply@aially.com.au` | Confirm or change to your real address |

Do this with VS Code's `Ctrl+Shift+H` (find & replace in files).

## Deploy options (in order of recommended)

### Option 1: GitHub Pages (recommended — free, integrated with Student Pack)

1. Create a new GitHub repo named `aially` (public — public repos get free Pages)
2. Push all the files in `site/` to the **root** of the repo (not in a `site/` subfolder)
3. Settings → Pages → Source: `Deploy from a branch` → Branch: `main` → Folder: `/ (root)`
4. Save. GitHub gives you a `https://yourusername.github.io/aially/` URL within ~1 minute
5. To use `aially.com.au` instead, add the CNAME (already in this folder) and configure DNS at your domain registrar

**Cost:** $0

### Option 2: Cloudflare Pages (also free, faster CDN)

1. Push to GitHub as above
2. Cloudflare dashboard → Pages → Create a project → Connect to Git
3. Build settings: leave all blank (it's static HTML)
4. Deploy

**Cost:** $0

### Option 3: Netlify (drag-and-drop, no Git needed)

1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag the entire `site/` folder onto the page
3. You get a `random-name-123.netlify.app` URL instantly
4. Domain settings → Add custom domain → `aially.com.au`

**Cost:** $0

## Connecting aially.com.au

Once domain is registered (Namecheap):
1. Namecheap → Domain List → `aially.com.au` → Manage → Advanced DNS
2. Add records depending on host:

**For GitHub Pages:**
```
Type   Host   Value
A      @      185.199.108.153
A      @      185.199.109.153
A      @      185.199.110.153
A      @      185.199.111.153
CNAME  www    yourusername.github.io.
```

**For Cloudflare Pages:**
```
CNAME  @      your-project.pages.dev
CNAME  www    your-project.pages.dev
```

**For Netlify:**
```
CNAME  @      your-site.netlify.app
CNAME  www    your-site.netlify.app
```

DNS propagation: 5 min – 24 hours.

## Local preview

Open `index.html` directly in a browser, or:

```bash
# Python 3
cd site
python -m http.server 8000
# → http://localhost:8000
```

## Future improvements (post-launch, not blocking)

- Add a real contact form (Formspree free tier or Netlify Forms)
- Add Google Analytics (or Plausible — privacy-friendly + Student Pack)
- Add Open Graph image (1200×630 PNG, Canva)
- Replace placeholder testimonials once Cohort 1 ships
- Add a `/privacy.html` page (legally required if collecting any data)
- Add a `/blog/` section once you have posts to publish

---

Built by Claude on 2026-04-08. Brand locked. Ready to ship.
