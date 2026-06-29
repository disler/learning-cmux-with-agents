<script setup lang="ts">
import { nextTick, onMounted, ref, watch } from "vue";
import type { Block } from "../api";

const props = defineProps<{ block: Block }>();

const emit = defineEmits<{
  update: [id: number, content: string];
  enter: [id: number];
  removeEmpty: [id: number];
  transform: [id: number, type: string, content: string];
}>();

const ta = ref<HTMLTextAreaElement | null>(null);

function autosize() {
  const el = ta.value;
  if (!el) return;
  el.style.height = "auto";
  el.style.height = `${el.scrollHeight}px`;
}

onMounted(autosize);
watch(() => props.block.content, () => nextTick(autosize));

// Markdown-style shortcuts: typing one of these prefixes at the start of a
// `text` block converts it to a different block type.
const PREFIXES: Array<[string, string]> = [
  ["# ", "heading"],
  ["- ", "bullet"],
  ["* ", "bullet"],
  ["> ", "quote"],
];

function placeholderFor(type: string): string {
  if (type === "heading") return "Heading";
  if (type === "bullet") return "List item";
  return "Type something…";
}

function onInput(e: Event) {
  autosize();
  const el = e.target as HTMLTextAreaElement;
  const value = el.value;
  emit("update", props.block.id, value);

  // Markdown shortcut: a trailing space was just typed at the start of a
  // plain `text` block, completing one of the trigger prefixes. We detect
  // this by checking that the content *starts with* the prefix AND the
  // cursor sits exactly at the end of the prefix — i.e. selectionStart
  // equals the prefix length, which only happens the instant the trailing
  // space is typed (further typing moves the cursor past it).
  if (props.block.type === "text") {
    for (const [prefix, newType] of PREFIXES) {
      if (value.startsWith(prefix) && el.selectionStart === prefix.length) {
        emit("transform", props.block.id, newType, value.slice(prefix.length));
        return;
      }
    }
  }
}

function onEnter(e: KeyboardEvent) {
  e.preventDefault();
  emit("enter", props.block.id);
}

function onBackspace() {
  if (props.block.content !== "") return;
  // On an empty transformed block, revert to plain text instead of deleting.
  if (props.block.type !== "text") {
    emit("transform", props.block.id, "text", "");
  } else {
    emit("removeEmpty", props.block.id);
  }
}

function focus() {
  ta.value?.focus();
}
defineExpose({ focus });
</script>

<template>
  <div class="block" :class="`block--${block.type}`">
    <textarea
      ref="ta"
      rows="1"
      :value="block.content"
      :placeholder="placeholderFor(block.type)"
      @input="onInput"
      @keydown.enter.exact="onEnter"
      @keydown.backspace="onBackspace"
    />
  </div>
</template>