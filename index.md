---
layout: default
---

<div class="max-w-5xl mx-auto px-6 py-16">
  <h2 class="text-5xl font-extrabold uppercase mb-12 border-b-8 border-black pb-4 bg-yellow-300 inline-block px-4">
    Posts
  </h2>

  <ul class="grid md:grid-cols-2 gap-8">
    {% for post in site.posts %}
    <li class="border-4 border-black bg-pink-200 p-6 hover:bg-pink-300 transition-colors">

      <!-- Title -->
      <a href="{{ post.url | relative_url }}" 
         class="block text-2xl font-extrabold text-black underline decoration-4 hover:no-underline mb-3">
        {{ post.title }}
      </a>

      <!-- Meta -->
      <p class="text-sm font-mono mb-4">
        {{ post.date | date: "%B %d, %Y" }}
      </p>

      <!-- Description -->
      {% if post.description %}
      <p class="text-base font-mono mb-6">
        {{ post.description }}
      </p>
      {% endif %}

      <!-- Tags -->
      {% if post.tags %}
      <div class="flex flex-wrap gap-2">
        {% for tag in post.tags %}
        <a href="{{ '/tags/' | append: tag | relative_url }}"
           class="px-3 py-1 border-2 border-black text-xs uppercase font-bold 
                  bg-green-200 hover:bg-green-300 transition-colors">
          {{ tag }}
        </a>
        {% endfor %}
      </div>
      {% endif %}
    </li>
    {% endfor %}
  </ul>
</div>

