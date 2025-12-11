<script lang="ts">
  import { appState } from "../../state.svelte";
</script>

<div class="overflow-auto">
  {#if appState.currentBranch !== null && appState.currentFile !== null}
    <img
      src="/api/branches/{appState.currentBranch.id}/files/{appState.currentFile
        .fullpath}"
      alt=""
    />
  {/if}
</div>
