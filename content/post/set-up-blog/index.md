+++
date = '2026-03-20T00:58:39+08:00'
draft = false
title = 'Set up the Blog'
description = "Web construting based on Hugo, Netlify and Cloudflare"

image = 'cover.jpg'
+++

Today, I would like to share the process of setting up this blog. The three main tools are Hugo, Netlify and Cloudflare.


## Framework

[Hugo](https://gohugo.io/) is one of the most popular open-source static site generators. It is an [open-source project](https://github.com/gohugoio/hugo) written in Golang. Fast, flexible and free to use are the most important reasons that I chose it. The theme I am using is called [*Stack*](https://github.com/CaiJimmy/hugo-theme-stack), and there are also plenty of other themes to select.

Building a basic blog based on Hugo is pretty easy; the only reference you need is the [quick-start tutorial](https://gohugo.io/getting-started/quick-start/). Using several CLI commands and editing the *hugo.toml*  file, the blog website can start function. And by adding content to the project, a new blog can be generated. There are many advanced features provided by Hugo or the *Stack* theme waiting for me to discover. I hope I can dive deeper later and maitain my blog well and make it more interesting.

## Deployment
When it comes to deploying a static site, we are lucky to have several world-class platforms. However, for a Hugo-based site (like the one I'm building with the Stack theme), [Netlify](https://docs.netlify.com/) stands out as the most balanced choice. There are several reasons:

1. Zero-Config Deployment. The workflow is seamless: I just git push my code to GitHub, and Netlify automatically detects the Hugo framework, builds the site, and deploys it within seconds. No manual uploading is required.
2. Powerful Built-in Functionalities. Netlify provides easy access to SSL certificates, DNS, Monitoring & Insights, etc. Although some of the functions are not required currently, but it is also good to choose a comprehensive platform.

As I said above, Netlify is very convenient to use. There is a [Hugo tutorial](https://gohugo.io/host-and-deploy/host-on-netlify/) about deploying on Netlify. Once you completed the steps, a brand new website would be ready. But the domain is something weird like "illustrious-crisp-79ae99/overview", so I did the last step to set up my own domain.
 

## Domain
ALthough domain can be purchased and maintained on Netlify, I chose to use [Cloudflare](https://dash.cloudflare.com/) for three reasons：

1. True At-Cost Pricing. The price offered by Cloudflare is lower. Although other platforms has first-year discount i, I didn't consider that because I wish to use the domain in my whole life :).
2. World-Class DNS Performance & Security. Cloudflare runs one of the fastest and largest authoritative DNS networks in the world. Cloudflare provides WHOIS Privacy Protection for free, ensuring your personal contact information isn't harvested by spammers.
3. "Separation of Concerns". In system architecture, it is always a best practice to keep your Assets (Domain) separate from your Services (Hosting).

After purchasing the domain, don't forget to set it as the custom link for the Netlify project. And also, DNS records need to be added under *DNS - Records* section on Cloudflare. The type should be "CNAME", and the content is the original link of Netlify website.




Throughout the process of constructing the blog, I met some problems including .toml file config error, Hugo theme imcompatibiltiy, etc.. I threw the questions to [Gemini](https://gemini.google.com/), and high-quality answers showed up right away. All the time I spent constructing the web so for is just 1 hour. Not only solving the problems, Gemini also recommend some features or styles for me to try in the future. I have to say, the powerful AI tools should be our best friends. And I hope to post some blogs about AI, too.

Stay tuned.