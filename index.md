---
layout: default
title: Лента
---

<!-- Подключаем Alpine.js -->
<script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>

<div x-data="feed" x-init="init()" class="max-w-3xl mx-auto px-5 py-12">
  <!-- Шапка и поиск -->
  <div class="mb-8">
    <h1 class="text-4xl font-black text-white tracking-tight mb-2">Дайджест open-source</h1>
    <input type="search" x-model="search" placeholder="Поиск по заголовкам..."
           class="w-full p-3 mt-4 bg-slate-800 border border-slate-700 rounded-lg text-white">
  </div>

  <!-- Скелетон загрузки -->
  <div x-show="loading" class="text-center py-16 text-slate-500">
    <p class="mono text-xs uppercase tracking-widest">loading feed...</p>
  </div>

  <!-- Список постов -->
  <div x-show="!loading" class="space-y-3">
    <template x-for="post in paginatedPosts" :key="post.url">
      <article class="border border-slate-800/80 rounded-xl p-6" style="background: linear-gradient(180deg, rgba(15,17,25,0.9), rgba(10,11,16,0.9));">
        <div class="flex items-center gap-2 mb-3">
          <span class="mono text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                x-text="post.categories[0] || 'general'"></span>
          <span class="mono text-[10px] text-slate-600" x-text="post.date"></span>
        </div>
        <h2 class="text-xl font-bold text-white mb-3">
          <a :href="post.url" class="hover:text-indigo-400 transition-colors" x-text="post.title"></a>
        </h2>
        <p class="text-sm text-slate-400" x-text="post.excerpt"></p>
        <a :href="post.url" class="inline-flex items-center gap-1 mt-4 mono text-[11px] uppercase tracking-widest font-semibold text-indigo-400 hover:text-indigo-300">
          Читать ↗
        </a>
      </article>
    </template>
    <div x-show="filteredPosts.length === 0" class="text-center py-16 border border-dashed border-slate-800 rounded-xl">
      <p class="mono text-xs text-slate-600 uppercase tracking-widest">no posts found</p>
    </div>
  </div>

  <!-- Пагинация -->
  <div x-show="totalPages > 1" class="flex justify-between items-center mt-8 pt-4 border-t border-slate-800">
    <button @click="prevPage()" :disabled="currentPage === 1" class="px-4 py-2 text-sm font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed">← Назад</button>
    <span class="mono text-xs text-slate-500" x-text="`стр. ${currentPage} из ${totalPages}`"></span>
    <button @click="nextPage()" :disabled="currentPage === totalPages" class="px-4 py-2 text-sm font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed">Вперед →</button>
  </div>
</div>

<script>
  document.addEventListener('alpine:init', () => {
    Alpine.data('feed', () => ({
      posts: [],
      loading: true,
      search: '',
      currentPage: 1,
      itemsPerPage: 10,

      async init() {
        try {
          const response = await fetch('{{ "/posts.json" | relative_url }}');
          this.posts = await response.json();
        } catch (e) {
          console.error('Failed to load posts:', e);
        } finally {
          this.loading = false;
        }
      },

      get filteredPosts() {
        if (!this.search) return this.posts;
        const query = this.search.toLowerCase();
        return this.posts.filter(post =>
          post.title.toLowerCase().includes(query) ||
          post.excerpt.toLowerCase().includes(query)
        );
      },

      get totalPages() {
        return Math.ceil(this.filteredPosts.length / this.itemsPerPage);
      },

      get paginatedPosts() {
        const start = (this.currentPage - 1) * this.itemsPerPage;
        return this.filteredPosts.slice(start, start + this.itemsPerPage);
      },

      prevPage() {
        if (this.currentPage > 1) this.currentPage--;
      },

      nextPage() {
        if (this.currentPage < this.totalPages) this.currentPage++;
      }
    }));
  });
</script>