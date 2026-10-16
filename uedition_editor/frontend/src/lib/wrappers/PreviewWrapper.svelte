<script lang="ts">
  import { createQuery } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { appState } from "../../state.svelte";

  const { children } = $props();

  let refetchInterval = $state(60000);
  const previewStatus = createQuery(() => ({
    queryKey: ["branches", appState.currentBranch?.id, "preview", "status"],
    queryFn: apiQueryHandler<string>,
    refetchInterval: refetchInterval,
    enabled: appState.currentBranch !== null,
  }));

  $effect(() => {
    if (appState.currentBranch !== null && previewStatus.isSuccess) {
      if (appState.preview !== previewStatus.data) {
        appState.preview = previewStatus.data;
      }
    } else if (appState.preview !== null) {
      appState.preview = null;
    }
  });

  $effect(() => {
    const newRefetchInterval =
      appState.preview === "generating" ? 10000 : 60000;
    if (newRefetchInterval !== refetchInterval) {
      refetchInterval = newRefetchInterval;
    }
  });
</script>

{@render children()}
