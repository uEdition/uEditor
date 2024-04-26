<script context="module" lang="ts">
  import { writable } from "svelte/store";

  export enum Actions {
    LOAD_TEXT_FILE = 1,
  }

  const activeActions = writable([] as Action[]);

  export function runAction(action: Action) {
    activeActions.update((actions) => {
      return actions.concat([action]);
    });
  }
</script>

<script lang="ts">
</script>

<div>
  {#each $activeActions as action}
    <span>{action.type}</span>
  {/each}
</div>
