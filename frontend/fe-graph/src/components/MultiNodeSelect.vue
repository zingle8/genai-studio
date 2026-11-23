<template>
  <div class="mns" ref="rootEl">
    <button type="button" class="mns-trigger" @click.stop="toggle">
      <span :class="{ ph: !modelValue.length }">{{ display }}</span>
      <span class="mns-caret" :class="{ up: open }">▾</span>
    </button>
    <div v-if="open" class="mns-panel" @click.stop>
      <div class="mns-search"><input ref="searchEl" v-model="kw" placeholder="搜索节点…" /></div>
      <div class="mns-options">
        <label v-for="o in filtered" :key="o.value" class="mns-option" @click.prevent="pick(o.value)">
          <input type="checkbox" :checked="isChecked(o.value)" @click.prevent /> {{ o.label }}
        </label>
        <div v-if="!filtered.length" class="mns-empty">无匹配节点</div>
      </div>
      <div class="mns-foot">
        <button type="button" @click="clear">清空（全图）</button>
        <button type="button" class="primary" @click="open = false">完成</button>
      </div>
    </div>
  </div>
</template>

<script setup>
/** 多选节点下拉：支持搜索、多选、清空（空=全图） */
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  options: { type: Array, default: () => [] },       // [{ value, label }]
  placeholder: { type: String, default: '全图（可多选）' }
})
const emit = defineEmits(['update:modelValue'])

const open = ref(false)
const kw = ref('')
const rootEl = ref(null)
const searchEl = ref(null)

const display = computed(() => {
  const arr = props.modelValue || []
  if (!arr.length) return props.placeholder
  const labels = arr.map(v => props.options.find(o => o.value === v)?.label ?? String(v))
  return labels.length <= 2 ? labels.join('、') : `已选 ${labels.length} 个节点`
})
const filtered = computed(() => {
  const k = kw.value.trim().toLowerCase()
  return k ? props.options.filter(o => String(o.label).toLowerCase().includes(k)) : props.options
})

function toggle() {
  open.value = !open.value
  if (open.value) { kw.value = ''; nextTick(() => searchEl.value?.focus()) }
}
function isChecked(v) { return (props.modelValue || []).includes(v) }
function pick(v) {
  const arr = [...(props.modelValue || [])]
  const i = arr.indexOf(v)
  if (i >= 0) arr.splice(i, 1)
  else arr.push(v)
  emit('update:modelValue', arr)
}
function clear() { emit('update:modelValue', []) }
function onDocClick(e) { if (rootEl.value && !rootEl.value.contains(e.target)) open.value = false }
onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>

<style>
.mns { position: relative; display: inline-block; min-width: 170px; }
.mns-trigger {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  width: 100%; min-width: 170px; height: 32px; padding: 0 9px;
  border: 1px solid var(--border-light, #e9ebf0); border-radius: 8px;
  background: #fff; font-size: 12.5px; color: #1f2430; cursor: pointer; white-space: nowrap;
}
.mns-trigger:hover { border-color: #4d6bfe; }
.mns-trigger span:first-child { flex: 1; overflow: hidden; text-overflow: ellipsis; text-align: left; }
.mns-trigger .ph { color: #9ca3af; }
.mns-caret { color: #9ca3af; transition: transform .16s; }
.mns-caret.up { transform: rotate(180deg); }
.mns-panel {
  position: absolute; z-index: 80; top: calc(100% + 5px); left: 0; width: max(230px, 100%);
  max-height: 300px; display: flex; flex-direction: column;
  background: #fff; border: 1px solid var(--border-light, #e9ebf0); border-radius: 10px;
  box-shadow: 0 8px 26px rgba(0,0,0,.14);
}
.mns-search { padding: 7px 9px; border-bottom: 1px solid #f0f1f5; }
.mns-search input { width: 100%; height: 28px; padding: 0 8px; border: 1px solid #e9ebf0; border-radius: 6px; font-size: 12.5px; outline: none; }
.mns-options { flex: 1; min-height: 0; overflow-y: auto; padding: 4px; }
.mns-option { display: flex; align-items: center; gap: 7px; padding: 6px 7px; border-radius: 6px; font-size: 12.5px; cursor: pointer; }
.mns-option:hover { background: #f4f6fb; }
.mns-option input { accent-color: #4d6bfe; }
.mns-empty { padding: 16px 0; text-align: center; font-size: 12px; color: #9ca3af; }
.mns-foot { display: flex; justify-content: space-between; gap: 6px; padding: 7px 9px; border-top: 1px solid #f0f1f5; }
.mns-foot button { height: 26px; padding: 0 10px; border: 1px solid #e9ebf0; border-radius: 6px; background: #fff; font-size: 12px; color: #6b7280; cursor: pointer; }
.mns-foot button.primary { background: #4d6bfe; border-color: #4d6bfe; color: #fff; }
</style>
