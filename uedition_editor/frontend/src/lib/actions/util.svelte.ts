import { appState } from "../../state.svelte";

/**
 * Start running a new action.
 *
 * @param action The action to start running
 */
export function runAction(action: Action) {
  action.status = "active";
  appState.actions.push(action);
  let promise: Promise<void> | null = null;
  if (action.action === "LoadTextFile") {
    promise = loadTextFile(action);
  } else if (action.action === "SaveCurrentFile") {
    promise = saveCurrentFile(action);
  } else if (action.action === "SynchroniseBranches") {
    promise = synchroniseBranches(action);
  }
  if (promise !== null) {
    promise.finally(() => {
      appState.actions.splice(appState.actions.indexOf(action), 1);
    });
  }
}

/**
 * Fetch a text file from remote.
 *
 * @param action The action with the details of the text file to load
 */
async function loadTextFile(action: LoadTextFileAction) {
  const response = await window.fetch(
    "/api/branches/" + action.branch.id + "/files/" + action.filename
  );
  action.callback(await response.text());
}

/**
 * Save the current file to the remote.
 *
 * @param action The action with the details of the file to save
 */
async function saveCurrentFile(action: SaveCurrentFileAction) {
  const formData = new FormData();
  formData.append("content", new Blob([action.data]));
  const response = await window.fetch(
    "/api/branches/" + action.branch.id + "/files/" + action.filename,
    { method: "PUT", body: formData }
  );
  if (response.ok) {
    action.callback();
  } else {
    //showSaveError.set(true);
  }
}

/**
 * Synchronise the branches
 *
 * @param action The action
 */
async function synchroniseBranches(action: SynchroniseBranchesAction) {
  await window.fetch("/api/branches", { method: "PATCH" });
  if (action.callback) {
    action.callback();
  }
}
