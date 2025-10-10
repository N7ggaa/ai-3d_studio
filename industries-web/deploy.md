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
GitHub Pages deployment is automated via GitHub Actions.

1. **Enable GitHub Pages**:
   - Go to your repository settings
   - Scroll to "Pages" section
   - Select "GitHub Actions" as the source

2. **Automatic Deployment**:
   - The site deploys automatically when you push changes to the `industries-web/` folder on the `main` branch
   - The workflow deploys the contents of `industries-web/` as the root of your site

3. **Site URL**:
   - Your site will be available at `https://yourusername.github.io/repository-name/`
   - For this repository, it will be `https://N7ggaa.github.io/ai-3d_studio/`

### 4. Free Subdomain Setup (username.github.io)
The GitHub Pages URL serves as your free subdomain. No additional setup is required beyond enabling Pages as described above.

- **Project Site**: `https://yourusername.github.io/repository-name/` (current setup)
- **User/Organization Site**: To use `https://yourusername.github.io/` as root, create a new repository named `yourusername.github.io` and move the site files there.

### 5. Custom Domain Setup
1. **Add Custom Domain in GitHub**:
   - Go to repository Settings → Pages
   - In the "Custom domain" field, enter your domain (e.g., `www.yourdomain.com` or `yourdomain.com`)
   - Click Save

2. **Update DNS Records**:
   - Go to your domain registrar's DNS settings
   - Add a CNAME record pointing `www.yourdomain.com` to `yourusername.github.io`
   - Or add an A record for the apex domain pointing to GitHub's IP addresses:
     - 185.199.108.153
     - 185.199.109.153
     - 185.199.110.153
     - 185.199.111.153

3. **Enforce HTTPS**:
   - GitHub Pages will automatically provision an SSL certificate
   - Ensure "Enforce HTTPS" is checked in Pages settings

4. **Update Site Content** (Optional):
   - Update any hardcoded URLs in `index.html` if needed

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
