---
layout: post
title: "Building Mantbytes: A Modern, Free, Serverless Blog Architecture"
date: 2026-07-24 10:00:00 +0530
categories: Tech
excerpt: "How I built a high-performance, fully-featured tech blog with authentication, databases, and ad management using 100% free cloud infrastructure."
---

When setting out to build **Mantbytes**, I had a clear goal: create a high-performance, premium-feeling tech publication without spending a dime on hosting, databases, or backend servers. 

The result is a fully serverless architecture that combines the blazing speed of static site generation with the dynamic capabilities of a traditional full-stack application.

Here is a deep dive into the technology stack and high-end features that power Mantbytes.

---

## 1. 100% Free Cloud Infrastructure

The core of the application relies entirely on free, enterprise-grade cloud services. 

- **Hosting & CDN**: The site is hosted on **GitHub Pages**. Because it serves static HTML/CSS/JS, it is incredibly fast, globally distributed via GitHub's CDN, and costs $0.
- **CI/CD Pipeline**: I use **GitHub Actions** for continuous integration and deployment. Every time I push a new markdown file or update a configuration, a GitHub Action automatically spins up a virtual environment, installs Jekyll, builds the entire site from scratch, and deploys the compiled code to production in under 60 seconds.

## 2. Dynamic Backend: Authentication & Database

Static sites usually lack interactivity. To solve this, I integrated **Firebase** directly into the frontend using client-side JavaScript. This gives the blog a "full-stack" feel without a traditional Node.js or Python backend server.

### Authentication
We use **Firebase Authentication** to handle user logins. Users can create an account and log in securely to interact with the content. This prevents spam and ensures that interactions are tied to real users.

### Database (Firestore)
For data persistence, we use **Cloud Firestore**, a NoSQL document database. This powers our real-time interactive features:
- **Comments System**: Authenticated users can leave comments on individual blog posts. The comments are stored in Firestore and fetched dynamically via JavaScript when the page loads.
- **Engagement Metrics**: We built a custom Reddit-style upvote/downvote system, along with a "Like" counter and a "Save for later" bookmarking feature. All of these interactions are securely written to Firestore in real-time. Strict security rules (`firestore.rules`) ensure that users can only modify their own votes and data.

## 3. Email & Request Handling

Handling form submissions on a static site can be tricky without a backend server to process the POST requests. 

For the **Contact Page**, we implemented **FormSubmit**. It acts as a serverless endpoint. When a user fills out the contact form, the HTML form sends a POST request directly to FormSubmit's API, which then formats the data and forwards it directly to my personal email address. It handles spam filtering and Captchas automatically, completely eliminating the need for a custom backend route or email server.

## 4. Custom Ad Management System

Monetization and sponsorships are crucial for publications. Instead of relying on bloated third-party ad networks that slow down the site, I built a **Custom YAML-based Ad Engine**.

- **Configuration**: Ads are managed in a simple `_data/ads.yml` file. I can define the ad image, the sponsor's link, start/end dates, and toggle them active or inactive.
- **Injection**: Using Jekyll's Liquid templating, ad slots are dynamically injected into specific locations (Homepage, Archive, Top of Article, Bottom of Article).
- **Performance**: Because the ads are compiled statically at build time, there are no heavy JavaScript trackers or external API calls. The ads load instantly with the rest of the page content.

## 5. High-End UI/UX Features

To make the reading experience feel premium, we implemented several advanced frontend features:

- **Client-Side Category Filtering**: On the homepage, users can filter posts by category (Tech, News, Geopolitics) instantly. We use Vanilla JavaScript to toggle visibility without reloading the page.
- **Reading Progress Bar**: A sleek progress bar fixed to the top of the screen fills up as the user scrolls through a long article, providing visual feedback on their reading progress.
- **Responsive Grid & List Layouts**: The CSS utilizes modern CSS Grid and Flexbox to create a fluid, responsive design. We use a hybrid layout where featured posts get a horizontal 50/50 split on desktop, while regular posts adapt to a clean vertical stack.

## 6. SEO & Discoverability

To ensure the content reaches a wide audience, we heavily optimized the site for search engines:
- **Jekyll SEO Tag**: Automatically generates perfectly formatted meta tags, Open Graph tags for social sharing (Twitter/LinkedIn cards), and JSON-LD structured data.
- **Auto-Generated Sitemap**: The `jekyll-sitemap` plugin automatically builds an XML sitemap of every post and page, which is submitted to **Google Search Console** for rapid indexing.
- **RSS Feed**: The `jekyll-feed` plugin generates an Atom feed, allowing readers to subscribe to the blog using Feedly or other RSS readers.

---

### Conclusion

By combining the speed and security of a Static Site Generator (Jekyll) with the dynamic power of Firebase and GitHub Actions, Mantbytes achieves the best of both worlds. It is highly performant, completely free to host, and incredibly easy to maintain.
