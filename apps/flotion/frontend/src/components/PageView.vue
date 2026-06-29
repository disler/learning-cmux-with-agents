<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { api, type Block, type PageDetail } from "../api";
import BlockItem from "./BlockItem.vue";

function wordCountOf(s: string): number {
  return s.split(" ").filter(Boolean).length;
}

const props = defineProps<{ page: PageDetail }>();
const emit = defineEmits<{ rename: [id: number, title: string] }>();

const title = ref(props.page.title);
const blocks = ref<Block[]>([...props.page.blocks]);
const itemRefs = ref<InstanceType<typeof BlockItem>[]>([]);

// Reset local editing state whenever the selected page changes.
watch(
  () => props.page.id,
  () => {
    title.value = props.page.title;
    blocks.value = [...props.page.blocks];
  },
);

// ── debounced persistence ─────────────────────────────────
const timers = new Map<string, number>();
function debounce(key: string, fn: () => void, ms = 400) {
  const existing = timers.get(key);
  if (existing) clearTimeout(existing);
  timers.set(key, window.setTimeout(fn, ms));
}

function onTitleInput(e: Event) {
  const value = (e.target as HTMLTextAreaElement).value;
  title.value = value;
  emit("rename", props.page.id, value);
  debounce("title", () => api.updatePage(props.page.id, { title: value }));
}

function onBlockUpdate(id: number, content: string) {
  const b = blocks.value.find((x) => x.id === id);
  if (b) b.content = content;
  debounce(`block-${id}`, () => api.updateBlock(id, { content }));
}

function onTransform(id: number, type: string, content: string) {
  const b = blocks.value.find((x) => x.id === id);
  if (!b) return;
  b.type = type;
  b.content = content;
  const idx = blocks.value.findIndex((x) => x.id === id);
  debounce(`block-${id}`, () =>
    api.updateBlock(id, { type, content }),
  );
  nextTick(() => itemRefs.value[idx]?.focus());
}

async function onEnter(afterId: number) {
  const idx = blocks.value.findIndex((b) => b.id === afterId);
  const position = idx + 1;
  const created = await api.createBlock(props.page.id, { type: "text", position });
  blocks.value.splice(position, 0, created);
  await nextTick();
  itemRefs.value[position]?.focus();
}

async function onRemoveEmpty(id: number) {
  if (blocks.value.length <= 1) return; // keep at least one block
  const idx = blocks.value.findIndex((b) => b.id === id);
  blocks.value.splice(idx, 1);
  await api.deleteBlock(id);
  await nextTick();
  itemRefs.value[Math.max(0, idx - 1)]?.focus();
}

function setItemRef(el: any, i: number) {
  if (el) itemRefs.value[i] = el;
}

// Live word count across every block, including unsaved in-progress edits.
// Updates whenever onBlockUpdate / onEnter / onRemoveEmpty mutate blocks.value.
const wordCount = computed(() =>
  blocks.value.reduce((n, b) => n + wordCountOf(b.content), 0),
);
</script>

<template>
  <main class="main">
    <div class="page">
      <textarea
        class="page__title"
        rows="1"
        :value="title"
        placeholder="Untitled"
        @input="onTitleInput"
      />
      <p class="page__word-count">{{ wordCount }} words</p>
      <BlockItem
        v-for="(block, i) in blocks"
        :key="block.id"
        :ref="(el) => setItemRef(el, i)"
        :block="block"
        @update="onBlockUpdate"
        @enter="onEnter"
        @remove-empty="onRemoveEmpty"
        @transform="onTransform"
      />
    </div>
  </main>
</template>
