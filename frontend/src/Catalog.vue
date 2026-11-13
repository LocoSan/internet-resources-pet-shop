<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, notice, signedIn } from './api'

const route = useRoute()
const router = useRouter()
const titles = { pets: 'Животные', breeds: 'Породы', species: 'Виды' }
const section = computed(() => route.params.section)
const title = computed(() => titles[section.value])
const endpoint = computed(() => '/api/' + section.value + '/')
const page = computed(() => Math.max(1, Number(route.query.page) || 1))
const editing = computed(() => route.name === 'new' || route.name === 'edit')
const result = ref(null)
const record = ref(null)
const options = ref([])
const form = ref({})
const loading = ref(true)
const busy = ref(false)
const error = ref('')

function location(name, id, query) {
  return { name, params: { section: section.value, ...(id ? { id } : {}) }, query }
}

function showError(exception) {
  if (!signedIn()) {
    router.replace({ name: 'login', query: { next: route.fullPath } })
  } else {
    error.value = exception.message
  }
}

async function readOptions(path) {
  const records = []
  while (path) {
    const response = await api(path)
    records.push(...response.results)
    const next = response.next ? new URL(response.next) : null
    path = next ? next.pathname + next.search : null
  }
  return records
}

watch(() => route.fullPath, async (_, __, onCleanup) => {
  if (!route.meta.private) return
  let current = true
  onCleanup(() => { current = false })
  const url = endpoint.value
  const mode = route.name
  const id = route.params.id
  loading.value = true
  error.value = ''
  result.value = null
  record.value = null
  options.value = []
  form.value = {}
  try {
    if (mode === 'list') {
      const data = await api(url + '?page=' + page.value)
      if (current) result.value = data
    } else {
      const data = id ? await api(url + id + '/') : null
      const related = mode !== 'detail' && section.value !== 'species'
        ? await readOptions(section.value === 'pets' ? '/api/breeds/' : '/api/species/')
        : []
      if (current) {
        record.value = data
        options.value = related
        form.value = data ? { ...data } : { name: '', description: '', breed: '', species: '' }
      }
    }
  } catch (exception) {
    if (current) showError(exception)
  } finally {
    if (current) loading.value = false
  }
}, { immediate: true })

async function save() {
  error.value = ''
  notice.value = ''
  const data = { name: form.value.name.trim() }
  if (!data.name) {
    error.value = 'Введите название или имя.'
    return
  }
  if (section.value === 'breeds') data.species = form.value.species
  if (section.value === 'pets') {
    data.breed = form.value.breed
    data.age_months = form.value.age_months
    data.price = form.value.price
    data.description = form.value.description
  }
  const id = route.params.id
  const start = route.fullPath
  busy.value = true
  try {
    const saved = await api(id ? endpoint.value + id + '/' : endpoint.value, id ? 'PATCH' : 'POST', data)
    if (route.fullPath === start) {
      notice.value = id ? 'Запись обновлена.' : 'Запись добавлена.'
      await router.push(location('detail', saved.id))
    }
  } catch (exception) {
    if (route.fullPath === start) showError(exception)
  } finally {
    busy.value = false
  }
}

async function remove() {
  if (!window.confirm('Удалить запись «' + record.value.name + '»?')) return
  error.value = ''
  notice.value = ''
  const start = route.fullPath
  busy.value = true
  try {
    await api(endpoint.value + record.value.id + '/', 'DELETE')
    if (route.fullPath === start) {
      notice.value = 'Запись удалена.'
      await router.push(location('list'))
    }
  } catch (exception) {
    if (route.fullPath === start) showError(exception)
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <section class="panel">
    <h1 v-if="route.name === 'list'">{{ title }}</h1>
    <h1 v-else-if="editing">{{ route.name === 'new' ? 'Новая запись' : 'Редактирование' }} · {{ title }}</h1>
    <h1 v-else>{{ record?.name || title }}</h1>

    <p v-if="loading" role="status">Загрузка…</p>
    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <template v-if="result">
      <div class="actions">
        <RouterLink class="button" :to="location('new')">Добавить</RouterLink>
        <span>Всего записей: {{ result.count }}</span>
      </div>
      <ul v-if="result.results.length" class="records">
        <li v-for="item in result.results" :key="item.id">
          <RouterLink :to="location('detail', item.id)">{{ item.name }}</RouterLink>
          <span v-if="item.breed_name">{{ item.breed_name }} · {{ item.price }} ₽</span>
          <span v-else-if="item.species_name">{{ item.species_name }}</span>
        </li>
      </ul>
      <p v-else>Записей пока нет.</p>
      <div v-if="result.next || result.previous" class="actions">
        <RouterLink v-if="result.previous" :to="location('list', null, { page: page - 1 })">Предыдущая</RouterLink>
        <span>Страница {{ page }}</span>
        <RouterLink v-if="result.next" :to="location('list', null, { page: page + 1 })">Следующая</RouterLink>
      </div>
    </template>

    <template v-if="record && !editing">
      <dl v-if="section !== 'species'">
        <dt>Вид</dt><dd>{{ record.species_name }}</dd>
        <template v-if="section === 'pets'">
          <dt>Порода</dt><dd>{{ record.breed_name }}</dd>
          <dt>Возраст в месяцах</dt><dd>{{ record.age_months }}</dd>
          <dt>Цена</dt><dd>{{ record.price }} ₽</dd>
          <dt>Описание</dt><dd>{{ record.description || '—' }}</dd>
        </template>
      </dl>
      <div class="actions">
        <RouterLink class="button" :to="location('edit', record.id)">Изменить</RouterLink>
        <button class="danger" type="button" :disabled="busy" @click="remove">Удалить</button>
      </div>
    </template>

    <form v-if="editing && !loading && form.name !== undefined" @submit.prevent="save">
      <label>
        {{ section === 'pets' ? 'Имя' : 'Название' }}
        <input v-model="form.name" maxlength="80" required>
      </label>
      <label v-if="section === 'breeds'">Вид
        <select v-model.number="form.species" required>
          <option value="" disabled>Выберите вид</option>
          <option v-for="item in options" :key="item.id" :value="item.id">{{ item.name }}</option>
        </select>
      </label>
      <template v-if="section === 'pets'">
        <label>Порода
          <select v-model.number="form.breed" required>
            <option value="" disabled>Выберите породу</option>
            <option v-for="item in options" :key="item.id" :value="item.id">{{ item.name }} ({{ item.species_name }})</option>
          </select>
        </label>
        <label>Возраст в месяцах <input v-model.number="form.age_months" type="number" min="0" max="32767" step="1" required></label>
        <label>Цена, ₽ <input v-model="form.price" type="number" min="0" max="9999999.99" step="0.01" required></label>
        <label>Описание <textarea v-model="form.description" maxlength="500" rows="3"></textarea></label>
      </template>
      <p v-if="section !== 'species' && !options.length">Сначала добавьте {{ section === 'pets' ? 'породу' : 'вид' }}.</p>
      <button :disabled="busy || (section !== 'species' && !options.length)">Сохранить</button>
    </form>

    <RouterLink v-if="route.name !== 'list'" class="back" :to="location('list')">К списку</RouterLink>
  </section>
</template>
