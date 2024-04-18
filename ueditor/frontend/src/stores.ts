import { writable } from "svelte/store";

export const currentBranch = writable("-1");
export const currentFile = writable(null as FileTreeEntry | null);
