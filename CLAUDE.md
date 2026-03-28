# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Hugo static blog using the [Stack theme](https://github.com/CaiJimmy/hugo-theme-stack). The site is deployed to Netlify.

## Setup

1. Clone the repository with submodules:
   ```bash
   git clone --recursive <repo-url>
   ```
   If already cloned, initialize submodules:
   ```bash
   git submodule init && git submodule update
   ```

2. Install Hugo (version 0.158.0 or later). The Netlify build environment uses Hugo 0.158.0.

## Common Commands

### Development Server
Start a local Hugo server with live reload:
```bash
hugo server
```

### Build Site
Build the site for production (outputs to `public/`):
```bash
hugo build --gc --minify
```

### Create New Post
Create a new blog post with the default archetype:
```bash
hugo new post/MMDD-post-title/index.md
```
The post will be created in `content/post/MMDD-post-title/` with draft frontmatter.

### Preview Drafts
Include draft posts in the local server:
```bash
hugo server -D
```

## Adding a New Post

1. Use `hugo new post/MMDD-post-title/index.md` (replace MMDD with month/day and a descriptive slug).
2. Edit the generated markdown file in `content/post/MMDD-post-title/index.md`.
3. Update frontmatter: set `draft = false`, add `description`, `categories`, `tags`, and `image` (optional).
4. Place any post-specific images in the same folder and reference them via relative paths.
5. Write content in Markdown below the frontmatter.
6. Preview with `hugo server -D`.

## Content Structure

- **Posts**: Located in `content/post/` with folder naming `MMDD-post-title/` (e.g., `0327-vibe-coding-vs-spec-coding`). Each post's `index.md` contains TOML frontmatter (`+++`) with fields: `date` (ISO 8601 with timezone), `draft`, `title`, `description`, `categories`, `tags`, `image`.
- **Images**: Post-specific images should be placed in the same folder as the post's `index.md`. The avatar image is at `assets/img/avatar.png`.
- **Custom Layouts**: Only the footer is customized (`layouts/partials/footer/footer.html`). The theme's default layouts are used elsewhere.
- **Configuration**: Site-wide settings are in `hugo.toml` (menu, sidebar, footer motto, etc.).

## Search Functionality

The blog has a client-side search feature powered by the Stack theme.

**How it works**:
1. The search page (`/search/`) generates a JSON index (`/search/index.json`) containing all post titles, content, dates, and permalinks.
2. When a user types in the search box, JavaScript fetches the JSON and performs fuzzy matching on the client side.
3. Results are displayed instantly with highlighted matches.

**Configuration**:
- Search page: `content/page/search/index.md` with `layout: "search"` and `outputs: [html, json]` (no menu configuration in page frontmatter)
- Menu: Enabled in `hugo.toml` (weight: 50) - this is the only menu entry for search
- Output formats: Configured for JSON generation in `hugo.toml`
- Widgets: Homepage widgets can be configured via `[params.widgets]` (currently empty)

**To modify search behavior**:
- Edit `themes/stack/assets/ts/search.tsx` for client-side search logic
- Edit `themes/stack/layouts/page/search.json` for JSON data structure
- The search uses client-side JavaScript; no server-side processing is required.

## Deployment

The site is deployed via Netlify. The `netlify.toml` file specifies the build command and environment variables. The build command runs `hugo build --gc --minify --baseURL "${URL}"`.

## Theme

The theme is a Git submodule at `themes/stack`. Customizations should be minimal; prefer overriding via `layouts/` when needed. Do not modify files inside the theme submodule directly.

## Notes

- There are no tests or linting scripts.
- Commit messages follow conventional commits (e.g., `feat:`, `fix:`).
- The blog is bilingual (Chinese and English) but currently only uses English.
- The `static/` folder contains the favicon.
- The `assets/` folder contains the avatar and a `jsconfig.json` for IDE support.
- Search functionality is enabled (`/search/`) with client-side fuzzy matching.