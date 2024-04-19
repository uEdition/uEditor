<script context="module" lang="ts">
  import {writable} from "svelte/store";

  export enum Actions {
    NOTHING = 1,
    FOLDER_CREATE,
    FOLDER_DELETE,
  }

  export const activeAction = writable(Actions.NOTHING);
</script>
<script lang="ts"></script>
{#if $activeAction === Actions.FOLDER_CREATE}
Create!
{:else if $activeAction === Actions.FOLDER_DELETE}
Delete!
{/if}
