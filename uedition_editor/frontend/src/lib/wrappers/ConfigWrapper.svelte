<script lang="ts">
  import { createQuery } from "@tanstack/svelte-query";
  import { deepCopy } from "deep-copy-ts";

  import { apiQueryHandler } from "../../util";
  import { appState } from "../../state.svelte";

  const { children } = $props();

  const uEditionConfig = createQuery(() => ({
    queryKey: ["branches", appState.currentBranch?.id, "configs", "uedition"],
    queryFn: apiQueryHandler<UEditionSettings>,
    enabled: appState.currentBranch !== null,
  }));

  const uEditorConfig = createQuery(() => ({
    queryKey: ["branches", appState.currentBranch?.id, "configs", "ueditor"],
    queryFn: apiQueryHandler<UEditorSettings>,
    enabled: appState.currentBranch !== null,
  }));

  $effect(() => {
    if (uEditionConfig.isSuccess) {
      appState.uEditionConfig = uEditionConfig.data;
    } else {
      appState.uEditionConfig = null;
    }
    if (uEditorConfig.isSuccess) {
      appState.uEditorConfig = uEditorConfig.data;
    } else {
      appState.uEditorConfig = null;
    }
    if (uEditionConfig.isSuccess && uEditorConfig.isSuccess) {
      if (
        uEditionConfig.data.sphinx_config &&
        uEditionConfig.data.sphinx_config.tei &&
        uEditionConfig.data.sphinx_config.tei.blocks
      ) {
        appState.tei.blocks = deepCopy(
          uEditionConfig.data.sphinx_config.tei.blocks,
        ).concat(deepCopy(uEditorConfig.data.tei.blocks));
      } else {
        appState.tei.blocks = deepCopy(uEditorConfig.data.tei.blocks);
      }
      if (
        uEditionConfig.data.sphinx_config &&
        uEditionConfig.data.sphinx_config.tei &&
        uEditionConfig.data.sphinx_config.tei.marks
      ) {
        appState.tei.marks = deepCopy(
          uEditionConfig.data.sphinx_config.tei.marks,
        ).concat(deepCopy(uEditorConfig.data.tei.marks));
      } else {
        appState.tei.marks = deepCopy(uEditorConfig.data.tei.marks);
      }
    } else {
      appState.tei.blocks = [];
      appState.tei.marks = [];
    }
  });
</script>

{@render children()}
