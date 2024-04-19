<script lang="ts">
  import FolderEditor from "./FolderEditor.svelte";
  import { currentFile } from "../stores";
</script>

{#if $currentFile !== null}
  {#if $currentFile.type === "folder"}
    <FolderEditor />
  {:else}
    <div class="flex-1 px-2 py-1 text-rose-700">
      Unfortunately the μEditor does not know how to edit this file.
    </div>
  {/if}
{:else}
  <div class="flex-1 relative px-2 py-1 text-gray-700">
    Please select a file or folder from the file-browser on the left
  </div>
{/if}
