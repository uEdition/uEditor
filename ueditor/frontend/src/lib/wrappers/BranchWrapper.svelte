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
  import { useApiStatus, useCurrentUser } from "../../stores";

  const initialBranchId = getApplicationParameter("branch");

  const apiStatus = useApiStatus();
  const currentUser = useCurrentUser();

  const branchesQuery = derived(
    [apiStatus, currentUser],
    ([apiStatus, currentUser]) => {
      return {
        queryKey: ["branches"],
        queryFn: apiQueryHandler<Branch[]>,
        refetchInterval: 60000,
        enabled:
          apiStatus.isSuccess && apiStatus.data.ready && currentUser.isSuccess,
      };
    }
  );
  const branches = createQuery(branchesQuery);
  setContext("branches", branches);

  const remoteBranchesQuery = derived(
    [apiStatus, currentUser],
    ([apiStatus, currentUser]) => {
      return {
        queryKey: ["branches", "?category=remote"],
        queryFn: apiQueryHandler<Branch[]>,
        refetchInterval: 60000,
        enabled:
          apiStatus.isSuccess &&
          apiStatus.data.ready &&
          apiStatus.data.git.enabled &&
          currentUser.isSuccess,
      };
    }
  );
  const remoteBranches = createQuery(remoteBranchesQuery);
  setContext("remoteBranches", remoteBranches);

  const currentBranch = writable(null as Branch | null);
  setContext("currentBranch", currentBranch);

  const syncBranchesQuery = derived(
    [apiStatus, currentUser],
    ([apiStatus, currentUser]) => {
      return {
        queryKey: [":internal:", "branches"],
        queryFn: async () => {
          let response = await window.fetch("/api/branches", {
            method: "PATCH",
          });
          if (response.ok) {
            return true;
          }
          throw new Error("Could not fetch data");
        },
        refetchInterval: 60000,
        enabled:
          apiStatus.isSuccess &&
          apiStatus.data.ready &&
          apiStatus.data.git.enabled &&
          currentUser.isSuccess,
      };
    }
  );
  const syncBranches = createQuery(syncBranchesQuery);
  setContext("syncBranches", syncBranches);

  const apiStatusUnsubscribe = apiStatus.subscribe((apiStatus) => {
    if (
      apiStatus.isSuccess &&
      apiStatus.data.ready &&
      !apiStatus.data.git.enabled
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
