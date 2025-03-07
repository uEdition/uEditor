<script lang="ts">
  import { setContext } from "svelte";
  import { derived } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { useCurrentBranch } from "../../stores";

  const currentBranch = useCurrentBranch();

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
