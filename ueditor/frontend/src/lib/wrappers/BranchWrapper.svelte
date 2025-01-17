<script lang="ts">
  import { getContext, onDestroy, setContext } from "svelte";
  import { derived, writable } from "svelte/store";
  import { createQuery, type CreateQueryResult } from "@tanstack/svelte-query";

  import {
    apiQueryHandler,
    deleteApplicationParameter,
    getApplicationParameter,
    setApplicationParameter,
  } from "../../util";

  const initialBranchId = getApplicationParameter("branch");

  const apiStatus = getContext("apiStatus") as CreateQueryResult<APIStatus>;

  const branchesQuery = derived(apiStatus, (apiStatus) => {
    return {
      queryKey: ["branches"],
      queryFn: apiQueryHandler<Branch[]>,
    };
  });
  const branches = createQuery(branchesQuery);
  setContext("branches", branches);

  const currentBranch = writable(null as Branch | null);
  setContext("currentBranch", currentBranch);

  const apiStatusUnsubscribe = apiStatus.subscribe((apiStatus) => {
    if (
      apiStatus.isSuccess &&
      apiStatus.data.ready &&
      !apiStatus.data.git_enabled
    ) {
      currentBranch.set({ id: "-", nogit: true, title: "All files" });
    }
  });

  const currentBranchUnsubscribe = currentBranch.subscribe((currentBranch) => {
    if (currentBranch !== null) {
      setApplicationParameter("branch", currentBranch.id);
    } else {
      deleteApplicationParameter("branch");
    }
  });

  const setInitialBranchUnsubscribe = branches.subscribe((branches) => {
    if (branches.isSuccess) {
      for (let branch of branches.data) {
        if (branch.id === initialBranchId) {
          currentBranch.set(branch);
        }
      }
      setInitialBranchUnsubscribe();
    }
  });

  onDestroy(() => {
    currentBranchUnsubscribe();
    apiStatusUnsubscribe();
  });
</script>

<slot></slot>
