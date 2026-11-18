<template>
  <div class="login-page">
    <div class="login-top">
      <span class="login-brand">
        <span class="logo-brand">GenAI Studio</span>
        <span class="logo-badge">管理平台</span>
      </span>
      <span v-if="signedName" class="signed-chip show">
        <span class="dot"></span>
        当前已登录：<b>{{ signedName }}</b>
        <a href="/home">进入工作台 →</a>
      </span>
    </div>

    <div class="login-main">
      <div class="login-card">
        <div class="brand-row">
          <h1>API网关平台</h1>
          <span class="badge-ms">微服务</span>
        </div>
        <p class="brand-sub">API Gateway Management Console</p>

        <div class="ltabs">
          <button class="ltab" :class="{ active: activeTab === 'login' }" @click="switchTab('login')">账号登录</button>
          <button class="ltab" :class="{ active: activeTab === 'register' }" @click="switchTab('register')">注册账号</button>
        </div>

        <!-- 账号登录 -->
        <form v-if="activeTab === 'login'" @submit.prevent="doLogin" autocomplete="off">
          <div class="field" :class="{ focus: focusField === 'u' }">
            <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            <input v-model="username" class="f-input" placeholder="admin"
                   @focus="focusField = 'u'" @blur="focusField = ''" />
          </div>

          <div class="field" :class="{ focus: focusField === 'p' }">
            <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input v-model="password" class="f-input" :type="showPwd ? 'text' : 'password'" placeholder="请输入密码"
                   @focus="focusField = 'p'" @blur="focusField = ''" />
            <button class="eye-btn" type="button" tabindex="-1" @click="showPwd = !showPwd"
                    :title="showPwd ? '隐藏密码' : '显示密码'">
              <svg v-if="!showPwd" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
            </button>
          </div>

          <div class="remember-row">
            <label class="remember">
              <input v-model="remember" type="checkbox" />
              <span>记住我</span>
            </label>
          </div>

          <button class="login-btn" type="submit" :disabled="loading">
            {{ loading ? '登录中…' : '登 录' }}
          </button>
          <div class="login-err">{{ error }}</div>
        </form>

        <!-- 注册账号 -->
        <form v-else @submit.prevent="doRegister" autocomplete="off">
          <div class="field" :class="{ focus: focusField === 'ru' }">
            <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            <input v-model="rUsername" class="f-input" placeholder="请输入用户名"
                   @focus="focusField = 'ru'" @blur="focusField = ''" />
          </div>
          <div class="field" :class="{ focus: focusField === 'rp' }">
            <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input v-model="rPassword" class="f-input" type="password" placeholder="请输入密码"
                   @focus="focusField = 'rp'" @blur="focusField = ''" />
          </div>
          <div class="field" :class="{ focus: focusField === 'rc' }">
            <svg class="f-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input v-model="rConfirm" class="f-input" type="password" placeholder="请再次输入密码"
                   @focus="focusField = 'rc'" @blur="focusField = ''" />
          </div>
          <button class="login-btn reg-btn" type="submit" :disabled="loading">
            {{ loading ? '注册中…' : '注 册' }}
          </button>
          <div class="login-err">{{ error }}</div>
        </form>

        <div class="card-foot">
          内置管理员账号：<b>admin / Admin@123</b>
        </div>
      </div>
    </div>

    <div class="login-foot">Copyright © 2026 GenAI Studio · 认证服务 jv-genai-auth</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, getUser } from '../api'

const router = useRouter()
const username = ref('admin')
const password = ref('Admin@123')
const loading = ref(false)
const error = ref('')
const signedName = ref(getUser()?.name || '')

const activeTab = ref('login')
const showPwd = ref(false)
const remember = ref(true)
const focusField = ref('')

const rUsername = ref('')
const rPassword = ref('')
const rConfirm = ref('')

function switchTab(tab) {
  activeTab.value = tab
  error.value = ''
}

async function submit(u, p) {
  error.value = ''
  loading.value = true
  try {
    const res = await api('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username: u, password: p })
    })
    if (res.code === 0 && res.data) {
      const token = res.data.token || res.data.accessToken || ''
      localStorage.setItem('genai_token', token)
      const user = res.data.user || {
        name: res.data.nickname || res.data.username || u,
        username: res.data.username || u,
        role: res.data.role
      }
      localStorage.setItem('genai_user', JSON.stringify(user))
      router.push('/home')
    } else {
      error.value = res.message || '登录失败（需网关平台用户服务可用）'
    }
  } catch (e) {
    error.value = '认证服务连接失败（jv-genai-auth @ 38081），请确认后端已启动'
  } finally {
    loading.value = false
  }
}

function doLogin() {
  if (!username.value.trim() || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  submit(username.value.trim(), password.value)
}

async function doRegister() {
  error.value = ''
  if (!rUsername.value.trim() || !rPassword.value) {
    error.value = '请输入用户名和密码'
    return
  }
  if (rPassword.value !== rConfirm.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  loading.value = true
  try {
    const res = await api('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username: rUsername.value.trim(), password: rPassword.value })
    })
    if (res.code === 0 || res.success) {
      username.value = rUsername.value.trim()
      password.value = rPassword.value
      rUsername.value = ''
      rPassword.value = ''
      rConfirm.value = ''
      activeTab.value = 'login'
      alert('注册成功，请登录')
    } else {
      error.value = res.message || '注册失败'
    }
  } catch (e) {
    error.value = '认证服务连接失败（jv-genai-auth @ 38081），请确认后端已启动'
  } finally {
    loading.value = false
  }
}
</script>

<style>
.login-page { background: #F2F3F5; min-height: 100vh; display: flex; flex-direction: column; }
.login-top { display: flex; align-items: center; justify-content: space-between; padding: 22px 32px 0; gap: 16px; flex-wrap: wrap; }
.login-brand { display: flex; align-items: center; gap: 8px; }
.login-brand .logo-brand { font-size: 18px; font-weight: 700; letter-spacing: -0.4px; }
.login-brand .logo-badge { font-size: 10px; color: #fff; background: var(--text-primary); padding: 2px 6px; border-radius: 4px; font-weight: 500; }
.signed-chip { display: none; align-items: center; gap: 8px; height: 32px; padding: 0 6px 0 10px; background: #fff; border: 1px solid var(--border); border-radius: 16px; font-size: 12.5px; color: var(--text-secondary); }
.signed-chip.show { display: inline-flex; }
.signed-chip a { color: var(--accent); font-weight: 500; }
.signed-chip .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--success); }

.login-main { flex: 1; display: flex; align-items: flex-start; justify-content: center; padding: 56px 20px 40px; }
.login-card {
  width: 100%; max-width: 620px; background: #fff; border-radius: 12px;
  padding: 46px 56px 24px; box-shadow: 0 4px 18px rgba(16, 24, 40, .05);
  border: 1px solid #EBEDF0;
}
.brand-row { display: flex; align-items: center; gap: 12px; }
.brand-row h1 { margin: 0; font-size: 28px; font-weight: 700; letter-spacing: -0.5px; color: #1F2329; }
.badge-ms { font-size: 12.5px; color: #fff; background: #1F2329; padding: 3px 9px; border-radius: 5px; font-weight: 500; }
.brand-sub { margin: 8px 0 0; font-size: 15.5px; color: #8A9099; letter-spacing: .2px; }

.ltabs { display: flex; margin-top: 36px; border-bottom: 1px solid #E5E7EB; }
.ltab { flex: 1; position: relative; background: transparent; background: none; border: 0; cursor: pointer; padding: 0 0 14px; font-size: 17px; color: #4B5563; font-weight: 500; transition: color .15s; }
.ltab:hover { color: #2E7CF6; }
.ltab.active { background: transparent; color: #2E7CF6; font-weight: 600; }
.ltab.active::after { content: ''; position: absolute; left: 0; right: 0; bottom: -1px; height: 3px; border-radius: 2px; background: #2E7CF6; }

.field { display: flex; align-items: center; gap: 12px; height: 56px; margin-top: 26px; padding: 0 16px; border: 1px solid #DCDFE6; border-radius: 8px; background: #fff; transition: border-color .15s, box-shadow .15s; }
.field.focus { border-color: #2E7CF6; box-shadow: 0 0 0 3px rgba(46, 124, 246, .10); }
.f-icon { width: 20px; height: 20px; color: #A3A9B3; flex-shrink: 0; }
.f-input { flex: 1; min-width: 0; height: 100%; border: 0; outline: 0; font-size: 16px; color: #1F2329; background: transparent; }
.f-input::placeholder { color: #A3A9B3; }
.eye-btn { background: none; border: 0; padding: 4px; cursor: pointer; color: #A3A9B3; display: flex; }
.eye-btn:hover { color: #6B7280; }
.eye-btn svg { width: 20px; height: 20px; }

.remember-row { display: flex; justify-content: flex-end; margin: 20px 0 26px; }
.remember { display: inline-flex; align-items: center; gap: 8px; cursor: pointer; color: #2E7CF6; font-size: 16px; }
.remember input { width: 20px; height: 20px; accent-color: #2E7CF6; cursor: pointer; }

.reg-btn { margin-top: 30px; }
.login-btn { width: 100%; height: 56px; border-radius: 6px; border: 0; cursor: pointer; background: #3B82F6; color: #fff; font-size: 18px; font-weight: 500; letter-spacing: 4px; text-indent: 4px; transition: background .15s; }
.login-btn:hover { background: #2E7CF6; }
.login-btn:disabled { background: #A9B7FE; cursor: not-allowed; }
.login-err { min-height: 20px; font-size: 13px; color: #E34D59; margin-top: 10px; text-align: center; }

.card-foot { margin-top: 18px; padding-top: 20px; border-top: 1px solid #EDEFF2; text-align: center; font-size: 15px; color: #9CA3AF; }
.card-foot b { color: #4B5563; font-weight: 600; }

.login-foot { padding: 20px 20px 26px; text-align: center; font-size: 12.5px; color: #A3A9B3; }

@media (max-width: 720px) {
  .login-main { padding: 30px 14px 24px; }
  .login-card { padding: 30px 22px 18px; }
  .brand-row h1 { font-size: 23px; }
  .brand-sub { font-size: 14px; }
  .ltab { font-size: 15.5px; }
}
</style>
