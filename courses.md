---
layout: default
title: Courses
permalink: /courses/
---
<h2>Courses</h2>
{% assign grouped = site.courses | group_by: "course" %}
{% for g in grouped %}
  {% assign parts = g.items | sort: "part" %}
  <h3>{{ g.name | capitalize }}</h3>
  <ol>
    {% for p in parts %}
      <li><a href="{{ p.url }}">Part {{ p.part }}: {{ p.title }}</a></li>
    {% endfor %}
  </ol>
{% endfor %}