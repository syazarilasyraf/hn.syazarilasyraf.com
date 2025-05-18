---
layout: archive
title: "Hacker News Digest Archive"
permalink: /archive/
---

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a> — {{ post.date | date: "%B %d, %Y" }}
      {% if post.tags %}
        <small>Tags: {{ post.tags | join: ", " }}</small>
      {% endif %}
    </li>
  {% endfor %}
</ul>