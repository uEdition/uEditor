<script lang="ts">
  import { setContext } from "svelte";
  import { derived } from "svelte/store";
  import { createQuery } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { useCurrentBranch } from "../../stores";
  import { deepCopy } from "deep-copy-ts";

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

  const configuredTEIBlocks = derived(
    [uEditionConfig, uEditorConfig],
    ([uEditionConfig, uEditorConfig]) => {
      if (uEditionConfig.isSuccess && uEditorConfig.isSuccess) {
        let configuredBlocks = deepCopy(uEditorConfig.data.tei.blocks);
        if (
          uEditionConfig.data.sphinx_config &&
          uEditionConfig.data.sphinx_config.tei &&
          uEditionConfig.data.sphinx_config.tei.blocks
        ) {
          configuredBlocks = configuredBlocks.concat(
            deepCopy(uEditionConfig.data.sphinx_config.tei.blocks),
          );
        }
        return configuredBlocks;
      }
      return [];
    },
  );
  setContext("configuredTEIBlocks", configuredTEIBlocks);

  const configuredTEIMarks = derived(
    [uEditionConfig, uEditorConfig],
    ([uEditionConfig, uEditorConfig]) => {
      if (uEditionConfig.isSuccess && uEditorConfig.isSuccess) {
        let configuredMarks = deepCopy(uEditorConfig.data.tei.marks);
        if (
          uEditionConfig.data.sphinx_config &&
          uEditionConfig.data.sphinx_config.tei &&
          uEditionConfig.data.sphinx_config.tei.marks
        ) {
          configuredMarks = configuredMarks.concat(
            deepCopy(uEditionConfig.data.sphinx_config.tei.marks),
          );
        }
        return configuredMarks;
      }
      return [];
    },
  );
  setContext("configuredTEIMarks", configuredTEIMarks);
</script>

<slot></slot>
