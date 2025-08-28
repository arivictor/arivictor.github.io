---
layout: default
title: Courses
permalink: /courses/
---

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