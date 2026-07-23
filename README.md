# mantbytes - Personal Blog

A lightweight, purely static personal blogging website powered by Jekyll and designed for GitHub Pages. Built with zero dependencies, no databases, and a clean, editorial layout.

## How to Enable GitHub Pages

1. Push this code to a GitHub repository.
2. Go to your repository **Settings**.
3. Click on **Pages** in the left sidebar.
4. Under "Build and deployment", set the **Source** to "Deploy from a branch".
5. Set the **Branch** to `main` (or `master`) and select the `/(root)` folder.
6. Click **Save**. Your site will be live at `https://yourusername.github.io/your-repo-name/` shortly.

## How to Write a New Post

Writing a new post is as simple as adding a Markdown file to the `_posts/` folder and pushing it to GitHub.

1. Create a new file in the `_posts/` directory.
2. Name the file with the following format: `YYYY-MM-DD-your-post-title.md` (e.g., `2026-07-25-my-new-post.md`).
3. Add the required YAML front matter at the very top of the file:

```yaml
---
layout: post
title: "Your Post Title Here"
date: 2026-07-25 10:00:00 +0530
categories: Tech
excerpt: "A short summary of what this post is about. This will show up on the homepage and archive."
cover_image: "/assets/images/posts/your-image.jpg"
cover_caption: "Optional caption for the image"
---
```

**Available Categories:** `News`, `Geopolitics`, `Tech`

4. Write your post content below the front matter using standard Markdown.
5. Commit and push the file to GitHub using the web UI ("Add file" -> "Create new file") or via git commands:
   ```bash
   git add _posts/2026-07-25-my-new-post.md
   git commit -m "Add new post about tech"
   git push origin main
   ```

*Note: GitHub Pages usually takes 1-3 minutes to reflect your changes live after a push.*

## How to Add Images to Posts

### Cover Image (Banner at the top of the post)

1. Upload your image to the `assets/images/posts/` folder in your repository.
2. In your post's front matter, add the `cover_image` field:

```yaml
cover_image: "/assets/images/posts/my-cover-photo.jpg"
cover_caption: "Photo credit or description"
```

The cover image will appear as a full-width banner at the top of the post and as a thumbnail on the homepage cards.

### Inline Images (Inside the post body)

You can add images anywhere in the body of your post using standard Markdown:

```markdown
![Description of the image](/assets/images/posts/my-inline-image.jpg)
```

### Uploading Images via GitHub Web UI

1. Go to the `assets/images/posts/` folder in your repository on GitHub.
2. Click **"Add file"** → **"Upload files"**.
3. Drag and drop your images and commit.
4. Reference them in your post using the path `/assets/images/posts/filename.jpg`.

**Tip:** Keep image file sizes under 1MB for fast loading. Use `.jpg` for photos and `.png` for screenshots or diagrams.

## Contact Form

The contact page uses [FormSubmit.co](https://formsubmit.co/) to deliver form submissions to your email. The first time someone submits the form, you will receive a confirmation email from FormSubmit — click the link in it to activate the endpoint. After that, all submissions go directly to your inbox. No account needed.

## Local Development (Optional)

If you want to view the site locally before pushing:
1. Make sure you have Ruby and Bundler installed.
2. Install Jekyll: `gem install jekyll bundler`
3. Run `jekyll serve` from the project root.
4. Open `http://localhost:4000` in your browser.
