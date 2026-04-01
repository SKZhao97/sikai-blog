---
name: blog-writer
description: |
  Create a new blog post for Hugo static blog with Stack theme. This skill creates a new post directory with proper frontmatter, copies the default cover image, and generates initial content based on user's summary. Use this skill whenever the user wants to write a new blog post, create a new article, add content to their blog, or start a new post in a Hugo-based blog. The skill follows the existing pattern in the blog's content/post directory with MMDD-title-slug folder naming and proper TOML frontmatter.
---

# Blog Writer Skill

This skill helps you create new blog posts for a Hugo static blog using the Stack theme. It creates a properly formatted post directory with all necessary files and frontmatter.

## How It Works

1. **Input Requirements**: You need to gather the following information from the user:
   - Post title (used to generate folder name)
   - Brief description/summary (for the description field and initial content)
   - Categories (array of categories, e.g., `["AI", "Thoughts"]`)
   - Tags (array of tags, e.g., `["AI", "Claude Code", "Efficiency"]`)

2. **Folder Creation**: Creates a folder in `content/post/` with naming pattern `MMDD-title-slug/` where:
   - `MMDD` is the current month and day (e.g., "0401" for April 1)
   - `title-slug` is the title converted to lowercase with spaces replaced by hyphens

3. **Cover Image**: Copies the default cover image from `static/cover.png` to the post directory and references it in the frontmatter.

4. **Frontmatter**: Generates proper TOML frontmatter (`+++`) with:
   - `date`: Current date and time in ISO 8601 with timezone (e.g., `'2026-04-01T16:15:00+08:00'`)
   - `draft`: Set to `true` (creates as draft)
   - `title`: The provided title
   - `description`: The provided description/summary
   - `categories`: User-provided categories array
   - `tags`: User-provided tags array
   - `image`: `'cover.png'` (references the copied image)

5. **Initial Content**: Generates initial markdown content based on the user's summary, starting with the summary text and adding section headers for further development.

## Step-by-Step Instructions

### 1. Gather Information

Ask the user for:
- **Title**: The main title of the blog post
- **Description/Summary**: A brief summary of what the post will cover
- **Categories**: Array of categories (e.g., `["Technology", "AI"]`)
- **Tags**: Array of tags (e.g., `["Claude", "Programming", "Tools"]`)

If the user doesn't provide categories or tags, suggest using `["Uncategorized"]` for categories and an empty array for tags.

### 2. Generate Folder Name

1. Get current date in format `MMDD` (month and day, zero-padded)
2. Convert title to slug:
   - Convert to lowercase
   - Replace spaces with hyphens
   - Remove special characters
3. Combine: `MMDD-title-slug`

Example: "My New Post" on April 1 → "0401-my-new-post"

### 3. Create Directory

Create directory at `content/post/MMDD-title-slug/`

### 4. Copy Cover Image

Copy `static/cover.png` to `content/post/MMDD-title-slug/cover.png`

### 5. Create index.md with Frontmatter

Create `content/post/MMDD-title-slug/index.md` with TOML frontmatter:

```toml
+++
date = 'YYYY-MM-DDTHH:MM:SS+08:00'
draft = true
title = 'Post Title'
description = 'Post description summary'

categories = ["Category1", "Category2"]
tags = ["tag1", "tag2", "tag3"]

image = 'cover.png'
+++
```

**Important**: Use single quotes around string values in TOML.

### 6. Add Initial Content

After the frontmatter, add:

```
[Description summary provided by user]

## Introduction

[Start writing the introduction here...]

## Main Content

[Add your main content sections here...]

## Conclusion

[Wrap up your post here...]
```

### 7. Verify and Confirm

1. Check that all files are created correctly
2. Show the user the created file structure
3. Provide instructions for next steps (editing, previewing with `hugo server -D`)

## Example

**User Input**:
- Title: "AI Coding Project Experience"
- Description: "My experience using AI coding tools for a complete software project"
- Categories: `["AI Coding", "Thoughts", "Engineering"]`
- Tags: `["AI", "Agent", "Claude Code", "Efficiency"]`

**Output**:
- Folder: `content/post/0401-ai-coding-project-experience/`
- Files:
  - `cover.png` (copied from `static/cover.png`)
  - `index.md` with proper frontmatter and initial content

## Notes

- The blog uses Hugo with Stack theme
- Posts are organized in `content/post/` with `MMDD-title-slug/` folders
- Frontmatter uses TOML format with `+++` delimiters
- Default cover image is at `static/cover.png`
- Created posts are drafts by default (set `draft = false` to publish)
- Use `hugo server -D` to preview drafts locally