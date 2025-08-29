---
layout: default
permalink: /tags/
title: Tags
---

<div class="space-y-16">
  <header class="text-center py-16">
    <h1 class="font-sans text-brand mb-6 leading-tight" style="font-size: 2.25rem;">
      Tags
    </h1>
    <p class="text-gray-600 text-lg max-w-2xl mx-auto leading-relaxed">
      Explore all content organized by topic
    </p>
  </header>

  <section class="max-w-4xl mx-auto">
    {% assign sorted_tags = site.tags | sort %}
    {% if sorted_tags.size > 0 %}
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {% for tag in sorted_tags %}
          {% assign tag_name = tag[0] %}
          {% assign tag_posts = tag[1] %}
          <div class="minimal-tag-card">
            <h2 class="tag-card-title">
              <a href="{{ '/tags/' | append: tag_name | append: '/' | relative_url }}" 
                 class="font-sans text-brand transition-colors">
                {{ tag_name }}
              </a>
            </h2>
            <p class="tag-card-count">
              {{ tag_posts.size }} 
              {% if tag_posts.size == 1 %}post{% else %}posts{% endif %}
            </p>
            
            {% if tag_posts.size > 0 %}
            <div class="tag-card-posts">
              {% for post in tag_posts limit:3 %}
              <div class="tag-card-post">
                <a href="{{ post.url | relative_url }}" class="transition-colors">
                  {{ post.title }}
                </a>
                <span class="tag-card-date">
                  {{ post.date | date: "%b %Y" }}
                </span>
              </div>
              {% endfor %}
              
              {% if tag_posts.size > 3 %}
              <div class="tag-card-more">
                <a href="{{ '/tags/' | append: tag_name | append: '/' | relative_url }}" 
                   class="text-brand transition-colors">
                  + {{ tag_posts.size | minus: 3 }} more
                </a>
              </div>
              {% endif %}
            </div>
            {% endif %}
          </div>
        {% endfor %}
      </div>
    {% else %}
      <p class="text-center text-gray-600">No tags found.</p>
    {% endif %}
  </section>
</div>