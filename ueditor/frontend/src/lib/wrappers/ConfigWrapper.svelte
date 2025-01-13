<script lang="ts">
  import { getContext, setContext } from "svelte";
  import { derived, type Readable } from "svelte/store";
  import { createQuery, type CreateQueryResult } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";

  const currentBranch = getContext("currentBranch") as Readable<Branch | null>;

  const uEditionConfigQuery = derived(currentBranch, (currentBranch) => {
    if (currentBranch !== null) {
      return {
        queryKey: ["branches", currentBranch.id, "configs", "uedition"],
        queryFn: apiQueryHandler<UEditionSettings>,
      };
    } else {
      return {
        queryKey: ["branches", "-", "configs", "uedition"],
        queryFn: apiQueryHandler<UEditionSettings>,
        enabled: currentBranch !== null,
      };
    }
  });
  const uEditionConfig = createQuery(uEditionConfigQuery);
  setContext("uEditionConfig", uEditionConfig);

  const uEditorConfigQuery = derived(currentBranch, (currentBranch) => {
    if (currentBranch !== null) {
      return {
        queryKey: ["branches", currentBranch.id, "configs", "ueditor"],
        queryFn: apiQueryHandler<UEditorSettings>,
      };
    } else {
      return {
        queryKey: ["branches", "-", "configs", "ueditor"],
        queryFn: apiQueryHandler<UEditorSettings>,
        enabled: false,
      };
    }
  });
  const uEditorConfig = createQuery(uEditorConfigQuery);
  setContext("uEditorConfig", uEditorConfig);
</script>

<slot></slot>
