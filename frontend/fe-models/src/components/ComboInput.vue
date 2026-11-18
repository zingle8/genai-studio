<template>
  <div class="combo" ref="rootEl">
    <input
      class="form-input"
      :value="modelValue"
      :placeholder="placeholder"
      autocomplete="off"
      @input="onInput"
      @focus="openList()"
      @keydown.esc="showList = false"
    />
    <button type="button" class="combo-arrow" tabindex="-1" aria-label="展开选项" @click.prevent="toggleList">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg>
    </button>
    <div v-if="showList && filtered.length" class="combo-list">
      <div
        v-for="opt in filtered"
        :key="opt"
        class="combo-item"
        :class="{ active: opt === modelValue }"
        @mousedown.prevent="pick(opt)"
      >{{ opt }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '' }
})
const emit = defineEmits(['update:modelValue'])

const showList = ref(false)
const rootEl = ref(null)

/* 聚焦/点箭头 → 展示全部选项；键入 → 按输入过滤（不强制匹配，任意输入即新增） */
const showFilter = ref(false)
const filtered = computed(() => {
  const opts = props.options || []
  if (!showFilter.value) return opts
  const v = (props.modelValue || '').trim().toLowerCase()
  if (!v) return opts
  const match = opts.filter(o => o.toLowerCase().includes(v))
  return match.length ? match : opts
})

function onInput(e) {
  emit('update:modelValue', e.target.value)
  showFilter.value = true
  showList.value = true
}
function openList() { showFilter.value = false; showList.value = true }
function toggleList() { showFilter.value = false; showList.value = !showList.value }
function pick(opt) { emit('update:modelValue', opt); showList.value = false }

function onDocClick(e) {
  if (rootEl.value && !rootEl.value.contains(e.target)) showList.value = false
}
onMounted(() => document.addEventListener('mousedown', onDocClick))
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))
</script>

<style>
/* 可输入 + 可点选下拉（支持自由输入新增值） */
.combo { position: relative; flex: 1; }
.combo .form-input { padding-right: 30px; }
.combo-arrow {
  position: absolute; right: 4px; top: 50%; transform: translateY(-50%);
  width: 24px; height: 24px; border: none; background: none; cursor: pointer;
  color: var(--text-muted, #8a94a6); display: flex; align-items: center; justify-content: center;
  border-radius: 6px;
}
.combo-arrow:hover { background: rgba(0,0,0,0.06); }
.combo-arrow svg { width: 14px; height: 14px; }
.combo-list {
  position: absolute; z-index: 30; top: calc(100% + 4px); left: 0; right: 0;
  max-height: 200px; overflow-y: auto;
  background: #fff; border: 1px solid var(--border-light, #e5e8ef); border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.12);
}
.combo-item {
  padding: 8px 12px; font-size: 13px; cursor: pointer; color: var(--text, #1f2430);
}
.combo-item:hover { background: var(--bg-soft, #f5f7fa); }
.combo-item.active { color: var(--primary, #4d6bfe); font-weight: 600; }
</style>
