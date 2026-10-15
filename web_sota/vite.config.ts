import { defineConfig } from "vite";

export default defineConfig({
	server: {
		port: 11245,
		host: "127.0.0.1",
		proxy: {
			"/api": "http://127.0.0.1:11246",
			"/mcp": "http://127.0.0.1:11246",
		},
	},
	preview: { port: 11245, host: "127.0.0.1" },
});
