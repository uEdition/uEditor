<script lang="ts">
  import { useCurrentBranch, currentFile } from "../../stores";

  const currentBranch = useCurrentBranch();
</script>

<div class="overflow-auto w-full">
  {#if $currentBranch !== null && $currentFile}
    <iframe
      src="/api/branches/{$currentBranch.id}/files/{$currentFile.fullpath}"
      title="Test"
      class="w-full h-full"
    />
  {/if}
</div>
