---
layout: default
title: Лента
---

<div class="mb-10">
  <h1 class="text-4xl font-black text-white tracking-tight mb-2">Дайджест <span class="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">open-source</span></h1>
  <p class="text-sm text-slate-500">Автоматические сводки активности репозиториев, сгенерированные локальной LLM</p>
</div>

<div class="space-y-3">
{% for post in site.posts %}
  <article class="group relative border border-slate-800/80 rounded-xl p-6 hover:border-indigo-500/40 transition-all duration-300" style="background: linear-gradient(180deg, rgba(15,17,25,0.9), rgba(10,11,16,0.9));">
    <div class="flex items-center gap-2 mb-3">
      <span class="mono text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
        {{ post.categories | first | default: "general" }}
      </span>
      <span class="mono text-[10px] text-slate-600">{{ post.date | date: "%Y.%m.%d" }}</span>
    </div>

    <h2 class="text-xl font-bold text-white mb-3 tracking-tight group-hover:text-indigo-400 transition-colors">
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </h2>

    <div class="post-content text-sm opacity-90">
      {{ post.content | strip_html | truncate: 260 }}
    </div>

    <a href="{{ post.url | relative_url }}"
       class="inline-flex items-center gap-1 mt-4 mono text-[11px] uppercase tracking-widest font-semibold text-indigo-400 hover:text-indigo-300 transition">
      Читать ↗
    </a>
  </article>
{% else %}
  <div class="text-center py-16 border border-dashed border-slate-800 rounded-xl">
    <p class="mono text-xs text-slate-600 uppercase tracking-widest">no posts yet</p>
  </div>
{% endfor %}
</div>