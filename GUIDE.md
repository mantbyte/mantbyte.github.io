# mantbytes — Complete Operations Guide

> Everything you need to run mantbytes daily. From first deploy to managing ads, blogs, and images — all from GitHub, all free.

---

## Table of Contents

1. [First-Time Setup: Getting Live on GitHub](#1-first-time-setup)
2. [How the Site Works (Architecture)](#2-how-the-site-works)
3. [Daily Blog Posting Workflow](#3-daily-blog-posting)
4. [Managing Images in Blog Posts](#4-managing-images)
5. [Managing Advertisements](#5-managing-advertisements)
6. [Contact Form Setup](#6-contact-form)
7. [Backend Systems (All Free)](#7-backend-systems)
8. [SEO & Analytics](#8-seo--analytics)
9. [Daily Operations Checklist](#9-daily-checklist)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. First-Time Setup: Publishing to GitHub

Since you mentioned you are publishing this at **mantbyte.github.io**, you have two options for how to structure your GitHub repository. Follow these exact steps to make your site live.

### Step 1: Prepare the `_config.yml` File

Before pushing your code, your `_config.yml` file must have the correct URLs.
Currently, your `url` and `baseurl` are empty (`""`). 

1. Open `_config.yml`.
2. Depending on your GitHub setup, update it:
   - **If your repository is exactly named `sujallohar.github.io`**:
     Leave both `url: ""` and `baseurl: ""` (or set `url: "https://sujallohar.github.io"`).
   - **If you created an organization named `mantbyte` and named the repo `mantbyte.github.io`**:
     Leave both `url: ""` and `baseurl: ""` (or set `url: "https://mantbyte.github.io"`).
   - **If your repo is just named `mantbyte` under your personal account (`sujallohar`)**:
     You MUST set `url: "https://sujallohar.github.io"` and `baseurl: "/mantbyte"`.

### Step 2: Create a GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. **Repository name**: Type your desired name (e.g., `sujallohar.github.io` or `mantbyte`).
3. **Visibility**: Public (required for free GitHub Pages).
4. **DO NOT** check "Add a README file" (you already have files on your computer).
5. Click **Create repository**.

### Step 3: Push Your Local Code to GitHub

Open the **Terminal** on your Mac. You will run these commands one by one to send your code from your local `gitMant` folder to GitHub.

```bash
# 1. Go into your website folder
cd /Users/sujalpanchal/Desktop/Hutsul/gitMant

# 2. Tell git to track this folder (only needed once)
git init

# 3. Add all your redesigned files to be committed
git add .

# 4. Save the files locally with a message
git commit -m "Initial launch of Mantbyte with premium redesign"

# 5. Connect your local folder to GitHub 
# IMPORTANT: Replace the URL below with YOUR actual repository URL from Step 2!
git remote add origin https://github.com/sujallohar/YOUR-REPO-NAME.git

# 6. Push the code to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Turn on GitHub Pages

1. Go to your repository page on GitHub.com.
2. Click **Settings** (the gear icon near the top right).
3. In the left sidebar, click **Pages**.
4. Under **Build and deployment**:
   - Source: Click the dropdown and select **GitHub Actions** (Do NOT choose "Deploy from a branch").
5. GitHub will automatically detect that you are using Jekyll and create a workflow. 
6. Click the **Actions** tab at the top of your repository. You will see a workflow running. Wait 1-2 minutes until it gets a green checkmark.

Congratulations! Your site is now live on the internet! Every time you write a new blog post and run `git push`, GitHub will automatically update your live website.

---

## 2. How the Site Works

```
mantbytes/
├── _config.yml              ← Site settings (edit author info, URLs here)
├── _data/
│   └── ads.yml              ← AD MANAGEMENT (add/remove ads here)
├── _includes/               ← Reusable components (header, footer, ads)
├── _layouts/                ← Page templates (post, page, default)
├── _posts/                  ← YOUR BLOG POSTS (add new .md files here)
├── assets/
│   ├── css/style.css        ← All styling
│   ├── js/                  ← JavaScript (search, progress bar)
│   └── images/
│       ├── posts/           ← BLOG POST IMAGES (upload here)
│       └── ads/             ← ADVERTISEMENT IMAGES (upload here)
├── category/                ← Category pages (Tech, News, Geopolitics)
├── contact.html             ← Contact page
├── index.html               ← Homepage
├── feed.xml                 ← RSS feed (auto-generated)
├── sitemap.xml              ← Sitemap (auto-generated)
└── .github/workflows/       ← CI/CD automation
```

**The key principle**: You only ever need to touch 3 things:
1. `_posts/` — to add blogs
2. `assets/images/` — to upload images
3. `_data/ads.yml` — to manage ads

Everything else is automated.

---

## 3. Daily Blog Posting

### Method 1: Write Directly on GitHub (Recommended)

This is the fastest method — you don't even need a computer with Git installed.

#### Step 1: Go to your repository on GitHub

Navigate to `https://github.com/sujallohar/mantbytes`

#### Step 2: Create a new post file

1. Click on the `_posts` folder
2. Click **"Add file"** → **"Create new file"**
3. **Name the file** using this exact format:
   ```
   YYYY-MM-DD-your-post-title.md
   ```
   Example: `2026-07-24-how-blockchain-secures-healthcare.md`

#### Step 3: Write the front matter (COPY THIS TEMPLATE)

```yaml
---
layout: post
title: "Your Post Title Here"
date: 2026-07-24 10:00:00 +0530
categories: Tech
excerpt: "A one-line summary of the post. Shows on homepage cards."
cover_image: "/assets/images/posts/your-image.jpg"
cover_caption: "Optional caption below the image"
---

Your blog content starts here. Write in Markdown.

## Subheading

Regular paragraph text. You can use **bold**, *italic*, and [links](https://example.com).

### Another Section

- Bullet point 1
- Bullet point 2

> This is a blockquote for highlighting important text.

```code
Code blocks work too
```
```

> [!IMPORTANT]
> **Available categories**: `Tech`, `News`, `Geopolitics`
> 
> **Date format**: `YYYY-MM-DD HH:MM:SS +0530` (the +0530 is IST timezone)
> 
> **cover_image**: Optional. If you don't have an image, just remove this line.

#### Step 4: Commit the file

1. Scroll down to "Commit new file"
2. Write a commit message: `Add post: How Blockchain Secures Healthcare`
3. Keep "Commit directly to the `main` branch" selected
4. Click **"Commit new file"**

**Done!** GitHub Actions will auto-build. Your post will be live in ~2 minutes.

---

### Method 2: Write Locally and Push

If you prefer writing offline:

```bash
# 1. Navigate to your project
cd /Users/sujalpanchal/Desktop/Hutsul/gitMant

# 2. Create a new post file
touch _posts/2026-07-24-my-new-post.md

# 3. Open it in any editor and write your content
# (Use VS Code, or any text editor)

# 4. Push to GitHub
git add .
git commit -m "Add post: My New Post"
git push
```

---

## 4. Managing Images

### Blog Post Cover Images

#### Uploading via GitHub Web:

1. Go to `assets/images/posts/` in your repo
2. Click **"Add file"** → **"Upload files"**
3. Drag and drop your image
4. Commit: `Add cover image for July 24 post`

#### Referencing in your post:

```yaml
cover_image: "/assets/images/posts/blockchain-healthcare.jpg"
cover_caption: "Illustration of federated blockchain architecture"
```

#### Inline images in post body:

```markdown
Here's a diagram of the architecture:

![System architecture diagram](/assets/images/posts/architecture-diagram.png)

As you can see in the diagram above...
```

### Image Best Practices

| Rule | Why |
|------|-----|
| Keep images under **500KB** | Fast loading on mobile |
| Use `.jpg` for photos | Smaller file size |
| Use `.png` for diagrams/screenshots | Crisp text and lines |
| Name files descriptively | `federated-learning-diagram.png` not `IMG_1234.png` |
| Resize to **max 1200px wide** | Larger images waste bandwidth |

> [!TIP]
> **Quick resize on Mac**: Open image in Preview → Tools → Adjust Size → Set width to 1200px → Save.

---

## 5. Managing Advertisements

Your site has a **data-driven ad management system**. All ads are controlled from a single file: `_data/ads.yml`. No code changes needed ever.

### How It Works

```
You get an ad from a local connection
    ↓
Upload the ad image to: assets/images/ads/
    ↓
Edit _data/ads.yml → set active: true
    ↓
Push to GitHub → Ad goes live in 2 minutes
```

### Adding a New Ad

#### Step 1: Upload the ad image

1. Go to `assets/images/ads/` in your GitHub repo
2. Upload the banner image (recommended: 728×90 or 970×250 pixels)
3. Commit: `Add ad image for [Client Name]`

#### Step 2: Edit the ads config

1. Go to `_data/ads.yml` in your repo
2. Click the **pencil icon** (edit)
3. Find the location where you want the ad, and update it:

```yaml
- location: "home-page"
  active: true                                    # ← Change to true
  image: "/assets/images/ads/client-banner.jpg"   # ← Your image path
  link: "https://clientwebsite.com"               # ← Where the ad links to
  alt: "Client Name - Special Offer"              # ← Description
  client: "Client Name"                           # ← Your reference
  start_date: "2026-07-24"                        # ← When it starts
  end_date: "2026-08-24"                          # ← When to remove it
```

4. Commit: `Activate home-page ad for [Client Name]`

#### Ad Locations

| Location | Where it appears |
|----------|-----------------|
| `home-page` | Homepage, below the hero section |
| `archive-page` | Archive page, below the title |
| `in-article` | Inside blog posts, below the title |
| `bottom-article` | Inside blog posts, at the very bottom |

#### Removing / Pausing an Ad

Just change `active: true` to `active: false` and push. The ad disappears instantly (next build). The image stays in your repo for records.

#### Ad Image Sizes (Recommended)

| Location | Recommended Size | Format |
|----------|-----------------|--------|
| Home page | 728 × 90 px (leaderboard) | JPG |
| Archive page | 728 × 90 px | JPG |
| In-article | 728 × 250 px (rectangle) | JPG/PNG |
| Bottom article | 728 × 90 px | JPG |

---

## 6. Contact Form

The contact form at `/contact` sends messages to **sujapanchal17@gmail.com** using [FormSubmit.co](https://formsubmit.co/).

### First-Time Activation

1. Go to your live site's contact page
2. Submit a test message (fill all fields)
3. Check your email (`sujapanchal17@gmail.com`) for a **confirmation email** from FormSubmit
4. Click the confirmation link
5. Done! All future submissions go directly to your inbox

**Cost**: Free forever. No account needed.

### What you receive

For each form submission, you get an email with:
- Sender's name
- Sender's email
- Subject
- Message
- Formatted as a clean table

---

## 7. Backend Systems

All backend features run **100% free** on GitHub — no server, no hosting costs.

### 7.1 GitHub Actions (CI/CD)

**What it does**: Every time you push code (add a post, update an ad, change anything), GitHub automatically:
1. Checks out your code
2. Installs Ruby and Jekyll
3. Builds the entire site
4. Deploys it to GitHub Pages

**You don't have to do anything** — it runs on every push.

**To check build status**:
1. Go to your repo → **Actions** tab
2. See green ✅ (success) or red ❌ (failed)
3. If failed, click to see error logs

**File**: [deploy.yml](file:///Users/sujalpanchal/Desktop/Hutsul/gitMant/.github/workflows/deploy.yml)

---

### 7.2 RSS Feed

**What it does**: Generates an RSS feed at `/feed.xml` so readers can subscribe using any RSS reader (Feedly, Inoreader, etc.)

**Auto-updates**: Every time you add a post and push, the feed updates automatically.

**Share this URL** with your readers:
```
https://yourusername.github.io/mantbytes/feed.xml
```

**File**: [feed.xml](file:///Users/sujalpanchal/Desktop/Hutsul/gitMant/feed.xml)

---

### 7.3 Sitemap

**What it does**: Generates an XML sitemap at `/sitemap.xml` for search engines (Google, Bing). Helps your blog get indexed and found.

**Auto-updates**: New posts automatically appear in the sitemap.

**Submit to Google**: 
1. Go to [Google Search Console](https://search.google.com/search-console)
2. Add your site
3. Submit your sitemap URL: `https://yourusername.github.io/mantbytes/sitemap.xml`

**File**: [sitemap.xml](file:///Users/sujalpanchal/Desktop/Hutsul/gitMant/sitemap.xml)

---

### 7.4 Client-Side Search

**What it does**: Generates a JSON search index at `/search.json`. The search bar in the header searches across all post titles, content, and categories — entirely in the browser, no server needed.

**Auto-updates**: New posts are automatically indexed.

**File**: [search.json](file:///Users/sujalpanchal/Desktop/Hutsul/gitMant/search.json)

---

### 7.5 Contact Form Backend

**What it does**: FormSubmit.co acts as a backend relay. Form submissions are POSTed to their server, which forwards them as emails to you.

**Features included**:
- Honeypot spam protection (invisible field)
- Custom email subject line
- Table-formatted emails
- No CAPTCHA needed

**File**: [contact.html](file:///Users/sujalpanchal/Desktop/Hutsul/gitMant/contact.html)

---

### 7.6 Data-Driven Ad System

**What it does**: Acts like a lightweight CMS for ads. Instead of editing HTML code, you just edit a YAML config file. The Jekyll build system reads the data and renders the appropriate ads.

**How it's "backend"**: The `_data/ads.yml` file is your admin panel. You update it, push, and the build pipeline processes and deploys the changes automatically.

**File**: [ads.yml](file:///Users/sujalpanchal/Desktop/Hutsul/gitMant/_data/ads.yml)

---

## 8. SEO & Analytics

### Google Analytics 4 (GA4)

I have fully integrated the code to support Google Analytics 4. GA4 is completely free and will automatically track:
- Daily visitors & Page views
- Returning users vs New users
- Popular articles (which pages get the most traffic)
- Traffic sources (where users are coming from: Google, Twitter, direct links)
- Countries and Devices (Mobile vs Desktop)

**How to activate it:**
1. Go to [analytics.google.com](https://analytics.google.com/) and create a free account.
2. Create a "Property" for your website (e.g., Mantbyte).
3. Set up a "Web Data Stream" and enter your website URL (e.g., `mantbyte.github.io`).
4. Google will give you a **Measurement ID** that starts with `G-` (e.g., `G-12345ABCD`).
5. Open your `_config.yml` file.
6. Replace the placeholder in the `google_analytics` field with your actual ID:
   ```yaml
   google_analytics: "G-12345ABCD"
   ```
7. Commit and push! The tracking script will now automatically load on every page of your site.

---

### Already Built-In SEO

Your site automatically generates everything needed for search engines:
- ✅ Dynamic `<title>` tags on every page
- ✅ Meta descriptions from post excerpts
- ✅ Semantic HTML structure
- ✅ RSS feed for subscribers
- ✅ XML sitemap for search engines
- ✅ Canonical URLs to avoid duplicate content
- ✅ Clean, readable URLs

### Add Free Analytics (Optional)

#### Option A: GoatCounter (Recommended — Privacy-Focused, Free)

1. Go to [goatcounter.com](https://www.goatcounter.com/) → Sign up (free)
2. Get your script tag (looks like `<script data-goatcounter="https://YOURSITE.goatcounter.com/count" ...>`)
3. Add it to `_layouts/default.html` just before `</body>`
4. Push → Done! View your dashboard at `YOURSITE.goatcounter.com`

#### Option B: Google Analytics (Free)

1. Create an account at [analytics.google.com](https://analytics.google.com/)
2. Get your measurement ID (G-XXXXXXXXXX)
3. Add the script to `_layouts/default.html` in the `<head>` section
4. Push → Done!

---

## 9. Daily Operations Checklist

### Every Day (Blog Posting)

```
□ Write your blog post in Markdown
□ Upload cover image to assets/images/posts/ (if using one)
□ Create the .md file in _posts/ with proper front matter
□ Commit and push (or commit directly on GitHub)
□ Wait 2 minutes → check the live site
```

### When You Get a New Ad Client

```
□ Get the ad banner image from the client
□ Resize it to the recommended size (728×90 or 728×250)
□ Upload to assets/images/ads/
□ Edit _data/ads.yml → set active: true, fill in details
□ Commit and push
□ Note the end_date — set a reminder to deactivate
```

### When an Ad Expires

```
□ Edit _data/ads.yml → set active: false for that slot
□ Commit and push
□ (Keep the image in the repo for your records)
```

### Weekly

```
□ Check GitHub Actions tab for any failed builds
□ Review contact form submissions in your email
□ Check ad end_dates — deactivate expired ads
□ Review site analytics (if set up)
```

### Monthly

```
□ Update _config.yml if any personal details changed
□ Review and clean up old ad images if needed
□ Submit sitemap to Google Search Console (first month only)
□ Check that all links on the site still work
```

---

## 10. Troubleshooting

### "My post isn't showing up"

1. **Check the filename**: Must be `YYYY-MM-DD-title.md` exactly
2. **Check the date**: Posts dated in the **future** won't show. Make sure the date is today or earlier
3. **Check front matter**: The `---` at top and bottom must be present
4. **Check GitHub Actions**: Go to Actions tab — is the build green?

### "My ad isn't showing"

1. **Check `active`**: Must be `true` (not `"true"` in quotes)
2. **Check the image path**: Must start with `/assets/images/ads/` and the file must exist
3. **Check indentation**: YAML is sensitive to spaces. Use 2-space indentation

### "The build failed" (red ❌ in Actions)

1. Click on the failed run in the Actions tab
2. Read the error message
3. Common causes:
   - Invalid YAML in `_config.yml` or `_data/ads.yml` (check spacing)
   - Missing `---` in a post's front matter
   - Unclosed Liquid tags in HTML files

### "Contact form isn't working"

1. Did you confirm the FormSubmit activation email?
2. Check your spam folder
3. Try submitting again — FormSubmit sends a new confirmation if the first expired

### "Images aren't loading"

1. Check the path is correct and starts with `/assets/images/`
2. Make sure the filename matches exactly (case-sensitive!)
3. Check that the file was actually committed and pushed

---

## Quick Reference Card

| Task | What to do |
|------|-----------|
| **New blog post** | Create `.md` in `_posts/` → commit |
| **Add post image** | Upload to `assets/images/posts/` → reference in front matter |
| **Activate an ad** | Edit `_data/ads.yml` → `active: true` → commit |
| **Deactivate an ad** | Edit `_data/ads.yml` → `active: false` → commit |
| **Update contact info** | Edit `_config.yml` → author section → commit |
| **Check if site built** | Repo → Actions tab → look for green ✅ |
| **View RSS feed** | `/feed.xml` on your live site |
| **View sitemap** | `/sitemap.xml` on your live site |

---

*This guide is for mantbytes, the personal blog of Sujal Lohar. All systems run free on GitHub Pages + GitHub Actions.*
