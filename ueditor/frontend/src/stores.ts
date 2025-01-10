import { writable } from "svelte/store";

export const currentBranch = writable("-1");
export const currentFile = writable(null as FileTreeEntry | null);
export const currentFileContent = writable(null as string | null);
export const currentFileModified = writable(false);

currentFile.subscribe((currentFile) => {
  if(currentFile !== null) {
    let hash = window.location.hash;
    if (hash.startsWith("#")) {
      hash = hash.substring(1);
    }
    let params = new URLSearchParams(hash);
    params.set("path", currentFile.fullpath);
    window.location.hash = params.toString();
  }
});
