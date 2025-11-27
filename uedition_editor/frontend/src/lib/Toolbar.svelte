<script lang="ts">
  import { Toolbar } from "bits-ui";
  import { mdiContentSave } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import { runAction } from "./actions/Index.svelte";
  import { appState } from "../state.svelte";

  const queryClient = useQueryClient();

  function saveCurrentFile() {
    if (
      appState.currentFile !== null &&
      appState.currentBranch !== null &&
      appState.currentFileContent !== null
    ) {
      runAction({
        action: "SaveCurrentFile",
        branch: appState.currentBranch,
        filename: appState.currentFile.fullpath,
        data: appState.currentFileContent,
        callback() {
          appState.ui.currentFileModified = false;
          if (
            appState.currentFile?.name === "uEdition.yml" ||
            appState.currentFile?.name === "uEdition.yaml" ||
            appState.currentFile?.name === "uEditor.yml" ||
            appState.currentFile?.name === "uEditor.yaml"
          ) {
            queryClient.invalidateQueries({ queryKey: ["configs"] });
          }
        },
      });
    }
  }
</script>

<Toolbar.Root class="border-b border-gray-300">
  {#if appState.apiStatus?.git.default_branch !== appState.currentBranch?.id}
    <Toolbar.Button
      onclick={saveCurrentFile}
      aria-label="Save"
      title="Save"
      aria-disabled={appState.currentFileContent !== null &&
      appState.ui.currentFileModified
        ? null
        : "true"}
    >
      <Icon path={mdiContentSave} />
    </Toolbar.Button>
  {/if}
</Toolbar.Root>
