<script context="module" lang="ts">
  import { Popover } from "bits-ui";
  import { writable } from "svelte/store";

  const activeActions = writable([] as Action[]);

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
      "/api/branches/" + action.branch + "/files/" + action.filename,
    );
    action.callback(await response.text());
  }

  async function saveCurrentFile(action: SaveCurrentFileAction) {
    const formData = new FormData();
    formData.append("content", new Blob([action.data]));
    const response = await window.fetch(
      "/api/branches/" + action.branch + "/files/" + action.filename,
      { method: "PUT", body: formData },
    );
    action.callback();
  }
</script>

<script lang="ts">
  import { mdiRefresh, mdiSync } from "@mdi/js";
  import Icon from "../Icon.svelte";
</script>

<Popover.Root>
  <Popover.Trigger>
    {#if $activeActions.length === 0}
      Idle
    {:else if $activeActions.length === 1}
      1 action running
    {:else}
      {$activeActions.length} actions running
    {/if}
    <Popover.Content class="z-50 bg-white shadow-lg">
      <ul>
        {#each $activeActions as action}
          <li
            class="flex flex-row items-center space-x-2 px-3 py-1 border-l border-r last:border-b first-border-t border-slate-300"
          >
            {#if action.action === "LoadTextFile"}
              <Icon path={mdiSync} class="w-4 h-4 animate-spin" />
              <span class="flex-1">Loading file...</span>
            {/if}
          </li>
        {/each}
      </ul>
    </Popover.Content>
  </Popover.Trigger>
</Popover.Root>
