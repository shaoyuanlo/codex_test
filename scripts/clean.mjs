import { rm } from "node:fs/promises";

// Rebuild generated output from scratch so deleted pages and assets disappear.
await rm(new URL("../_site/", import.meta.url), { recursive: true, force: true });
