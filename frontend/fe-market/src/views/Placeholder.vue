<template>
  <div class="ph">
    <div class="ph-icon">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><path d="M3 9h18M9 21V9"/></svg>
    </div>
    <div class="ph-title">{{ title }}</div>
    <div class="ph-desc">{{ desc }}</div>
    <div class="ph-tag">建设中</div>
    <div class="ph-tip">该功能规划中，敬请期待。当前可先通过对应的管理页面进行配置。</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const route = useRoute()
const title = computed(() => route.meta.title || '市场')
const desc = computed(() => route.meta.desc || '')
</script>

<style scoped>
.ph { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 60vh; text-align: center; }
.ph-icon { width: 64px; height: 64px; border-radius: 18px; background: linear-gradient(135deg, #eef2ff, #e0e7ff); color: #6366f1; display: flex; align-items: center; justify-content: center; margin-bottom: 18px; }
.ph-icon svg { width: 30px; height: 30px; }
.ph-title { font-size: 20px; font-weight: 700; color: #1f2937; }
.ph-desc { margin-top: 6px; font-size: 13.5px; color: #6b7280; }
.ph-tag { margin-top: 16px; font-size: 12px; color: #d97706; background: #fef3c7; border: 1px solid #fde68a; padding: 3px 12px; border-radius: 999px; }
.ph-tip { margin-top: 14px; font-size: 12px; color: #9ca3af; }
</style>
