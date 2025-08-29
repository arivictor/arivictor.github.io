---
layout: default
---


<div class="space-y-16">
  <header class="text-center py-16">
    <!-- <h1 class="font-serif text-brand mb-6 leading-tight" style="font-size: 3rem;">
      Recent Posts
    </h1> -->
    <p class="text-gray-600 text-lg max-w-2xl mx-auto leading-relaxed">
      This is where I sit with code, until it makes sense.
    </p>
  </header>

  <section class="neo-post-list">
    {% for post in site.posts %}
    <article class="post-item">
      <h2 class="post-title">
        <a href="{{ post.url | relative_url }}" class="font-serif text-brand transition-colors">
          {{ post.title }}
        </a>
      </h2>
      
      <p class="post-date">
        {{ post.date | date: "%B %d, %Y" }}
      </p>

      {% if post.description %}
      <p class="post-description">
        {{ post.description }}
      </p>
      {% endif %}

      {% if post.tags %}
      <div class="post-tags">
        {% for tag in post.tags %}
        <a href="{{ '/tags/' | append: tag | relative_url }}">{{ tag }}</a>
        {% endfor %}
      </div>
      {% endif %}
    </article>
    {% endfor %}
  </section>
</div>