<script lang="ts">
  import { useCurrentBranch, currentFile } from "../../stores";

  const currentBranch = useCurrentBranch();
</script>

<div class="overflow-auto">
  {#if $currentBranch !== null && $currentFile}
    <img
      src="/api/branches/{$currentBranch.id}/files/{$currentFile.fullpath}"
      alt=""
    />
  {/if}
</div>
