import { rm } from "node:fs/promises";

// Rebuild generated output from scratch so unpublished/deleted posts disappear.
await rm(new URL("../_site/", import.meta.url), { recursive: true, force: true });
