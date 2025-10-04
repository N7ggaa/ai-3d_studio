# ModelForge Website

Official website and download hub for **ModelForge** - The ultimate AI-powered 3D model generation platform.

## 🚀 Features

- **Modern Landing Page** - Showcases ModelForge capabilities with stunning visuals
- **Feature Highlights** - Detailed overview of AI 3D generation, YouTube to 3D, and Roblox integration
- **Download Section** - Platform-specific download options for desktop and web versions
- **Screenshot Gallery** - Visual demonstrations of ModelForge in action
- **System Requirements** - Clear specifications for optimal performance
- **SEO Optimized** - Built for discoverability and search engine ranking
- **Responsive Design** - Perfect experience on desktop, tablet, and mobile
- **Production Ready** - Optimized for deployment to Netlify, GitHub Pages, or any static hosting

## 🎨 Design Features

- **Dark Theme** - Modern dark UI with glass morphism effects
- **Gradient Accents** - Beautiful green-blue gradients matching ModelForge branding
- **Smooth Animations** - Subtle hover effects and scroll-triggered animations
- **Interactive Elements** - Engaging user interactions and feedback
- **Performance Optimized** - Fast loading with lazy images and efficient CSS

## 🛠️ Technology Stack

- **HTML5** - Semantic markup with proper accessibility
- **CSS3** - Modern styling with CSS Grid, Flexbox, and custom properties
- **Vanilla JavaScript** - No dependencies, pure performance
- **Feather Icons** - Beautiful, lightweight icon library
- **Inter Font** - Modern, readable typography

## 🚀 Quick Start

### Local Development

```bash
# Clone the repository
git clone https://github.com/modelforge/website.git
cd website

# Start development server
npm run dev
# or
python -m http.server 8000

# Open http://localhost:8000 in your browser
```

### Production Deployment

#### Netlify (Recommended)

1. **Connect Repository**
   - Push your code to GitHub
   - Connect to Netlify via GitHub integration
   - Auto-deploys on every push to main branch

2. **Manual Deploy**
   ```bash
   # Install Netlify CLI (optional)
   npm install -g netlify-cli

   # Deploy to production
   npm run deploy-netlify
   ```

#### GitHub Pages

1. **Enable Pages**
   - Go to repository Settings → Pages
   - Select "GitHub Actions" as source

2. **Deploy**
   ```bash
   # Install gh-pages package
   npm install

   # Deploy to GitHub Pages
   npm run deploy-github
   ```

#### Manual Hosting

Simply upload the files to any static hosting provider:
- **Vercel** - Drag and drop deployment
- **Firebase Hosting** - `firebase deploy`
- **Surge.sh** - `surge .`
- **Traditional Hosting** - Upload via FTP/SFTP

## 📁 Project Structure

```
website/
├── index.html          # Main landing page
├── package.json        # Project configuration
├── netlify.toml        # Netlify deployment config
├── README.md          # This file
└── .gitignore         # Git ignore rules
```

## 🎯 Key Sections

### Hero Section
- Compelling headline and value proposition
- Key statistics and social proof
- Multiple call-to-action buttons
- Animated background effects

### Features Section
- **Text-to-3D Generation** - Natural language model creation
- **Image-Guided Creation** - Reference image processing
- **YouTube to 3D** - Video content conversion
- **Roblox Integration** - Direct game asset creation
- **Multiple Export Formats** - Industry-standard file types
- **Batch Processing** - Efficient workflow management

### Download Section
- **Desktop Application** - Full-featured native app
- **Web Version** - Browser-based access
- **Mobile Apps** - Coming soon for iOS/Android
- **Platform Requirements** - Clear system specifications

### Technical Features
- **Responsive Design** - Mobile-first approach
- **SEO Optimization** - Meta tags, structured data, sitemap ready
- **Performance** - Optimized assets and lazy loading
- **Accessibility** - WCAG compliant design
- **Cross-browser** - Works on all modern browsers

## 🔧 Customization

### Branding
Update CSS custom properties in `index.html`:
```css
:root {
  --primary-gradient: linear-gradient(135deg, #4CAF50 0%, #2196F3 100%);
  --glass-bg: rgba(255, 255, 255, 0.05);
  --text-primary: rgba(255, 255, 255, 0.95);
}
```

### Content
- Edit text content directly in `index.html`
- Replace placeholder images with actual screenshots
- Update download links to point to real releases

### Styling
- Modify CSS in the `<style>` section
- Add custom animations and effects
- Adjust responsive breakpoints as needed

## 📊 Performance

- **Lighthouse Score** - Optimized for 90+ scores
- **Core Web Vitals** - Fast loading and interaction
- **Accessibility** - WCAG 2.1 AA compliant
- **SEO** - Search engine optimized

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation** - /docs (links in footer)
- **GitHub Issues** - Bug reports and feature requests
- **Email** - support@modelforge.dev

---

**ModelForge** - Empowering creators with AI-driven 3D model generation 🚀
