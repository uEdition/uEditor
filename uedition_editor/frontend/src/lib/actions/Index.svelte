<script context="module" lang="ts">
  import { writable } from "svelte/store";

  const activeActions = writable([] as Action[]);
  let showSaveError = writable(false);

  /**
   * Start running a new action.
   *
   * @param action The action to start running
   */
  export function runAction(action: Action) {
    action.status = "active";
    activeActions.update((actions) => {
      return actions.concat([action]);
    });
    let promise: Promise<void> | null = null;
    if (action.action === "LoadTextFile") {
      promise = loadTextFile(action);
    } else if (action.action === "SaveCurrentFile") {
      promise = saveCurrentFile(action);
    } else if (action.action === "SynchroniseBranches") {
      promise = synchroniseBranches(action);
    }
    if (promise !== null) {
      promise.then(() => {
        activeActions.update((actions) => {
          const idx = actions.indexOf(action);
          if (idx >= 0) {
            return actions.slice(0, idx).concat(actions.slice(idx + 1));
          } else {
            return actions;
          }
        });
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
      "/api/branches/" + action.branch.id + "/files/" + action.filename,
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
      { method: "PUT", body: formData },
    );
    if (response.ok) {
      action.callback();
    } else {
      showSaveError.set(true);
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
</script>

<script lang="ts">
  import { Dialog, Popover } from "bits-ui";
  import { mdiSync } from "@mdi/js";
  import { derived } from "svelte/store";

  import Icon from "../Icon.svelte";
  import { useBranches } from "../../stores";

  const branches = useBranches();
  const backgroundBusyCount = derived([branches], (stores) => {
    let count = 0;
    for (const store of stores) {
      if (store !== null && store.isFetching) {
        count = count + 1;
      }
    }
    return count;
  });
</script>

<Popover.Root>
  <Popover.Trigger class="inline-flex items-center">
    {#if $activeActions.length + $backgroundBusyCount === 0}
      <span>Idle</span>
    {:else if $activeActions.length + $backgroundBusyCount === 1}
      <Icon path={mdiSync} class="w-4 h-4 animate-spin animate-reverse" />
      <span class="pl-2">1 action running</span>
    {:else}
      <Icon path={mdiSync} class="w-4 h-4 animate-spin animate-reverse" />
      <span class="pl-2"
        >{$activeActions.length + $backgroundBusyCount} actions running</span
      >
    {/if}
  </Popover.Trigger>
  <Popover.Content class="z-50 bg-white shadow-lg">
    <ul>
      {#each $activeActions as action}
        <li
          class="flex flex-row items-center space-x-2 px-3 py-1 border-l border-r last:border-b first-border-t border-slate-300"
        >
          {#if action.action === "LoadTextFile"}
            <Icon path={mdiSync} class="w-4 h-4 animate-spin animate-reverse" />
            <span class="flex-1">Loading file</span>
          {:else if action.action === "SaveCurrentFile"}
            <Icon path={mdiSync} class="w-4 h-4 animate-spin animate-reverse" />
            <span class="flex-1">Saving file</span>
          {/if}
        </li>
      {/each}
      {#if $branches.isFetching}
        <li
          class="flex flex-row items-center space-x-2 px-3 py-1 border-l border-r last:border-b first-border-t border-slate-300"
        >
          <Icon path={mdiSync} class="w-4 h-4 animate-spin animate-reverse" />
          <span class="flex-1">Fetching branches</span>
        </li>
      {/if}
    </ul>
  </Popover.Content>
</Popover.Root>

{#if $showSaveError}
  <Dialog.Root
    open={true}
    onOpenChange={(open) => {
      if (!open) {
        showSaveError.set(false);
      }
    }}
  >
    <Dialog.Trigger class="hidden" />
    <Dialog.Portal>
      <Dialog.Overlay />
      <Dialog.Content>
        <Dialog.Title>Saving failed</Dialog.Title>
        <div data-dialog-content-area>
          <p>Unfortunately saving the file failed.</p>
          <div data-dialog-buttons>
            <Dialog.Close data-button>Close</Dialog.Close>
          </div>
        </div>
      </Dialog.Content>
    </Dialog.Portal>
  </Dialog.Root>
{/if}
