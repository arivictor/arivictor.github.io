---
layout: default
title: Posts
permalink: /posts/
---

<h2>All Posts</h2>
<ul class="list">
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <small>{{ post.date | date: "%-d %b %Y" }}</small>
    </li>
  {% endfor %}
</ul>