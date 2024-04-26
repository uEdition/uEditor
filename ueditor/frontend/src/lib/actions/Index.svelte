<script context="module" lang="ts">
  import { writable } from "svelte/store";

  export enum Actions {
    LOAD_TEXT_FILE = 1,
  }

  export const activeActions = writable([] as Actions[]);
</script>

<script lang="ts">
</script>

<div>Ready</div>
