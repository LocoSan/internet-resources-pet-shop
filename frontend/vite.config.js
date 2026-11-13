import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const proxy = { '/api': process.env.PET_SHOP_API || 'http://127.0.0.1:8000' }

export default defineConfig({
  plugins: [vue()],
  server: { proxy },
  preview: { proxy },
})
