<script lang="ts">
  import DirectoryEditor from "./DirectoryEditor/Index.svelte";
  import { currentFile } from "../stores";
</script>

{#if $currentFile !== null}
  {#if $currentFile.type === "directory"}
    <DirectoryEditor />
  {:else}
    <div class="flex-1 px-2 py-1 text-rose-700">
      Unfortunately the μEditor does not know how to edit this file.
    </div>
  {/if}
{:else}
  <div class="flex-1 relative px-2 py-1 text-gray-700">
    Please select a file from the file-browser on the left
  </div>
{/if}
