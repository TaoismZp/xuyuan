// Representative schema only. This is deliberately NOT wired into production.
// Tina's own skill recommends Next.js/React/Astro for its strongest visual editing path.
import { defineConfig } from 'tinacms'

export default defineConfig({
  branch: process.env.GITHUB_BRANCH || 'main',
  clientId: process.env.NEXT_PUBLIC_TINA_CLIENT_ID || '',
  token: process.env.TINA_TOKEN || '',
  build: {
    outputFolder: 'admin',
    publicFolder: 'personal-site-v1',
  },
  media: {
    tina: {
      mediaRoot: 'content/media',
      publicFolder: 'personal-site-v1',
    },
  },
  schema: {
    collections: [
      {
        name: 'essay',
        label: '长文',
        path: 'personal-site-v1/content/essays',
        format: 'md',
        fields: [
          { type: 'string', name: 'title', label: '标题', isTitle: true, required: true },
          { type: 'string', name: 'dek', label: '副标题', ui: { component: 'textarea' } },
          { type: 'string', name: 'slug', label: 'Slug', required: true },
          { type: 'datetime', name: 'date', label: '日期', required: true },
          { type: 'string', name: 'tags', label: '标签', list: true },
          { type: 'boolean', name: 'draft', label: '草稿' },
          { type: 'rich-text', name: 'body', label: '正文', isBody: true },
        ],
      },
    ],
  },
})
