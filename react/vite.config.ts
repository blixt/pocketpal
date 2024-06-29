import react from "@vitejs/plugin-react-swc"
import { promises as fs } from "node:fs"
import path from "node:path"
import { defineConfig } from "vite"

export default defineConfig({
    plugins: [
        react(),
        {
            name: "move-html",
            closeBundle: async () => {
                const srcHtmlPath = path.resolve(__dirname, "dist", "index.html")
                const destHtmlDir = path.resolve(__dirname, "dist", "templates")

                await fs.mkdir(destHtmlDir, { recursive: true })
                await fs.rename(srcHtmlPath, path.join(destHtmlDir, "index.html"))
            },
        },
    ],
    build: {
        rollupOptions: {
            input: path.resolve(__dirname, "index.html"),
            output: {
                assetFileNames: "static/[name].[hash].[ext]",
                chunkFileNames: "static/[name].[hash].js",
                entryFileNames: "static/[name].[hash].js",
            },
        },
        outDir: "dist",
        emptyOutDir: true,
        assetsDir: "static",
    },
    publicDir: false,
    base: "./",
})
