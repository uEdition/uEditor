import { writable } from "svelte/store";

import { setApplicationParameter } from "./util";

export const currentBranch = writable("-1");
export const currentFile = writable(null as FileTreeEntry | null);
export const currentFileContent = writable(null as string | null);
export const currentFileModified = writable(false);

currentFile.subscribe((currentFile) => {
  if(currentFile !== null) {
    setApplicationParameter("path", currentFile.fullpath);
  }
});
