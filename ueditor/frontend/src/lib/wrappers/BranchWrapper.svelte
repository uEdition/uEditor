<script lang="ts">
  import { getContext, onDestroy, setContext } from "svelte";
  import { derived, writable } from "svelte/store";
  import { createQuery, type CreateQueryResult } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";

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

  onDestroy(
    apiStatus.subscribe((apiStatus) => {
      if (
        apiStatus.isSuccess &&
        apiStatus.data.ready &&
        !apiStatus.data.git_enabled
      ) {
        currentBranch.set({ id: "-", nogit: true, title: "All files" });
      }
    })
  );
</script>

<slot></slot>
