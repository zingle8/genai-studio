<template>
  <div class="gw-select" ref="rootEl" :class="{ open: open, disabled: disabled }">
    <button type="button" class="gw-select-trigger" :disabled="disabled" @click="toggle">
      <span class="gw-select-value" :class="{ placeholder: !display }">{{ display || placeholder }}</span>
      <svg class="gw-caret" :class="{ up: open }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
    </button>
    <teleport to="body" :disabled="!fixed">
      <transition name="gw-drop">
        <div v-if="open" class="gw-panel" :class="{ 'gw-panel-fixed': fixed }" :style="fixed ? panelStyle : null" @click.stop ref="panelEl">
          <div v-if="searchable" class="gw-search">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4-4"/></svg>
            <input ref="searchEl" v-model="kw" placeholder="搜索…" @keydown.esc.stop="close" />
          </div>
          <div class="gw-options">
            <button v-for="o in filtered" :key="String(o.value)" type="button" class="gw-option"
                    :class="{ selected: isChecked(o.value) }" @click="pick(o)">
              <span v-if="multiple" class="gw-check" :class="{ on: isChecked(o.value) }">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>
              </span>
              <span class="gw-option-body">
                <span class="gw-option-label">{{ o.label }}</span>
                <span v-if="o.desc" class="gw-option-desc">{{ o.desc }}</span>
              </span>
              <span v-if="o.tag" class="gw-option-tag" :class="o.tagCls">{{ o.tag }}</span>
            </button>
            <button v-if="canCreate" type="button" class="gw-option create" @click="pickCreate">
              <span class="gw-create-plus">+</span>
              <span class="gw-option-body">
                <span class="gw-option-label">使用「{{ kw }}」</span>
                <span class="gw-option-desc">输入的新值（不在列表中）</span>
              </span>
            </button>
            <div v-if="!filtered.length && !canCreate" class="gw-panel-empty">无匹配项</div>
          </div>
          <div v-if="multiple" class="gw-panel-foot">
            <button type="button" class="gw-foot-btn" @click="clearAll">清空</button>
            <button type="button" class="gw-foot-btn primary" @click="close">完成</button>
          </div>
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup>
/* 统一下拉选择器（替换原生 select）：单选/多选/搜索/点击外部关闭 */
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  modelValue: { type: [String, Number, Array], default: '' },
  options: { type: Array, default: () => [] },          // [{ value, label, desc?, tag?, tagCls? }]
  multiple: { type: Boolean, default: false },
  searchable: { type: Boolean, default: false },
  creatable: { type: Boolean, default: false },          // 可直接输入新值（配 searchable 使用）
  placeholder: { type: String, default: '请选择' },
  disabled: { type: Boolean, default: false },
  fixed: { type: Boolean, default: false }               // 面板 teleport 到 body 用 fixed 定位（弹层容器 overflow 会裁剪时使用）
})
const emit = defineEmits(['update:modelValue', 'create'])

const open = ref(false)
const kw = ref('')
const rootEl = ref(null)
const panelEl = ref(null)
const searchEl = ref(null)
const panelStyle = ref({})

/** fixed 模式：按触发按钮位置计算面板坐标，屏幕下方放不下时向上弹 */
function placePanel() {
  const btn = rootEl.value?.querySelector('.gw-select-trigger')
  if (!btn) return
  const r = btn.getBoundingClientRect()
  const vh = window.innerHeight
  const est = Math.min(300, props.options.length * 36 + 60)
  const st = { left: Math.round(r.left) + 'px', width: Math.round(r.width) + 'px' }
  if (r.bottom + 6 + est < vh - 8) st.top = Math.round(r.bottom + 5) + 'px'
  else {
    st.bottom = Math.round(vh - r.top + 5) + 'px'
    st.maxHeight = Math.max(160, Math.round(r.top - 14)) + 'px'   // 向上弹时不超出视口顶部
  }
  panelStyle.value = st
}

const display = computed(() => {
  if (props.multiple) {
    const arr = Array.isArray(props.modelValue) ? props.modelValue : []
    if (!arr.length) return ''
    if (arr.length <= 2) return arr.map(v => labelOf(v)).join('、')
    return `已选 ${arr.length} 个`
  }
  return labelOf(props.modelValue)
})
function labelOf(v) { return props.options.find(o => o.value === v)?.label ?? '' }

const filtered = computed(() => {
  const k = kw.value.trim().toLowerCase()
  if (!k) return props.options
  return props.options.filter(o =>
    (o.label || '').toLowerCase().includes(k) ||
    (o.desc || '').toLowerCase().includes(k))
})

/** 输入了列表中不存在的新值（creatable 模式） */
const canCreate = computed(() =>
  props.creatable && kw.value.trim() !== '' &&
  !props.options.some(o => o.value === kw.value.trim() || o.label === kw.value.trim()))

function isChecked(v) {
  return props.multiple ? (Array.isArray(props.modelValue) && props.modelValue.includes(v))
                        : props.modelValue === v
}

function toggle() {
  if (props.disabled) return
  open.value ? close() : show()
}
function show() {
  kw.value = ''
  open.value = true
  nextTick(() => {
    if (props.fixed) placePanel()
    if (props.searchable) searchEl.value?.focus()
  })
}
function close() { open.value = false }

function pick(o) {
  if (props.multiple) {
    const arr = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const i = arr.indexOf(o.value)
    i >= 0 ? arr.splice(i, 1) : arr.push(o.value)
    emit('update:modelValue', arr)
  } else {
    emit('update:modelValue', o.value)
    close()
  }
}
function clearAll() { emit('update:modelValue', []) }

/** 使用输入的新值 */
function pickCreate() {
  const v = kw.value.trim()
  if (!v) return
  emit('update:modelValue', v)
  emit('create', v)
  close()
}

function onDocClick(e) {
  const t = e.target
  if (rootEl.value?.contains(t)) return
  if (props.fixed && panelEl.value?.contains(t)) return  // teleport 后面板不在 rootEl 内
  close()
}
onMounted(() => document.addEventListener('click', onDocClick))
onBeforeUnmount(() => document.removeEventListener('click', onDocClick))
</script>

<style>
.gw-select { position: relative; overflow: visible; }
.gw-select-trigger {
  display: flex; align-items: center; gap: 8px; width: 100%;
  height: 34px; padding: 0 10px 0 12px;
  border: 1px solid var(--border); border-radius: var(--radius);
  background: #fff; cursor: pointer; text-align: left;
  transition: border-color .15s, box-shadow .15s;
}
.gw-select-trigger:hover { border-color: var(--text-quaternary); }
.gw-select.open .gw-select-trigger { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
.gw-select.disabled .gw-select-trigger { opacity: .55; cursor: not-allowed; }
.gw-select-value {
  flex: 1; min-width: 0; font-size: 13px; color: var(--text-primary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.gw-select-value.placeholder { color: var(--text-quaternary); }
.gw-caret { width: 14px; height: 14px; flex-shrink: 0; color: var(--text-tertiary); transition: transform .18s; }
.gw-caret.up { transform: rotate(180deg); }
.gw-panel {
  position: absolute; z-index: 80; left: 0; right: 0; top: calc(100% + 5px);
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg); overflow: hidden;
}
.gw-panel-fixed { position: fixed; z-index: 9999; min-width: 140px; top: auto; bottom: auto; left: auto; right: auto; display: flex; flex-direction: column; }
.gw-panel-fixed .gw-options { flex: 1; min-height: 0; max-height: none; }
.gw-drop-enter-active, .gw-drop-leave-active { transition: opacity .14s, transform .14s; }
.gw-drop-enter-from, .gw-drop-leave-to { opacity: 0; transform: translateY(-4px); }
.gw-search {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; border-bottom: 1px solid var(--border-light);
}
.gw-search svg { width: 13px; height: 13px; color: var(--text-tertiary); flex-shrink: 0; }
.gw-search input { flex: 1; border: none; outline: none; font-size: 12.5px; color: var(--text-primary); background: none; }
.gw-options { max-height: 240px; overflow-y: auto; padding: 4px; }
.gw-option {
  display: flex; align-items: center; gap: 8px; width: 100%;
  padding: 7px 8px; border: none; background: none; border-radius: var(--radius-sm);
  cursor: pointer; text-align: left; transition: background .12s;
}
.gw-option:hover { background: var(--bg-soft); }
.gw-option.selected { background: var(--accent-soft); }
.gw-check {
  width: 15px; height: 15px; flex-shrink: 0; border: 1.5px solid var(--text-quaternary);
  border-radius: 4px; display: flex; align-items: center; justify-content: center;
  transition: background .12s, border-color .12s;
}
.gw-check.on { background: var(--accent); border-color: var(--accent); color: #fff; }
.gw-check svg { width: 10px; height: 10px; opacity: 0; }
.gw-check.on svg { opacity: 1; }
.gw-option-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 1px; }
.gw-option-label { font-size: 13px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gw-option-desc { font-size: 11px; color: var(--text-tertiary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.gw-option-tag {
  flex-shrink: 0; font-size: 10px; padding: 1px 6px; border-radius: 4px;
  background: var(--bg-soft); color: var(--text-secondary);
}
.gw-option-tag.tag-danger { background: var(--danger-soft); color: var(--danger); }
.gw-option-tag.tag-success { background: var(--success-soft); color: var(--success); }
.gw-panel-empty { padding: 18px 0; text-align: center; font-size: 12px; color: var(--text-tertiary); }
.gw-option.create { color: var(--accent); }
.gw-create-plus {
  width: 15px; height: 15px; flex-shrink: 0; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 13px;
}
.gw-option.create .gw-option-label { overflow: hidden; text-overflow: ellipsis; max-width: 200px; }
.gw-panel-foot {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 8px 10px; border-top: 1px solid var(--border-light); background: var(--bg-page);
}
.gw-foot-btn {
  height: 26px; padding: 0 12px; font-size: 12px; border-radius: var(--radius-sm);
  border: 1px solid var(--border); background: #fff; cursor: pointer; color: var(--text-secondary);
}
.gw-foot-btn:hover { background: var(--bg-soft); }
.gw-foot-btn.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
.gw-foot-btn.primary:hover { background: var(--accent-hover); }
</style>
