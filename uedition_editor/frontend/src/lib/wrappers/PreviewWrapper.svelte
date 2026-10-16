<script lang="ts">
  import { createQuery } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { appState } from "../../state.svelte";

  const { children } = $props();

  const previewStatus = createQuery(() => ({
    queryKey: ["branches", appState.currentBranch?.id, "preview", "status"],
    queryFn: apiQueryHandler<string>,
    refetchInterval: appState.preview === "generating" ? 10000 : 60000,
    enabled: appState.currentBranch !== null,
  }));

  $effect(() => {
    if (appState.currentBranch !== null && previewStatus.isSuccess) {
      appState.preview = previewStatus.data;
    } else {
      appState.preview = null;
    }
  });
</script>

{@render children()}
