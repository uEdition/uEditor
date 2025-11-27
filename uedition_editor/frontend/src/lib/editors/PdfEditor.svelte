<script lang="ts">
  import { appState } from "../../state.svelte";
</script>

<div class="overflow-auto w-full">
  {#if appState.currentBranch !== null && appState.currentFile !== null}
    <iframe
      src="/api/branches/{appState.currentBranch.id}/files/{appState.currentFile
        .fullpath}"
      title="Test"
      class="w-full h-full"
    ></iframe>
  {/if}
</div>
