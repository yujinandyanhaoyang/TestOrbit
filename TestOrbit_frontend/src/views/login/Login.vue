<template>
  <div class="login-container">
    <!-- 背景装饰 -->
    <div class="background-decoration">
      <div class="floating-orb orb-1"></div>
      <div class="floating-orb orb-2"></div>
      <div class="floating-orb orb-3"></div>
      <div class="gradient-mesh"></div>
    </div>

    <!-- 主登录卡片 -->
    <div class="login-card" :class="{ 'shake': isShaking }">
      <!-- 品牌标识区域 -->
      <div class="brand-section">
        <div class="logo-container">
          <div class="logo-icon">
            <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#667eea"/>
                  <stop offset="50%" stop-color="#764ba2"/>
                  <stop offset="100%" stop-color="#f093fb"/>
                </linearGradient>
              </defs>
              <circle cx="50" cy="50" r="45" fill="url(#logoGradient)" opacity="0.1"/>
              <path d="M30 35 L70 50 L30 65 Z" fill="url(#logoGradient)" opacity="0.8"/>
              <circle cx="50" cy="50" r="4" fill="url(#logoGradient)"/>
              <path d="M50 25 Q65 40 50 50 Q35 60 50 75" stroke="url(#logoGradient)" stroke-width="2" fill="none" opacity="0.6"/>
            </svg>
          </div>
        </div>
        <h1 class="brand-title">TestOrbit</h1>
        <p class="brand-subtitle">专业API测试平台</p>
      </div>

      <!-- 登录表单区域 -->
      <div class="form-section">
        <div class="form-header">
          <h2 class="form-title">欢迎回来</h2>
          <p class="form-description">请登录您的账户以继续使用</p>
        </div>

        <form @submit.prevent="Login" class="login-form">
          <!-- 用户名输入框 -->
          <div class="input-group">
            <div class="input-wrapper" :class="{ 
              'focused': focusedField === 'username', 
              'filled': userInfo.username,
              'has-value': userInfo.username && userInfo.username.length > 0
            }">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <input
                v-model="userInfo.username"
                type="text"
                class="form-input"
                @focus="focusedField = 'username'"
                @blur="focusedField = ''"
                required
              />
              <label class="floating-label"></label>
            </div>
          </div>

          <!-- 密码输入框 -->
          <div class="input-group">
            <div class="input-wrapper" :class="{ 
              'focused': focusedField === 'password', 
              'filled': userInfo.password,
              'has-value': userInfo.password && userInfo.password.length > 0
            }">
              <div class="input-icon">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                  <circle cx="12" cy="16" r="1" fill="currentColor"/>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
              <input
                v-model="userInfo.password"
                :type="showPassword ? 'text' : 'password'"
                class="form-input"
                @focus="focusedField = 'password'"
                @blur="focusedField = ''"
                required
              />
              <label class="floating-label"></label>
              <button
                type="button"
                class="password-toggle"
                @click="showPassword = !showPassword"
              >
                <svg v-if="showPassword" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" stroke="currentColor" stroke-width="2"/>
                  <line x1="1" y1="1" x2="23" y2="23" stroke="currentColor" stroke-width="2"/>
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 记住我和忘记密码 -->
          <div class="form-options">
            <label class="checkbox-wrapper">
              <input type="checkbox" v-model="rememberMe" class="checkbox-input">
              <span class="checkmark"></span>
              <span class="checkbox-label">记住我</span>
            </label>
            <button type="button" class="forgot-password" @click="handleForgotPassword">
              忘记密码？
            </button>
          </div>

          <!-- 登录按钮 -->
          <button 
            type="submit" 
            class="login-button" 
            :class="{ 'loading': isLoading }"
            :disabled="isLoading"
          >
            <div class="button-content">
              <div v-if="isLoading" class="loading-spinner"></div>
              <svg v-else class="button-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="button-text">{{ isLoading ? '登录中...' : '登录' }}</span>
            </div>
          </button>

        </form>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="login-footer">
      <p>&copy; 2025 TestOrbit. 致力于为开发者提供最优质的API测试体验.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import useUserStore from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

// 表单数据
const userInfo = ref({
  username: 'admin',
  password: 'admin'
})

// UI状态管理
const focusedField = ref('')
const showPassword = ref(false)
const rememberMe = ref(false)
const isLoading = ref(false)
const isShaking = ref(false)

// 表单验证和提交
const Login = async () => {
  if (!userInfo.value.username || !userInfo.value.password) {
    triggerShake()
    ElMessage.warning('用户名和密码不能为空')
    return
  }

  isLoading.value = true

  try {
    // 模拟加载时间，让用户看到优雅的加载动画
    await new Promise(resolve => setTimeout(resolve, 800))
    
    const success = await userStore.login(userInfo.value.username, userInfo.value.password)
    
    if (success) {
      // 成功动画
      ElMessage.success({
        message: '登录成功！欢迎回来',
        duration: 2000,
        showClose: true
      })
      
      // 延迟跳转，让用户看到成功提示
      setTimeout(() => {
        router.push('/home')
      }, 1000)
    } else {
      triggerShake()
    }
  } catch (error) {
    triggerShake()
    ElMessage.error('登录请求失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}

// 震动效果
const triggerShake = () => {
  isShaking.value = true
  setTimeout(() => {
    isShaking.value = false
  }, 600)
}

// 忘记密码处理
const handleForgotPassword = () => {
  ElMessage.info({
    message: '忘记密码功能正在开发中，请联系管理员',
    duration: 3000,
    showClose: true
  })
}

// 第三方登录处理
const handleSocialLogin = (provider: string) => {
  ElMessage.info({
    message: `${provider === 'google' ? 'Google' : 'GitHub'} 登录功能正在开发中`,
    duration: 3000,
    showClose: true
  })
}

// 键盘事件处理
const handleKeyPress = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !isLoading.value) {
    Login()
  }
}

// 组件挂载时添加键盘监听
import { onMounted, onUnmounted } from 'vue'

onMounted(() => {
  document.addEventListener('keypress', handleKeyPress)
})

onUnmounted(() => {
  document.removeEventListener('keypress', handleKeyPress)
})
</script>

<style scoped lang="scss">
// 全局变量和混合器
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  --surface-glass: rgba(255, 255, 255, 0.9);
  --surface-glass-dark: rgba(255, 255, 255, 0.05);
  --text-primary: #1a1a1a;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --border-light: rgba(255, 255, 255, 0.2);
  --shadow-soft: 0 8px 32px rgba(0, 0, 0, 0.1);
  --shadow-strong: 0 20px 60px rgba(0, 0, 0, 0.2);
  --border-radius-lg: 24px;
  --border-radius-md: 16px;
  --border-radius-sm: 12px;
}

.login-container {
  width: 100vw;
  height: 100vh;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  
  // 动态背景
  background: linear-gradient(135deg, 
    #667eea 0%, 
    #764ba2 25%, 
    #f093fb 50%, 
    #f5576c 75%, 
    #4facfe 100%
  );
  background-size: 400% 400%;
  animation: gradientShift 15s ease infinite;

  // 背景装饰
  .background-decoration {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 1;

    .floating-orb {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      animation: floatOrb 20s ease-in-out infinite;

      &.orb-1 {
        width: 300px;
        height: 300px;
        top: -150px;
        right: -150px;
        animation-delay: 0s;
      }

      &.orb-2 {
        width: 200px;
        height: 200px;
        bottom: -100px;
        left: -100px;
        animation-delay: -7s;
      }

      &.orb-3 {
        width: 150px;
        height: 150px;
        top: 50%;
        left: -75px;
        animation-delay: -14s;
      }
    }

    .gradient-mesh {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: 
        radial-gradient(circle at 20% 50%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
        radial-gradient(circle at 40% 80%, rgba(120, 219, 255, 0.3) 0%, transparent 50%);
      animation: meshMove 25s ease infinite;
    }
  }

  // 主登录卡片
  .login-card {
    position: relative;
    z-index: 10;
    width: 100%;
    max-width: 480px;
    background: var(--surface-glass);
    backdrop-filter: blur(20px);
    border-radius: var(--border-radius-lg);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-strong);
    padding: 48px;
    transition: all 0.4s cubic-bezier(0.4, 0.0, 0.2, 1);

    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 32px 80px rgba(0, 0, 0, 0.25);
    }

    &.shake {
      animation: shakeAnimation 0.6s cubic-bezier(0.36, 0.07, 0.19, 0.97);
    }

    // 品牌区域
    .brand-section {
      text-align: center;
      margin-bottom: 40px;

      .logo-container {
        display: flex;
        justify-content: center;
        margin-bottom: 24px;

        .logo-icon {
          width: 80px;
          height: 80px;
          transition: transform 0.3s ease;

          &:hover {
            transform: scale(1.05) rotate(5deg);
          }

          svg {
            width: 100%;
            height: 100%;
            filter: drop-shadow(0 4px 12px rgba(102, 126, 234, 0.3));
          }
        }
      }

      .brand-title {
        font-size: 32px;
        font-weight: 800;
        margin: 0 0 8px 0;
        background: var(--primary-gradient);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.02em;
      }

      .brand-subtitle {
        font-size: 16px;
        color: var(--text-secondary);
        margin: 0;
        font-weight: 500;
      }
    }

    // 表单区域
    .form-section {
      .form-header {
        text-align: center;
        margin-bottom: 32px;

        .form-title {
          font-size: 24px;
          font-weight: 700;
          color: var(--text-primary);
          margin: 0 0 8px 0;
          letter-spacing: -0.01em;
        }

        .form-description {
          font-size: 15px;
          color: var(--text-secondary);
          margin: 0;
          font-weight: 400;
        }
      }

      .login-form {
        .input-group {
          margin-bottom: 24px;

          .input-wrapper {
            position: relative;
            background: rgba(255, 255, 255, 0.6);
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: var(--border-radius-md);
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
            overflow: hidden;

            &:hover {
              border-color: rgba(102, 126, 234, 0.4);
              background: rgba(255, 255, 255, 0.8);
            }

            &.focused {
              border-color: #667eea;
              background: rgba(255, 255, 255, 0.95);
              box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
              transform: translateY(-2px);

              .floating-label {
                transform: translateY(-12px) translateX(-4px) scale(0.85);
                color: #667eea;
                font-weight: 600;
              }

              .input-icon {
                color: #667eea;
                transform: scale(1.05);
              }
            }

            &.filled .floating-label {
              transform: translateY(-12px) translateX(-4px) scale(0.85);
              color: var(--text-secondary);
            }

            &.has-value .floating-label {
              transform: translateY(-12px) translateX(-4px) scale(0.85);
              color: var(--text-secondary);
            }

            .input-icon {
              position: absolute;
              left: 16px;
              top: 50%;
              transform: translateY(-50%);
              width: 20px;
              height: 20px;
              color: var(--text-muted);
              transition: all 0.3s ease;
              z-index: 2;
            }

            .form-input {
              width: 100%;
              height: 56px;
              padding: 16px 16px 16px 52px;
              border: none;
              background: transparent;
              font-size: 16px;
              color: var(--text-primary);
              outline: none;
              font-weight: 500;
              transition: all 0.3s ease;

              &::placeholder {
                color: transparent;
                opacity: 0;
              }

              &:focus::placeholder {
                color: transparent;
                opacity: 0;
              }

              &:not(:placeholder-shown) + .floating-label {
                transform: translateY(-12px) translateX(-4px) scale(0.85);
                color: var(--text-secondary);
              }
            }

            .floating-label {
              position: absolute;
              left: 52px;
              top: 50%;
              transform: translateY(-50%);
              font-size: 16px;
              color: var(--text-muted);
              pointer-events: none;
              transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
              font-weight: 500;
              z-index: 1;
            }

            .password-toggle {
              position: absolute;
              right: 16px;
              top: 50%;
              transform: translateY(-50%);
              width: 24px;
              height: 24px;
              border: none;
              background: none;
              color: var(--text-muted);
              cursor: pointer;
              transition: all 0.2s ease;
              display: flex;
              align-items: center;
              justify-content: center;
              border-radius: 6px;

              &:hover {
                color: var(--text-primary);
                background: rgba(0, 0, 0, 0.05);
              }

              svg {
                width: 18px;
                height: 18px;
              }
            }
          }
        }

        .form-options {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 32px;

          .checkbox-wrapper {
            display: flex;
            align-items: center;
            cursor: pointer;
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 500;

            .checkbox-input {
              position: absolute;
              opacity: 0;
              cursor: pointer;

              &:checked + .checkmark {
                background: var(--primary-gradient);
                border-color: #667eea;

                &::after {
                  opacity: 1;
                  transform: rotate(45deg) scale(1);
                }
              }
            }

            .checkmark {
              width: 20px;
              height: 20px;
              border: 2px solid #d1d5db;
              border-radius: 6px;
              margin-right: 12px;
              position: relative;
              transition: all 0.2s ease;
              flex-shrink: 0;

              &::after {
                content: '';
                position: absolute;
                left: 5px;
                top: 1px;
                width: 6px;
                height: 10px;
                border: solid white;
                border-width: 0 2px 2px 0;
                opacity: 0;
                transform: rotate(45deg) scale(0.8);
                transition: all 0.2s ease;
              }
            }

            .checkbox-label {
              user-select: none;
            }

            &:hover .checkmark {
              border-color: #667eea;
            }
          }

          .forgot-password {
            background: none;
            border: none;
            color: #667eea;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s ease;
            padding: 4px 0;
            border-radius: 4px;

            &:hover {
              color: #5a67d8;
              text-decoration: underline;
            }
          }
        }

        .login-button {
          width: 100%;
          height: 56px;
          background: rgba(255, 255, 255, 0.95);
          border: 2px solid rgba(102, 126, 234, 0.3);
          border-radius: var(--border-radius-md);
          color: #667eea;
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
          position: relative;
          overflow: hidden;
          margin-bottom: 24px;
          backdrop-filter: blur(10px);
          box-shadow: 
            0 4px 20px rgba(102, 126, 234, 0.15),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, 
              transparent, 
              rgba(102, 126, 234, 0.1), 
              transparent
            );
            transition: left 0.6s ease;
          }

          &:hover:not(:disabled) {
            background: rgba(102, 126, 234, 0.05);
            border-color: #667eea;
            color: #5a67d8;
            transform: translateY(-2px);
            box-shadow: 
              0 12px 40px rgba(102, 126, 234, 0.25),
              inset 0 1px 0 rgba(255, 255, 255, 0.9);

            &::before {
              left: 100%;
            }
          }

          &:active:not(:disabled) {
            transform: translateY(0);
            background: rgba(102, 126, 234, 0.1);
          }

          &:disabled {
            cursor: not-allowed;
            opacity: 0.6;
            background: rgba(255, 255, 255, 0.5);
            border-color: rgba(102, 126, 234, 0.2);
            color: rgba(102, 126, 234, 0.5);
          }

          &.loading {
            pointer-events: none;
            background: rgba(102, 126, 234, 0.08);
            border-color: rgba(102, 126, 234, 0.4);

            .button-content {
              opacity: 0.9;
            }
          }

          .button-content {
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            position: relative;
            z-index: 1;

            .button-icon {
              width: 18px;
              height: 18px;
              margin-right: 8px;
              filter: drop-shadow(0 1px 2px rgba(102, 126, 234, 0.2));
            }

            .button-text {
              font-weight: 600;
              letter-spacing: 0.01em;
              text-shadow: 0 1px 2px rgba(102, 126, 234, 0.1);
            }

            .loading-spinner {
              width: 20px;
              height: 20px;
              border: 2px solid rgba(102, 126, 234, 0.3);
              border-radius: 50%;
              border-top-color: #667eea;
              animation: spin 1s ease-in-out infinite;
              margin-right: 8px;
            }
          }
        }

        .divider {
          position: relative;
          text-align: center;
          margin: 32px 0;

          &::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 1px;
            background: rgba(0, 0, 0, 0.1);
          }

          .divider-text {
            background: var(--surface-glass);
            padding: 0 16px;
            font-size: 14px;
            color: var(--text-muted);
            font-weight: 500;
          }
        }

        .social-login {
          display: flex;
          gap: 12px;

          .social-button {
            flex: 1;
            height: 48px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            background: rgba(255, 255, 255, 0.6);
            border-radius: var(--border-radius-sm);
            color: var(--text-primary);
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);

            .social-icon {
              width: 20px;
              height: 20px;
            }

            &:hover {
              background: rgba(255, 255, 255, 0.9);
              border-color: rgba(102, 126, 234, 0.3);
              transform: translateY(-1px);
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }

            &.google:hover {
              border-color: #4285f4;
            }

            &.github:hover {
              border-color: #333;
            }
          }
        }
      }
    }
  }

  // 页脚
  .login-footer {
    position: absolute;
    bottom: 20px;
    text-align: center;
    z-index: 10;

    p {
      margin: 0;
      font-size: 13px;
      color: rgba(255, 255, 255, 0.8);
      font-weight: 500;
    }
  }
}

// 动画定义
@keyframes gradientShift {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

@keyframes floatOrb {
  0%, 100% {
    transform: translate(0px, 0px) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

@keyframes meshMove {
  0%, 100% {
    transform: rotate(0deg) scale(1);
  }
  50% {
    transform: rotate(180deg) scale(1.1);
  }
}

@keyframes shakeAnimation {
  0%, 100% {
    transform: translateX(0);
  }
  10%, 30%, 50%, 70%, 90% {
    transform: translateX(-8px);
  }
  20%, 40%, 60%, 80% {
    transform: translateX(8px);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media (max-width: 640px) {
  .login-container {
    padding: 20px;

    .login-card {
      padding: 32px 24px;
      max-width: calc(100vw - 40px);
      margin: 0;

      .brand-section {
        margin-bottom: 32px;

        .brand-title {
          font-size: 28px;
        }

        .logo-icon {
          width: 64px;
          height: 64px;
        }
      }

      .form-section {
        .form-header {
          margin-bottom: 24px;

          .form-title {
            font-size: 20px;
          }
        }

        .login-form {
          .input-group {
            margin-bottom: 20px;

            .input-wrapper .form-input {
              height: 52px;
            }
          }

          .social-login {
            flex-direction: column;
            gap: 8px;
          }
        }
      }
    }

    .login-footer {
      position: relative;
      margin-top: 24px;
      bottom: auto;
    }
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 16px;
    
    .login-card {
      padding: 24px 16px;
      max-width: calc(100vw - 32px);

      .form-section .login-form .form-options {
        flex-direction: column;
        gap: 16px;
        align-items: flex-start;
      }
    }
  }
}

// Dark mode support (for future implementation)
@media (prefers-color-scheme: dark) {
  :root {
    --surface-glass: rgba(0, 0, 0, 0.8);
    --text-primary: #f9fafb;
    --text-secondary: #d1d5db;
    --text-muted: #9ca3af;
    --border-light: rgba(255, 255, 255, 0.1);
  }
}

// 提升可访问性
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
