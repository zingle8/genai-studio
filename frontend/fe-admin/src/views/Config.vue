<template>
  <div>
    <div class="page-header">
      <div><div class="page-title">平台配置</div><div class="page-subtitle">全局配置项（jv-genai-config）</div></div>
      <div class="page-actions"><button class="btn btn-primary" @click="openCreate">＋ 新增配置</button></div>
    </div>
    <div class="card"><div class="card-body no-pad"><div class="table-wrap">
      <table>
        <thead><tr>
                <th>配置键</th>
                <th>配置值</th>
                <th>说明</th>
                <th class="text-right">操作</th>
        </tr></thead>
        <tbody>
          <tr v-for="row in list" :key="row.id">
                <td><b class="mono">{{ row.configKey }}</b></td>
                <td><span class="mono">{{ row.configValue }}</span></td>
                <td><span class="muted">{{ row.remark }}</span></td>
            <td class="text-right">
              <span class="link" style="cursor:pointer;" @click="openEdit(row)">编辑</span> |
              <span class="link" style="color:var(--danger); cursor:pointer;" @click="remove(row)">删除</span>
            </td>
          </tr>
          <tr v-if="!list.length"><td colspan="4"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
        </tbody>
      </table>
    </div></div></div>

    <div v-if="open" class="modal-mask show" style="display:flex" @click.self="open = false">
      <div class="modal">
        <div class="modal-header"><div class="modal-title">{{ editId ? '编辑' : '新增配置' }}</div><button class="modal-close" @click="open = false">×</button></div>
        <div class="modal-body">
          <div class="form-row"><label class="form-label">配置键 *</label><input class="form-input" v-model="form.configKey" placeholder="如 model.default" /></div>
          <div class="form-row"><label class="form-label">配置值</label><input class="form-input" v-model="form.configValue" placeholder="" /></div>
          <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="form.remark" placeholder="" /></div>
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
const form = ref({configKey: '', configValue: '', remark: ''})
onMounted(load)
async function load() {
  const res = await api('/api/configs?size=50')
  if (res.code === 0) list.value = res.data.list || res.data || []
}
function openCreate() { editId.value = null; form.value = {configKey: '', configValue: '', remark: ''}; open.value = true }
function openEdit(row) { editId.value = row.id; form.value = {configKey: row.configKey == null ? '' : row.configKey, configValue: row.configValue == null ? '' : row.configValue, remark: row.remark == null ? '' : row.remark}; open.value = true }
async function submit() {
  const res = editId.value
    ? await api('/api/configs/' + editId.value, { method: 'PUT', body: JSON.stringify(form.value) })
    : await api('/api/configs', { method: 'POST', body: JSON.stringify(form.value) })
  if (res.code === 0) { open.value = false; load() } else alert(res.message || '操作失败')
}
async function remove(row) {
  if (!confirm('确认删除「' + row.configKey + '」？')) return
  await api('/api/configs/' + row.id, { method: 'DELETE' }); load()
}
</script>
