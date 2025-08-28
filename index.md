---
layout: default
title: Home
---

<section>
<h1>👋🏻 Hey, I'm Ari</h1>
<p>I write about code. Mostly python. 🐍</p>
</section>

<h2>Posts</h2>
<ul class="list">
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <small>{{ post.date | date: "%-d %b %Y" }}</small>
    </li>
  {% endfor %}
</ul>