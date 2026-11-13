<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { signIn } from './api'

const route = useRoute()
const router = useRouter()
const login = ref('')
const password = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  busy.value = true
  error.value = ''
  try {
    await signIn(login.value.trim(), password.value)
    const next = typeof route.query.next === 'string' ? route.query.next : ''
    await router.replace(next.startsWith('/catalog/') ? next : '/catalog/pets')
  } catch (exception) {
    error.value = exception.message
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="panel login">
    <h1>Вход</h1>
    <p>Войдите, чтобы открыть каталог.</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <form @submit.prevent="submit">
      <label>Логин <input v-model="login" autocomplete="username" required></label>
      <label>Пароль <input v-model="password" type="password" autocomplete="current-password" required></label>
      <button :disabled="busy">Войти</button>
    </form>
  </section>
</template>
