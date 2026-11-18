<template>
  <div>
    <div class="page-header">
      <div><div class="page-title">MCP 管理</div><div class="page-subtitle">MCP 服务注册 / 启停（jv-genai-mcpgateway）</div></div>
      <div class="page-actions"><button class="btn btn-primary" @click="openCreate">＋ 注册 MCP 服务</button></div>
    </div>
    <div class="card"><div class="card-body no-pad"><div class="table-wrap">
      <table>
        <thead><tr>
                <th>名称</th>
                <th>端点</th>
                <th>鉴权</th>
                <th>状态</th>
                <th>备注</th>
                <th class="text-right">操作</th>
        </tr></thead>
        <tbody>
          <tr v-for="row in list" :key="row.id">
                <td><b>{{ row.name }}</b></td>
                <td><span class="mono">{{ row.endpoint }}</span></td>
                <td>{{ row.authType }}</td>
                <td><span class="tag" :class="row.status === 1 ? 'tag-success' : ''">{{ row.status === 1 ? "启用" : "停用" }}</span></td>
                <td><span class="muted">{{ row.remark }}</span></td>
            <td class="text-right">
              <span class="link" style="cursor:pointer;" @click="openEdit(row)">编辑</span> |
              <span class="link" style="color:var(--danger); cursor:pointer;" @click="remove(row)">删除</span>
            </td>
          </tr>
          <tr v-if="!list.length"><td colspan="6"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
        </tbody>
      </table>
    </div></div></div>

    <div class="modal-mask" :class="{ show: open }" @click.self="open = false">
      <div class="modal">
        <div class="modal-header"><div class="modal-title">{{ editId ? '编辑' : '注册 MCP 服务' }}</div><button class="modal-close" @click="open = false">×</button></div>
        <div class="modal-body">
          <div class="form-row"><label class="form-label">名称 *</label><input class="form-input" v-model="form.name" placeholder="如 天气查询 MCP" /></div>
          <div class="form-row"><label class="form-label">端点 *</label><input class="form-input" v-model="form.endpoint" placeholder="http://…" /></div>
          <div class="form-row"><label class="form-label">鉴权(none/token/oauth)</label><input class="form-input" v-model="form.authType" placeholder="none" /></div>
          <div class="form-row"><label class="form-label">备注</label><input class="form-input" v-model="form.remark" placeholder="" /></div>
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
const form = ref({name: '', endpoint: '', authType: '', remark: ''})
onMounted(load)
async function load() {
  const res = await api('/api/mcp?size=50')
  if (res.code === 0) list.value = res.data.list || res.data || []
}
function openCreate() { editId.value = null; form.value = {name: '', endpoint: '', authType: '', remark: ''}; open.value = true }
function openEdit(row) { editId.value = row.id; form.value = {name: row.name == null ? '' : row.name, endpoint: row.endpoint == null ? '' : row.endpoint, authType: row.authType == null ? '' : row.authType, remark: row.remark == null ? '' : row.remark}; open.value = true }
async function submit() {
  const res = editId.value
    ? await api('/api/mcp/' + editId.value, { method: 'PUT', body: JSON.stringify(form.value) })
    : await api('/api/mcp', { method: 'POST', body: JSON.stringify(form.value) })
  if (res.code === 0) { open.value = false; load() } else alert(res.message || '操作失败')
}
async function remove(row) {
  if (!confirm('确认删除「' + row.name + '」？')) return
  await api('/api/mcp/' + row.id, { method: 'DELETE' }); load()
}
</script>
