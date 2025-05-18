---
layout: home
title: Hacker News Digest - Syazaril Asyraf
---
{% assign latest_post = site.posts | first %}
<h1>{{ latest_post.title }}</h1>
<p><em>{{ latest_post.date | date: "%B %d, %Y" }}</em></p>

{{ latest_post.content }}

<p><a href="/archive/">See all archives</a></p>

_Disclaimer: The “Save to Linkding” button adds bookmarks to my Linkding account. To save to your own Linkding, just copy the story URL and title, then add them manually in your Linkding app or web interface._
