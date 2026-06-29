<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api, type Page, type PageDetail } from "./api";
import Sidebar from "./components/Sidebar.vue";
import PageView from "./components/PageView.vue";

const pages = ref<Page[]>([]);
const current = ref<PageDetail | null>(null);

async function loadPages() {
  pages.value = await api.listPages();
}

async function selectPage(id: number) {
  current.value = await api.getPage(id);
}

async function newPage() {
  const page = await api.createPage("Untitled");
  await loadPages();
  await selectPage(page.id);
}

async function removePage(id: number) {
  await api.deletePage(id);
  await loadPages();
  if (current.value?.id === id) {
    const next = pages.value[0];
    current.value = next ? await api.getPage(next.id) : null;
  }
}

function onRename(id: number, title: string) {
  const p = pages.value.find((x) => x.id === id);
  if (p) p.title = title;
}

onMounted(async () => {
  await loadPages();
  if (pages.value.length) await selectPage(pages.value[0].id);
});
</script>

<template>
  <div class="app">
    <Sidebar
      :pages="pages"
      :current-id="current?.id ?? null"
      @select="selectPage"
      @create="newPage"
      @remove="removePage"
    />
    <PageView v-if="current" :key="current.id" :page="current" @rename="onRename" />
    <main v-else class="main">
      <p class="empty">No page selected. Create one with “+”.</p>
    </main>
  </div>
</template>
