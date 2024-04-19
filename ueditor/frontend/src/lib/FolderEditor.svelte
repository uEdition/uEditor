<script lang="ts">
  import { onDestroy, onMount } from "svelte";

  import { currentFile } from "../stores";
  import { activeDialog, Dialogs } from "./dialogs/Index.svelte";

  let focusElement: HTMLHeadingElement | null = null;

  onMount(() => {
    if (focusElement) {
      focusElement.focus();
    }
  });

  onDestroy(
    currentFile.subscribe(() => {
      if (focusElement) {
        focusElement.focus();
      }
    }),
  );
</script>

<div bind:this={focusElement} class="flex-1 px-2 py-2" tabindex="-1">
  <h2 class="sr-only">
    Actions for the directory {$currentFile?.fullpath
      ? $currentFile?.fullpath
      : "/"}
  </h2>
  <div class="flex flex-col w-60 space-y-2">
    <button
      data-button
      on:click={() => {
        activeDialog.set(Dialogs.FOLDER_CREATE);
      }}>Create a new Folder</button
    >
    <button
      data-button
      on:click={() => {
        activeDialog.set(Dialogs.FILE_CREATE);
      }}>Create a new File</button
    >
    <button
      class="px-3 py-1 border-2 transition-colors border-fuchsia-700 bg-white hover:bg-fuchsia-700 hover:text-white focus:bg-fuchsia-700 focus:text-white rounded"
      >Upload a File</button
    >
    <button
      class="px-3 py-1 border-2 transition-colors border-fuchsia-700 bg-white hover:bg-fuchsia-700 hover:text-white focus:bg-fuchsia-700 focus:text-white rounded"
      >Rename</button
    >
    <button
      data-button
      on:click={() => {
        activeDialog.set(Dialogs.FOLDER_DELETE);
      }}>Delete this Folder</button
    >
  </div>
</div>
