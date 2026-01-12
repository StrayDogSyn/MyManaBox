# Tailwind CSS v4 Configuration Fix Plan

I have confirmed that the project is using **Tailwind CSS v4.1.18**, but the current configuration files (`postcss.config.js`, `tailwind.config.js`, `index.css`) are using **v3 patterns**. This mismatch causes the PostCSS plugin error.

I will execute the **IMMEDIATE RESOLUTION** steps as outlined in your guide to migrate to the correct v4 configuration.

## Task 1.2: Resolve Tailwind CSS Configuration

### 1. Verify State
- **Current Version**: Checked `package.json`, confirmed `tailwindcss` and `@tailwindcss/postcss` are version `^4.1.18`.
- **Current Config**: `postcss.config.js` is incorrectly using `tailwindcss` plugin instead of `@tailwindcss/postcss`.

### 2. Implementation Steps
1.  **Stop Server**: Terminate the running `npm run dev` process to apply changes safely.
2.  **Update PostCSS Config**: Rewrite `web/postcss.config.js` to use the v4 plugin.
    ```javascript
    export default {
      plugins: {
        '@tailwindcss/postcss': {},
      },
    }
    ```
3.  **Migrate to CSS-First Config**: Rewrite `web/src/index.css` to replace `@tailwind` directives with `@import "tailwindcss";` and move theme variables into the `@theme` block.
    *   This replaces the need for `tailwind.config.js`.
4.  **Remove Legacy Config**: Delete `web/tailwind.config.js` as it is superseded by the CSS configuration in v4.

### 3. Verification
- Run `npm run dev` and confirm the server starts without the PostCSS error.
- Verify the web interface loads with the correct dark theme colors (checking if variables like `--color-bg-primary` are being applied).

### 4. Rollback Plan
- If v4 configuration fails to stabilize, I will downgrade to Tailwind v3 as a fallback:
  `npm uninstall tailwindcss @tailwindcss/postcss`
  `npm install tailwindcss@3.4.17 postcss autoprefixer --save-dev`
