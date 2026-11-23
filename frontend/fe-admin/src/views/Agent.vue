<template>
  <div>
    <div class="page-header">
      <div><div class="page-title">Skill / Agent</div><div class="page-subtitle">智能体与技能注册（jv-genai-agentgateway）</div></div>
      <div class="page-actions"><button class="btn btn-primary" @click="openCreate">＋ 注册 Skill / Agent</button></div>
    </div>
    <div class="card"><div class="card-body no-pad"><div class="table-wrap">
      <table>
        <thead><tr>
                <th>名称</th>
                <th>类型</th>
                <th>模型</th>
                <th>工具</th>
                <th>说明</th>
                <th>状态</th>
                <th class="text-right">操作</th>
        </tr></thead>
        <tbody>
          <tr v-for="row in list" :key="row.id">
                <td><b>{{ row.name }}</b></td>
                <td><span class="tag" :class="row.type === 'Agent' ? 'tag-accent' : ''">{{ row.type }}</span></td>
                <td>{{ row.model }}</td>
                <td><span class="muted">{{ row.tools || "-" }}</span></td>
                <td><span class="muted">{{ row.description }}</span></td>
                <td><span class="tag" :class="row.enabled === 1 ? 'tag-success' : ''">{{ row.enabled === 1 ? "启用" : "停用" }}</span></td>
            <td class="text-right">
              <span class="link" style="cursor:pointer;" @click="openEdit(row)">编辑</span> |
              <span class="link" style="color:var(--danger); cursor:pointer;" @click="remove(row)">删除</span>
            </td>
          </tr>
          <tr v-if="!list.length"><td colspan="7"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
        </tbody>
      </table>
    </div></div></div>

    <div v-if="open" class="modal-mask show" style="display:flex" @click.self="open = false">
      <div class="modal">
        <div class="modal-header"><div class="modal-title">{{ editId ? '编辑' : '注册 Skill / Agent' }}</div><button class="modal-close" @click="open = false">×</button></div>
        <div class="modal-body">
          <div class="form-row"><label class="form-label">名称 *</label><input class="form-input" v-model="form.name" placeholder="" /></div>
          <div class="form-row"><label class="form-label">类型(Skill/Agent)</label><input class="form-input" v-model="form.type" placeholder="Agent" /></div>
          <div class="form-row"><label class="form-label">模型</label><input class="form-input" v-model="form.model" placeholder="如 GLM-4.7" /></div>
          <div class="form-row"><label class="form-label">工具(逗号分隔)</label><input class="form-input" v-model="form.tools" placeholder="" /></div>
          <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="form.description" placeholder="" /></div>
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
import { ref, onMounted } from 'vue'
import { api } from '../api'
const list = ref([]); const open = ref(false); const editId = ref(null)
const form = ref({name: '', type: '', model: '', tools: '', description: ''})
onMounted(load)
async function load() {
  const res = await api('/api/agents?size=50')
  if (res.code === 0) list.value = res.data.list || res.data || []
}
function openCreate() { editId.value = null; form.value = {name: '', type: '', model: '', tools: '', description: ''}; open.value = true }
function openEdit(row) { editId.value = row.id; form.value = {name: row.name == null ? '' : row.name, type: row.type == null ? '' : row.type, model: row.model == null ? '' : row.model, tools: row.tools == null ? '' : row.tools, description: row.description == null ? '' : row.description}; open.value = true }
async function submit() {
  const res = editId.value
    ? await api('/api/agents/' + editId.value, { method: 'PUT', body: JSON.stringify(form.value) })
    : await api('/api/agents', { method: 'POST', body: JSON.stringify(form.value) })
  if (res.code === 0) { open.value = false; load() } else alert(res.message || '操作失败')
}
async function remove(row) {
  if (!confirm('确认删除「' + row.name + '」？')) return
  await api('/api/agents/' + row.id, { method: 'DELETE' }); load()
}
</script>
