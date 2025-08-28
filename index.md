---
layout: default
title: Home
---

<section>
<h1>👋🏻 Hey, I'm Ari</h1>
<p>I write about code.</p>
</section>

<h2>Posts</h2>
<ul class="list">
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
      <small>{{ post.date | date: "%-d %b %Y" }}</small>
      {% if post.tags %} - 
        {% for tag in post.tags %}
          <a href="/tags/{{ tag | slugify }}/">#{{ tag }}</a>{% unless forloop.last %}, {% endunless %}
        {% endfor %}
      {% endif %}
    </li>
  {% endfor %}
</ul>

<h2>Courses</h2>
{% assign grouped = site.courses | group_by: "course" %}
{% for g in grouped %}
  <h3>{{ g.name | capitalize }}</h3>
  <ol>
    {% assign parts = g.items | sort: "part" %}
    {% for p in parts %}
      <li><a href="{{ p.url | relative_url }}">Part {{ p.part }}: {{ p.title }}</a></li>
    {% endfor %}
  </ol>
{% endfor %}