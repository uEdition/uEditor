<script context="module" lang="ts">
  import { writable } from "svelte/store";

  export enum Dialogs {
    NONE = 1,

    FOLDER_CREATE,
    FOLDER_DELETE,

    FILE_CREATE,
    FILE_DELETE,
  }

  export const activeDialog = writable(Dialogs.NONE);
</script>

<script lang="ts">
  import FolderCreate from "./folder/Create.svelte";
  import FolderDelete from "./folder/Delete.svelte";
  import FileCreate from "./file/Create.svelte";
  import FileDelete from "./file/Delete.svelte";
</script>

{#if $activeDialog === Dialogs.FOLDER_CREATE}
  <FolderCreate />
{:else if $activeDialog === Dialogs.FOLDER_DELETE}
  <FolderDelete />
{:else if $activeDialog === Dialogs.FILE_CREATE}
  <FileCreate />
{:else if $activeDialog === Dialogs.FILE_DELETE}
  <FileDelete />
{/if}
