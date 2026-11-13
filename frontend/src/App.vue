<script setup>
import { useRouter } from 'vue-router'
import { notice, signOut, username } from './api'

const router = useRouter()

function logout() {
  signOut()
  router.push({ name: 'login' })
}
</script>

<template>
  <header>
    <div class="header-content">
      <RouterLink class="brand" to="/catalog/pets">Магазин домашних животных</RouterLink>
      <div v-if="username" class="account">
        <span>Вы вошли: {{ username }}</span>
        <button class="secondary" type="button" @click="logout">Выйти</button>
      </div>
    </div>
  </header>
  <main>
    <nav v-if="username" aria-label="Каталог">
      <RouterLink to="/catalog/pets">Животные</RouterLink>
      <RouterLink to="/catalog/species">Виды</RouterLink>
      <RouterLink to="/catalog/breeds">Породы</RouterLink>
    </nav>
    <p v-if="notice" class="notice" role="status">{{ notice }}</p>
    <RouterView />
  </main>
</template>
