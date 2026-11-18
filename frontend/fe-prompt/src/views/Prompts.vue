<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">提示词管理</div>
        <div class="page-subtitle">模板创建 / 变量 / 标签（jv-genai-prompt）</div>
      </div>
      <div class="page-actions"><button class="btn btn-primary" @click="openCreate">＋ 新建模板</button></div>
    </div>
    <div class="filter-bar">
      <input class="form-input" v-model="keyword" placeholder="名称 / 标签" style="width:220px;" @keyup.enter="go(1)" />
      <button class="btn btn-primary" @click="load">查询</button>
      <div class="spacer"></div><span class="text-sm muted">共 {{ total }} 个模板</span>
    </div>
    <div class="card"><div class="card-body no-pad"><div class="table-wrap">
      <table>
        <thead><tr><th>模板名</th><th>内容</th><th>变量</th><th>标签</th><th>状态</th><th class="text-right">操作</th></tr></thead>
        <tbody>
          <tr v-for="p in list" :key="p.id">
            <td><b>{{ p.name }}</b></td>
            <td class="muted" style="max-width:320px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{{ p.content }}</td>
            <td><span v-for="v in splitVars(p.variables)" :key="v" class="tag" style="font-size:11px;">{{ '{' }}{{ v }}{{ '}' }}</span><span v-if="!p.variables" class="muted">-</span></td>
            <td><span v-for="t in splitVars(p.tags)" :key="t" class="tag tag-accent" style="font-size:11px;">{{ t }}</span></td>
            <td><span class="tag" :class="p.status === 1 ? 'tag-success' : ''">{{ p.status === 1 ? '启用' : '停用' }}</span></td>
            <td class="text-right">
              <span class="link" style="cursor:pointer;" @click="openEdit(p)">编辑</span> |
              <span class="link" style="cursor:pointer;" @click="toggle(p)">{{ p.status === 1 ? '停用' : '启用' }}</span> |
              <span class="link" style="color:var(--danger); cursor:pointer;" @click="remove(p)">删除</span>
            </td>
          </tr>
          <tr v-if="!list.length"><td colspan="6"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
        </tbody>
      </table>
    </div>
    <div class="card-footer">
      <div class="text-sm muted">共 {{ total }} 个模板</div>
      <div style="display:flex; align-items:center; gap:12px;">
        <select class="form-select page-size-select" v-model.number="size" @change="go(1)">
          <option :value="10">10 个/页</option>
          <option :value="20">20 个/页</option>
          <option :value="50">50 个/页</option>
          <option :value="100">100 个/页</option>
        </select>
        <span class="text-sm muted">第 {{ page }} / {{ totalPages }} 页</span>
        <button class="page-btn" :disabled="page <= 1" @click="go(page - 1)">‹ 上一页</button>
        <button class="page-btn" :disabled="page >= totalPages" @click="go(page + 1)">下一页 ›</button>
      </div>
    </div></div></div>

    <div class="modal-mask" :class="{ show: open }" @click.self="open = false">
      <div class="modal modal-lg">
        <div class="modal-header"><div class="modal-title">{{ editId ? '编辑模板' : '新建模板' }}</div><button class="modal-close" @click="open = false">×</button></div>
        <div class="modal-body">
          <div class="form-row"><label class="form-label">模板名称 <span class="required">*</span></label><input class="form-input" v-model="form.name" /></div>
          <div class="form-row"><label class="form-label">模板内容（变量用 <span v-pre><b>{{var}}</b></span> 占位）</label><textarea class="form-input" v-model="form.content" rows="6" style="resize:vertical;"></textarea></div>
          <div class="form-row"><label class="form-label">变量（逗号分隔）</label><input class="form-input" v-model="form.variables" placeholder="如 code,question" /></div>
          <div class="form-row" style="margin-bottom:0;"><label class="form-label">标签（逗号分隔）</label><input class="form-input" v-model="form.tags" placeholder="如 RAG,问答" /></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="open = false">取消</button>
          <button class="btn btn-primary" @click="submit">{{ editId ? '保存' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
const router = useRouter()
const list = ref([]); const total = ref(0); const keyword = ref(''); const open = ref(false); const editId = ref(null)
const page = ref(1); const size = ref(20)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / size.value)))
const form = ref({ name: '', content: '', variables: '', tags: '' })
onMounted(load)
async function load() {
  const res = await api('/api/prompts?keyword=' + encodeURIComponent(keyword.value) + '&page=' + page.value + '&size=' + size.value)
  if (res.code === 0) {
    list.value = res.data.list || []; total.value = res.data.total || 0
    if (!list.value.length && page.value > 1) { page.value = totalPages.value; return load() }
  }
}
function go(p) { page.value = Math.min(Math.max(1, p), totalPages.value); load() }
function openCreate() { editId.value = null; form.value = { name: '', content: '', variables: '', tags: '' }; open.value = true }
function openEdit(p) { editId.value = p.id; form.value = { name: p.name, content: p.content, variables: p.variables || '', tags: p.tags || '' }; open.value = true }
async function submit() {
  const res = editId.value
    ? await api('/api/prompts/' + editId.value, { method: 'PUT', body: JSON.stringify(form.value) })
    : await api('/api/prompts', { method: 'POST', body: JSON.stringify(form.value) })
  if (res.code === 0) { open.value = false; load() } else alert(res.message || '操作失败')
}
async function toggle(p) {
  await api('/api/prompts/' + p.id, { method: 'PUT', body: JSON.stringify({ status: p.status === 1 ? 0 : 1 }) })
  load()
}
async function remove(p) {
  if (!confirm('确认删除模板「' + p.name + '」？')) return
  await api('/api/prompts/' + p.id, { method: 'DELETE' }); load()
}
function splitVars(s) { return s ? s.split(',').filter(Boolean) : [] }
</script>
