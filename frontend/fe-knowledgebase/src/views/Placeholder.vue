<template>
  <div>
    <div class="page-header"><div><div class="page-title">{{ title }}</div><div class="page-subtitle">{{ desc }}</div></div></div>
    <div class="card">
      <div class="card-body empty" style="padding:80px 0; text-align:center;">
        <div style="font-size:15px; font-weight:600; margin-bottom:8px;">建设中</div>
        <div class="muted">本模块基于 Python 单体服务（FastAPI）实现，属第二波交付内容</div>
      </div>
    </div>
  </div>
</template>
<script setup>
defineProps({ title: String, desc: String })
</script>
