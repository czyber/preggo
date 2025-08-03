# Frontend - Nuxt 3 Boilerplate

This is a Nuxt 3 frontend boilerplate with the following features:

## Technologies Used

- **Nuxt 3**: The Intuitive Vue Framework
- **Vue 3**: Progressive JavaScript Framework
- **TypeScript**: Static type checking
- **Pinia**: State Management for Vue.js
- **Tailwind CSS**: Utility-first CSS framework
- **openapi-fetch**: Type-safe API client
- **openapi-typescript**: Generate TypeScript types from OpenAPI schemas

## Project Structure

```
frontend/
├── assets/
│   └── css/                 # Global styles
├── components/              # Vue components
├── composables/             # Vue composables
│   └── useApi.ts           # API client composable
├── layouts/                 # Nuxt layouts
│   └── default.vue         # Default layout
├── pages/                   # File-based routing
│   ├── index.vue           # Home page
│   └── items.vue           # Items demo page
├── plugins/                 # Nuxt plugins
├── stores/                  # Pinia stores
│   └── items.ts            # Items store
├── types/                   # TypeScript types
│   └── api.ts              # Auto-generated API types
├── app.vue                 # Root component
├── nuxt.config.ts          # Nuxt configuration
├── package.json            # Dependencies and scripts
├── tailwind.config.js      # Tailwind configuration
└── tsconfig.json           # TypeScript configuration
```

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Generate API types (after backend is running):**
   ```bash
   npm run generate-types
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000

## Development

### API Integration

The frontend uses a type-safe API client generated from the backend's OpenAPI schema:

1. **Generate types from OpenAPI schema:**
   ```bash
   npm run generate-types
   ```

2. **Use the API client in components:**
   ```typescript
   const api = useApi()
   const { data, error } = await api.getItems()
   ```

### State Management

Pinia is used for state management. Example store structure:

```typescript
// stores/items.ts
import { defineStore } from 'pinia'
import type { components } from '~/types/api'

type Item = components['schemas']['ItemRead']

export const useItemsStore = defineStore('items', {
  state: () => ({
    items: [] as Item[],
    loading: false,
    error: null as string | null,
  }),

  actions: {
    async fetchItems() {
      // Implementation
    }
  }
})
```

### Adding New Pages

1. **Create a new page in `pages/`:**
   ```vue
   <!-- pages/your-page.vue -->
   <template>
     <div>
       <h1>Your Page</h1>
     </div>
   </template>
   ```

2. **The page will be automatically routed to `/your-page`**

### Adding New Components

1. **Create a component in `components/`:**
   ```vue
   <!-- components/YourComponent.vue -->
   <template>
     <div>
       <!-- Component content -->
     </div>
   </template>
   ```

2. **Use it in pages or other components:**
   ```vue
   <template>
     <YourComponent />
   </template>
   ```

### Environment Configuration

Configuration is managed through `nuxt.config.ts` with runtime config:

```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'
    }
  }
})
```

You can override settings using environment variables:

```bash
NUXT_PUBLIC_API_BASE=https://api.example.com/v1 npm run dev
```

## Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run generate` - Generate static site
- `npm run preview` - Preview production build
- `npm run generate-types` - Generate TypeScript types from OpenAPI schema

## Features

- **Type Safety**: Full TypeScript support with auto-generated API types
- **State Management**: Pinia for reactive state management
- **Styling**: Tailwind CSS for rapid UI development
- **API Integration**: Type-safe API client with automatic error handling
- **File-based Routing**: Automatic routing based on file structure
- **Server-Side Rendering**: Built-in SSR support with Nuxt 3
- **Hot Module Replacement**: Fast development with hot reloading

## Development Tips

1. **Always generate types after backend changes:**
   ```bash
   npm run generate-types
   ```

2. **Use the useApi composable for all API calls:**
   ```typescript
   const api = useApi()
   const { data, error } = await api.getItems()
   ```

3. **Create reusable composables for common logic:**
   ```typescript
   // composables/useItems.ts
   export const useItems = () => {
     const store = useItemsStore()
     
     const fetchItems = async () => {
       await store.fetchItems()
     }
     
     return {
       items: computed(() => store.items),
       loading: computed(() => store.loading),
       fetchItems
     }
   }
   ```

4. **Use Pinia stores for complex state management:**
   ```typescript
   const store = useItemsStore()
   ```