<script lang="ts">
  import { createQuery } from "@tanstack/svelte-query";

  import {
    apiQueryHandler,
    deleteApplicationParameter,
    getApplicationParameter,
    setApplicationParameter,
  } from "../../util";
  import { appState } from "../../state.svelte";

  const { children } = $props();
  let initialBranchId = getApplicationParameter("branch");

  const branches = createQuery(() => ({
    queryKey: ["branches"],
    queryFn: apiQueryHandler<Branches>,
    refetchInterval: 60000,
  }));

  $effect(() => {
    if (!appState.apiStatus?.git.enabled) {
      appState.currentBranch = { id: "-", nogit: true, title: "All files" };
    }
  });

  $effect(() => {
    if (appState.currentBranch !== null) {
      setApplicationParameter("branch", appState.currentBranch.id);
    } else {
      deleteApplicationParameter("branch");
    }
  });

  $effect(() => {
    if (branches.isSuccess) {
      appState.branches = branches.data;
      if (initialBranchId !== null) {
        for (let branch of branches.data.local) {
          if (branch.id === initialBranchId) {
            appState.currentBranch = branch;
            initialBranchId = null;
            break;
          }
        }
      }
    }
  });
</script>

{@render children()}
