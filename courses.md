---
layout: page
title: Courses
permalink: /courses/
---

# Domain Driven Design Workshop

A complete, hands-on 5-part workshop that teaches you to discover domains with event storming, carve out bounded contexts, and implement a complete DDD application in Python.

## Workshop Overview

**Outcome:** You'll learn to discover a domain with event storming, carve out bounded contexts, and implement a thin vertical slice with Entities, Value Objects, Aggregates, Repositories, Commands, Events, Policies, Queries, and Use Cases. You'll also master a repeatable 4-step command handling pattern.

**Domain for practice:** A minimal social app where users register accounts, follow each other, and block users. We'll fix the classic bug where blocked users can still see posts due to remaining follow links.

**Format:** Five 90-minute blocks. Each starts with 15 minutes of concepts, then 75 minutes of hands-on practice.

---

## Course Sections
<!-- 
<div class="course-list">
{% assign sorted_courses = site.courses | sort: 'order' %}
{% for course in sorted_courses %}
  <div class="course-item">
    <h3><a href="{{ course.url }}">{{ course.title }}</a></h3>
    <p class="course-meta">{{ course.part }} • {{ course.duration }}</p>
    <p>{{ course.content | strip_html | truncatewords: 30 }}</p>
    <a href="{{ course.url }}" class="course-link">Start this section →</a>
  </div>
{% endfor %}
</div> -->

---

## What You'll Build

By the end of this workshop, you'll have built a complete social application that demonstrates:

- **Event Storming** for domain discovery
- **Clean Architecture** with separated concerns  
- **Domain-Driven Design patterns** in practical Python code
- **Test-driven development** with scenario testing
- **Policy-driven business rules** that automatically fix bugs

## Workshop Approach

Each section follows a proven pattern:
1. **Concept introduction** (15 minutes)
2. **Hands-on implementation** (75 minutes)  
3. **Three-step improvement cycle**: immediate patch, deeper cause, optional enhancement

## Complete Working Code

The workshop includes a complete, runnable Python application that you can copy, paste, and run immediately. All concepts are tied to working code so you can see DDD patterns in action.

📥 **[Download the complete Python code →](/assets/ddd_workshop.py)**

---

**Ready to start?** Begin with [Part 1: Event Storming and Contexts](/courses/01-event-storming-contexts/)

<style>
.course-list {
  margin: 2rem 0;
}

.course-item {
  margin: 2rem 0;
  padding: 1.5rem;
  border: 1px solid #e1e1e1;
  border-radius: 4px;
  background-color: #fafafa;
}

.course-item h3 {
  margin-top: 0;
}

.course-item h3 a {
  text-decoration: none;
  color: #333;
}

.course-item h3 a:hover {
  color: #0066cc;
}

.course-meta {
  color: #666;
  font-size: 0.9em;
  margin: 0.5rem 0;
}

.course-link {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #0066cc;
  color: white;
  text-decoration: none;
  border-radius: 3px;
  font-size: 0.9em;
}

.course-link:hover {
  background-color: #0052a3;
  color: white;
}
</style>