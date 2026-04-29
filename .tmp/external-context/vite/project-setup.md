---
source: Official Docs (vitejs.dev)
library: React with Vite
package: vite
topic: project setup, build tool, patterns
fetched: 2026-04-29
official_docs: https://vitejs.dev/guide/
---

# Vite Documentation

## Overview

Vite is a build tool that aims to provide a faster and leaner development experience for modern web projects. It consists of two major parts:

- **Dev server** with rich feature enhancements over native ES modules, including extremely fast Hot Module Replacement (HMR)
- **Build command** that bundles code with Rollup, pre-configured to output highly optimized static assets for production

## Browser Support

During development, Vite assumes modern browsers that support ES modules. Vite sets `esnext` as the transform target to serve modules as close as possible to the original source code.

For production builds, Vite targets "Baseline Widely Available" browsers (released at least 2.5 years ago).

## Scaffolding Your First Vite Project

### Using npm create vite

```bash
$ npm create vite@latest
```

Then follow the prompts!

### Command Line Options

```bash
# npm 7+, extra double-dash is needed:
$ npm create vite@latest my-react-app -- --template react

# yarn
$ yarn create vite my-react-app --template react

# pnpm
$ pnpm create vite my-react-app --template react
```

Supported templates: `vanilla`, `vanilla-ts`, `vue`, `vue-ts`, `react`, `react-ts`, `preact`, `preact-ts`, `lit`, `lit-ts`, `svelte`, `svelte-ts`, `solid`, `solid-ts`, `qwik`, `qwik-ts`

### Online Templates

You can try Vite online on StackBlitz: `https://vite.new/react`

## Manual Installation

```bash
$ npm install -D vite
```

Create an `index.html` file:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite + React</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

Then run:

```bash
$ npx vite
```

The app will be served on `http://localhost:5173`.

## index.html and Project Root

In a Vite project, `index.html` is front-and-central instead of being tucked away inside `public`. This is intentional: during development Vite is a server, and `index.html` is the entry point to your application.

Vite treats `index.html` as source code and part of the module graph. It resolves `<script type="module" src="...">` that references your JavaScript source code.

Vite has the concept of a "root directory" which your files are served from. Absolute URLs in your source code will be resolved using the project root as base.

## Command Line Interface

In a project where Vite is installed, you can use the `vite` binary in npm scripts:

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }
}
```

### Common CLI Options

- `--port` - Specify port
- `--open` - Open browser on start
- `--host` - Expose to network

## Project Structure

Typical Vite + React project structure:

```
my-vite-app/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.jsx          # Entry point
│   ├── App.jsx           # Main component
│   ├── App.css          # Styles
│   └── assets/          # Static assets
├── public/               # Static files (copied to dist)
└── node_modules/
```

## Configuration

### vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  }
})
```

## Environment Variables

Vite uses `.env` files for environment variables:

```
# .env
VITE_API_URL=http://localhost:8000
```

Access in code:

```javascript
const apiUrl = import.meta.env.VITE_API_URL
```

### Available Env Files

- `.env` - Loaded in all cases
- `.env.local` - Local overrides (ignored by git)
- `.env.[mode]` - Mode-specific (`.env.development`, `.env.production`)
- `.env.[mode].local` - Mode-specific local overrides

## Features

### Hot Module Replacement (HMR)

Vite provides instant HMR. When you edit a file, only that module is updated, not the entire page.

### Dependency Pre-Bundling

Vite automatically pre-bundles dependencies using esbuild. This:
- Converts CommonJS to ESM
- Bundles multiple modules into one
- Reduces the number of requests

### Static Asset Handling

- Importing an asset returns the public URL
- CSS can be imported from JS files
- JSON can be imported directly

### Building for Production

```bash
$ npm run build
```

This generates optimized assets in the `dist` folder.

### Preview Production Build

```bash
$ npm run preview
```

## React Integration

### Using @vitejs/plugin-react

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
})
```

### JSX/TSX Support

With the React plugin, Vite supports:
- JSX/TSX out of the box
- Fast Refresh for React components
- Automatic JSX runtime

### Fast Refresh

Vite's Fast Refresh preserves component state while updating code. Works with:
- React components
- Hooks
- Context (with some limitations)

## Backend Integration

### Proxying API Requests

```javascript
// vite.config.js
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

### CORS Configuration

For development, configure your FastAPI backend to allow CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Key Commands Summary

| Command | Description |
|---------|-------------|
| `npm create vite@latest` | Scaffold new project |
| `npm run dev` | Start dev server |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build |
| `npx vite` | Run Vite directly |