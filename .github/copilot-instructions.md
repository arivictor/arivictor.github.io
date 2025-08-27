# GitHub Copilot Instructions

## Project Overview

This is the personal website and blog of Ari Victor (arivictor.github.io), built with Jekyll and hosted on GitHub Pages. The site focuses on software engineering, workflows, system design, and technical writing with an emphasis on precision and minimalism.

## Core Principles

- **Precision in engineering**: Code should do exactly what it says, nothing more, nothing less
- **Minimalism**: Prefer simple, clean solutions over complex ones
- **No excess, no hype**: Focus on functionality and clarity
- **Clean typography and design**: Maintain the established visual consistency

## Technology Stack

- **Static Site Generator**: Jekyll 4.x
- **Hosting**: GitHub Pages
- **Styling**: SCSS/CSS with custom theme
- **Content**: Markdown for posts and pages
- **Fonts**: Cabin (primary), Source Code Pro (monospace)
- **Build**: Ruby Bundler with GitHub Pages gem

## File Structure and Conventions

### Directory Structure
```
├── _config.yml              # Jekyll configuration
├── _includes/               # Reusable HTML components
├── _layouts/                # Page templates
├── _sass/                   # SCSS stylesheets
├── collections/
│   ├── _posts/             # Blog posts (YYYY-MM-DD-title.md)
│   └── _drafts/            # Draft posts
├── css/                    # Compiled CSS
├── js/                     # JavaScript files
├── images/                 # Static images
└── pages/                  # Static pages
```

### Naming Conventions
- Blog posts: `YYYY-MM-DD-title-with-hyphens.md`
- Files: lowercase with hyphens (kebab-case)
- SCSS variables: `$variable-name` format
- CSS classes: BEM methodology preferred

## Content Guidelines

### Blog Posts
- Use clear, descriptive titles
- Include proper front matter:
  ```yaml
  ---
  layout: post
  title: "Post Title"
  date: YYYY-MM-DD
  categories: [category1, category2]
  ---
  ```
- Write in a professional, technical tone
- Focus on practical insights and learnings
- Keep posts focused and actionable

### Code Examples
- Use proper syntax highlighting with triple backticks
- Include language identifiers: ```python, ```javascript, etc.
- Prefer concise, working examples
- Add comments only when necessary for clarity

## Styling Guidelines

### SCSS/CSS
- Follow existing variable naming in `_sass/_variables.scss`
- Use the established color palette (blacks, grays, minimal accent colors)
- Maintain responsive design principles
- Keep specificity low, prefer classes over IDs
- Follow the established typography scale

### HTML/Liquid
- Use semantic HTML5 elements
- Follow Jekyll/Liquid templating conventions
- Keep templates clean and readable
- Minimize inline styles, prefer CSS classes

## Development Workflow

### Local Development
```bash
bundle install          # Install dependencies
bundle exec jekyll serve # Run local development server
```

### Content Creation
1. For blog posts: Create in `collections/_posts/`
2. For drafts: Create in `collections/_drafts/`
3. For pages: Create in root or appropriate subdirectory
4. Test locally before committing

### Code Quality
- Validate HTML output
- Check responsive design on multiple screen sizes
- Ensure fast loading times
- Verify proper semantic structure

## Jekyll-Specific Guidelines

### Front Matter
- Always include required front matter
- Use consistent date format: `YYYY-MM-DD`
- Keep categories and tags relevant and consistent
- Use `layout: post` for blog posts, `layout: page` for static pages

### Liquid Templating
- Use `{% raw %}{% %}{% endraw %}` for logic, `{% raw %}{{ }}{% endraw %}` for output
- Prefer `site.baseurl` for internal links
- Use `{% raw %}{% include %}{% endraw %}` for reusable components
- Handle edge cases (empty collections, missing data)

### Plugins and Extensions
- Stick to GitHub Pages-compatible plugins
- Current plugins: jekyll-paginate, jekyll-sitemap
- Avoid adding unnecessary complexity

## Performance Considerations

- Optimize images before adding them
- Minimize CSS and JavaScript
- Use efficient Liquid loops and conditionals
- Leverage browser caching for static assets
- Keep page weight minimal

## Content Focus Areas

When creating content or features, prioritize:
- **Technical tutorials** on workflows and system design
- **Programming insights** especially Python, workflow engines
- **Engineering practices** and methodologies
- **Tool reviews** and comparisons
- **Personal projects** and case studies

## Code Comments and Documentation

- Code should be self-documenting through clear naming
- Add comments only when the "why" isn't obvious
- Keep README and documentation current
- Document any custom Jekyll plugins or modifications

## Accessibility

- Use proper heading hierarchy (h1, h2, h3...)
- Include alt text for images
- Ensure sufficient color contrast
- Test with screen readers when possible
- Make content keyboard navigable

## SEO and Metadata

- Include descriptive page titles
- Use meta descriptions for important pages
- Implement proper Open Graph tags
- Maintain consistent URL structure
- Include relevant keywords naturally

When suggesting code or content changes, always consider these guidelines and maintain consistency with the existing codebase and content style.