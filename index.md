---
layout: home
title: Hacker News Digest - Syazaril Asyraf
---
{% assign latest_post = site.posts | first %}
<h1>{{ latest_post.title }}</h1>
<p><em>{{ latest_post.date | date: "%B %d, %Y" }}</em></p>

{{ latest_post.content }}

<p><a href="/archive/">See all archives</a></p>
