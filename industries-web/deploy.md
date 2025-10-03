# Deployment Guide

## Quick Deploy Options

### 1. Vercel (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Follow the prompts to connect to your GitHub repo
```

### 2. Netlify
```bash
# Install Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy --prod --dir .
```

### 3. GitHub Pages
1. Go to your repository settings
2. Scroll to "Pages" section
3. Select "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Your site will be available at `https://yourusername.github.io/industries-web`

### 4. Custom Domain Setup
1. Add your domain to your hosting platform
2. Update DNS records to point to your hosting provider
3. Update the `index.html` file with your actual domain

## Local Development
```bash
# Start local server
python -m http.server 8000

# Or with Node.js
npx serve .

# Visit http://localhost:8000
```

## Customization

### Update Links
- Replace `yourusername` with your actual GitHub username
- Update email addresses in the footer
- Add your actual social media links

### Add New Projects
1. Copy a project card in `index.html`
2. Update the content for your new project
3. Add appropriate links and features

### Styling
- All styles are in the `<style>` section of `index.html`
- Colors can be customized by changing the CSS variables
- Responsive design is already included
