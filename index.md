---
layout: default
---

<style>
  .soft-card {
    border-radius: 1rem;
    background: white;
    padding: 2rem;
    box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }
  .soft-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0,0,0,0.12);
  }
  .soft-title {
    font-weight: 800;
    font-size: 1.5rem;
    color: #111;
    margin-bottom: 0.5rem;
  }
  .soft-meta {
    font-size: 0.875rem;
    color: #666;
    margin-bottom: 1rem;
  }
  .soft-desc {
    font-size: 1rem;
    color: #333;
    margin-bottom: 1.5rem;
  }
  .soft-tag {
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    background: #d3f9d8;
    color: #065f46;
    margin-right: 0.5rem;
  }
  .soft-tag:hover {
    background: #b2f2bb;
  }
  .soft-heading {
    font-weight: 900;
    font-size: 2.5rem;
    margin-bottom: 2rem;
    color: #222;
    background: linear-gradient(to right, #fde68a, #fbcfe8, #bfdbfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
</style>

<div class="max-w-6xl mx-auto px-6 py-20">
  <h2 class="soft-heading">Posts</h2>

  <ul class="grid md:grid-cols-2 gap-10">
    {% for post in site.posts %}
    <li class="soft-card">
      <a href="{{ post.url | relative_url }}" class="soft-title">
        {{ post.title }}
      </a>

      <p class="soft-meta">
        {{ post.date | date: "%B %d, %Y" }}
      </p>

      {% if post.description %}
      <p class="soft-desc">
        {{ post.description }}
      </p>
      {% endif %}

      {% if post.tags %}
      <div>
        {% for tag in post.tags %}
        <a href="{{ '/tags/' | append: tag | relative_url }}" class="soft-tag">
          {{ tag }}
        </a>
        {% endfor %}
      </div>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
</div>