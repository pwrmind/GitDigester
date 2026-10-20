---
layout: default
title: Лента
---

<div class="mb-8 flex items-center justify-between">
  <h2 class="text-2xl font-bold text-white tracking-tight">Последние обновления</h2>
  <span class="text-xs text-slate-500">{{ site.posts | size }} постов</span>
</div>

<div class="space-y-4">
{% for post in site.posts %}
  <article class="group bg-slate-900/40 border border-slate-800/60 rounded-xl p-5 hover:border-slate-700 transition">
    <div class="flex items-center justify-between gap-3 mb-2">
      <span class="px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-md bg-blue-950 text-blue-400 border border-blue-900/50">
        {{ post.categories | first | default: "general" }}
      </span>
      <time class="text-xs text-slate-500">{{ post.date | date: "%d.%m.%Y" }}</time>
    </div>
    <h3 class="text-lg font-bold text-white mb-2 group-hover:text-blue-400 transition">
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </h3>
    <p class="text-sm text-slate-400 leading-relaxed">
      {{ post.excerpt | strip_html | truncate: 200 }}
    </p>
    <a href="{{ post.url | relative_url }}"
       class="inline-block mt-3 text-xs font-semibold text-blue-400 hover:text-blue-300 transition">
      Читать далее →
    </a>
  </article>
{% else %}
  <div class="text-center py-16 border border-dashed border-slate-800 rounded-xl text-slate-500">
    😴 Пока нет постов. Запустите генератор.
  </div>
{% endfor %}
</div>