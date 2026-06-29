<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import type { Page } from "../api";

defineProps<{
  pages: Page[];
  currentId: number | null;
}>();

const emit = defineEmits<{
  select: [id: number];
  create: [];
  remove: [id: number];
}>();

// ── shortcuts cheat-sheet toggle ──────────────────────
// `?` pressed anywhere outside a textarea/input toggles the footer.
// `?` typed inside a block is just text and must not toggle anything.
const shortcutsVisible = ref(true);

function onGlobalKeydown(e: KeyboardEvent) {
  if (e.key !== "?") return;
  const t = e.target as Element | null;
  if (t && (t instanceof HTMLTextAreaElement || t instanceof HTMLInputElement)) {
    return;
  }
  e.preventDefault();
  shortcutsVisible.value = !shortcutsVisible.value;
}

onMounted(() => window.addEventListener("keydown", onGlobalKeydown));
onBeforeUnmount(() => window.removeEventListener("keydown", onGlobalKeydown));
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__brand">📝 Flotion</div>
    <div class="sidebar__head">
      <span>Pages</span>
      <button class="sidebar__new" title="New page" @click="emit('create')">+</button>
    </div>
    <div class="sidebar__pages">
      <div
        v-for="page in pages"
        :key="page.id"
        class="page-row"
        :class="{ 'page-row--active': page.id === currentId }"
        @click="emit('select', page.id)"
      >
        <span class="page-row__title">{{ page.title || "Untitled" }}</span>
        <button
          class="page-row__del"
          title="Delete page"
          @click.stop="emit('remove', page.id)"
        >
          ✕
        </button>
      </div>
    </div>
    <ul v-show="shortcutsVisible" class="sidebar__shortcuts">
      <li><kbd>#</kbd> Heading</li>
      <li><kbd>-</kbd> Bullet</li>
      <li><kbd>&gt;</kbd> Quote</li>
      <li><kbd>Enter</kbd> New block</li>
      <li><kbd>Backspace</kbd> Delete empty / revert</li>
    </ul>
  </aside>
</template>