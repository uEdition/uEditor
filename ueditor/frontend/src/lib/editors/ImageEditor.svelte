<script lang="ts">
  import { currentBranch, currentFile } from "../../stores";
</script>

<div class="overflow-auto">
  {#if $currentFile}
    <img
      src="/api/branches/{$currentBranch}/files/{$currentFile.fullpath}"
      alt=""
    />
  {/if}
</div>
