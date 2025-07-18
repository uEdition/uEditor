import { getContext } from "svelte";
import { writable, type Writable, type Readable } from "svelte/store";
import { type CreateQueryResult } from "@tanstack/svelte-query";

import { setApplicationParameter } from "./util";

export const currentFile = writable(null as FileTreeEntry | null);
export const currentFileContent = writable(null as string | null);
export const currentFileModified = writable(false);

currentFile.subscribe((currentFile) => {
  if (currentFile !== null) {
    setApplicationParameter("path", currentFile.fullpath);
  }
});

export function useApiStatus() {
  return getContext("apiStatus") as CreateQueryResult<APIStatus>;
}

export function useCurrentUser() {
  return getContext("currentUser") as CreateQueryResult<CurrentUser>;
}

export function useUEditorConfig() {
  return getContext("uEditorConfig") as CreateQueryResult<UEditorSettings>;
}

export function useCurrentBranch() {
  return getContext("currentBranch") as Writable<Branch | null>;
}

export function useBranches() {
  return getContext("branches") as CreateQueryResult<"Branches">;
}

export function useAuthStatus() {
  return getContext("authStatus") as Readable<"authenticating" | "authenticated" | "error" | "pending">;
}

export function useHasLoggedOut() {
  return getContext("hasLoggedOut") as Writable<boolean>;
}

export function useConfiguredTEIBlocks() {
  return getContext("configuredTEIBlocks") as Readable<UEditorTEINode[]>;
}
export function useConfiguredTEIMarks() {
  return getContext("configuredTEIMarks") as Readable<UEditorTEINode[]>;
}
