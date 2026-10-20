---
layout: default
title: Лента
---

## Последние обновления

{% for post in site.posts %}
<article class="post">
  <h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2>
  <p class="post-meta">{{ post.date | date: "%d.%m.%Y" }} · {{ post.categories | join: ", " }}</p>
  <div>{{ post.excerpt | strip_html | truncate: 240 }}</div>
</article>
{% else %}
<p>Пока нет постов.</p>
{% endfor %}