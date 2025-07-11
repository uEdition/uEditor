<script lang="ts">
  import {
    mdiFileDocumentPlusOutline,
    mdiFileUploadOutline,
    mdiFolderEditOutline,
    mdiFolderPlusOutline,
    mdiFolderRemoveOutline,
  } from "@mdi/js";
  import { onDestroy, onMount } from "svelte";

  import { currentFile, useApiStatus, useCurrentBranch } from "../../stores";
  import { activeDialog, Dialogs } from "../dialogs/Index.svelte";
  import Icon from "../Icon.svelte";

  const apiStatus = useApiStatus();
  const currentBranch = useCurrentBranch();
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
  {#if !$apiStatus.data?.git.protect_default_branch || $apiStatus.data?.git.default_branch !== $currentBranch?.id}
    <div class="flex flex-col w-60 space-y-2">
      <button
        data-button
        on:click={() => {
          activeDialog.set(Dialogs.FOLDER_CREATE);
        }}
      >
        <Icon path={mdiFolderPlusOutline} class="w4 h-4" />
        <span>Create a new Folder</span>
      </button>
      <button
        data-button
        on:click={() => {
          activeDialog.set(Dialogs.FILE_CREATE);
        }}
      >
        <Icon path={mdiFileDocumentPlusOutline} class="w4 h-4" />
        <span>Create a new File</span>
      </button>
      <button
        data-button
        on:click={() => {
          activeDialog.set(Dialogs.FILE_UPLOAD);
        }}
      >
        <Icon path={mdiFileUploadOutline} class="w4 h-4" />
        <span>Upload Files</span>
      </button>
      {#if $currentFile?.fullpath}
        <button
          data-button
          on:click={() => {
            activeDialog.set(Dialogs.FOLDER_RENAME);
          }}
        >
          <Icon path={mdiFolderEditOutline} class="w-4 h-4"></Icon>
          <span>Rename</span>
        </button>
        <button
          data-button
          on:click={() => {
            activeDialog.set(Dialogs.FOLDER_DELETE);
          }}
        >
          <Icon path={mdiFolderRemoveOutline} class="w-4 h-4"></Icon>
          <span>Delete this Folder</span>
        </button>
      {/if}
    </div>
  {:else}
    <div class="flex-1 relative px-2 py-1 text-gray-700">
      This branch is protected and no changes can be made.
    </div>
  {/if}
</div>
