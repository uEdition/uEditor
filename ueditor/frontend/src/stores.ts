import { writable } from "svelte/store";

export const currentBranch = writable("-1");
export const currentFile = writable(null as FileTreeEntry | null);
export const currentFileContent = writable(null as string | null);
export const currentFileModified = writable(false);
