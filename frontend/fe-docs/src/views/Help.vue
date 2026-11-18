<template>
  <div>
    <div class="page-header"><div><div class="page-title">帮助与反馈</div><div class="page-subtitle">常见问题与问题反馈</div></div></div>
    <div class="card" style="margin-bottom:16px;">
      <div class="card-header"><b>常见问题</b></div>
      <div class="card-body" style="display:flex; flex-direction:column; gap:14px;">
        <div v-for="f in faqs" :key="f.q">
          <div style="font-weight:600; font-size:13.5px;">Q：{{ f.q }}</div>
          <div class="muted" style="font-size:13px; margin-top:4px; line-height:1.7;">A：{{ f.a }}</div>
        </div>
      </div>
    </div>
    <div class="card">
      <div class="card-header"><b>反馈渠道</b></div>
      <div class="card-body muted" style="font-size:13px; line-height:2;">
        平台问题请提交至内部工单系统（应用：app-genai-studio）。<br/>
        网关平台相关问题请联系平台组（jv-api-gateway）。
      </div>
    </div>
  </div>
</template>

<script setup>
const faqs = [
  { q: 'API Key 在哪里创建？', a: '左侧菜单「API Key」进入开发者控制台，创建后密钥仅展示一次，请立即保存。' },
  { q: '体验中心的回复是真实模型吗？', a: '当前为演示回复。模型推理将通过 AI 网关（jv-genai-aigateway）接入本地模型（Ollama 等）。' },
  { q: '账单和成本数据从哪里来？', a: '账单来自计费服务（jv-genai-billing），成本来自日志 T+1 聚合（jv-genai-costs）。' },
  { q: '忘记密码怎么办？', a: '账号体系统一在网关平台，请联系平台管理员重置。' }
]
</script>
