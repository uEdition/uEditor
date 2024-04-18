import { writable } from "svelte/store";

export const currentFile = writable(null as FileTreeEntry | null);
