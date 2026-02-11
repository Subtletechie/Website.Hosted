# SubtleTech Consulting Website

Cloud security consulting and education website.

## 🚀 Deploy to Vercel

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/subtletech.git
git push -u origin main
```

### Step 2: Deploy on Vercel
1. Go to [vercel.com](https://vercel.com) and sign in with GitHub
2. Click "New Project"
3. Import your `subtletech` repo
4. Vercel auto-detects Vite — just click "Deploy"
5. Your site is live! 🎉

### Step 3: Custom domain (optional)
1. In Vercel dashboard → your project → Settings → Domains
2. Add your domain (e.g., `subtletechconsulting.com`)
3. Update your domain's DNS as Vercel instructs

---

## ✏️ How to Edit Content

**All your content lives in one file: `src/content.js`**

### To update your site:
1. Open `src/content.js` in GitHub (click the pencil icon)
2. Make your changes
3. Commit — Vercel auto-deploys in ~30 seconds

### What you can edit:
- **Homepage hero** — title, subtitle
- **Stats** — numbers and labels
- **About page** — headline, bio, expertise, certifications
- **Testimonials** — add/edit/remove
- **Case studies** — add/edit/remove
- **Blog posts** — add new posts at the top of the array
- **Social links** — update URLs
- **Site settings** — email, copyright text

### Adding a new blog post:
Copy this template and paste it at the TOP of the `blogPosts` array:

```javascript
{
  id: "b9",                              // increment the number
  title: "Your Post Title Here",
  excerpt: "A short description shown on the blog card...",
  date: "Feb 10, 2026",
  read: "5 min",
  tags: ["Cloud Security", "AWS"],       // pick from available tags
  published: true,                       // set false for drafts
},
```

### Adding a testimonial:
Add to the `testimonials` array:

```javascript
{
  name: "Client Name",
  role: "Their Title / Company",
  text: "What they said about working with you...",
},
```

---

## 🛠️ Local Development

```bash
npm install
npm run dev
```

Opens at `http://localhost:5173`

## 📁 Project Structure

```
subtletech/
├── index.html          ← HTML entry point (SEO meta tags here)
├── package.json        ← Dependencies
├── vite.config.js      ← Build config
└── src/
    ├── main.jsx        ← React entry (don't touch)
    ├── content.js      ← ⭐ ALL YOUR CONTENT (edit this!)
    └── App.jsx         ← Site code (layout, pages, styles)
```

## Contact
subtletechie@outlook.com
