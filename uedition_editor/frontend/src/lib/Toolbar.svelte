<script lang="ts">
  import { Toolbar } from "bits-ui";
  import { mdiContentSave } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import {
    currentFile,
    currentFileContent,
    currentFileModified,
    useApiStatus,
    useCurrentBranch,
  } from "../stores";
  import { runAction } from "./actions/Index.svelte";

  const queryClient = useQueryClient();
  const currentBranch = useCurrentBranch();
  const apiStatus = useApiStatus();

  function saveCurrentFile() {
    if ($currentFile !== null && $currentFileContent !== null) {
      runAction({
        action: "SaveCurrentFile",
        branch: $currentBranch as Branch,
        filename: $currentFile.fullpath,
        data: $currentFileContent,
        callback() {
          currentFileModified.set(false);
          if (
            $currentFile.name === "uEdition.yml" ||
            $currentFile.name === "uEdition.yaml" ||
            $currentFile.name === "uEditor.yml" ||
            $currentFile.name === "uEditor.yaml"
          ) {
            queryClient.invalidateQueries({ queryKey: ["configs"] });
          }
        },
      });
    }
  }
</script>

<Toolbar.Root class="border-b border-gray-300">
  {#if !$apiStatus.data?.git.protect_default_branch || $apiStatus.data?.git.default_branch !== $currentBranch?.id}
    <Toolbar.Button
      on:click={saveCurrentFile}
      aria-label="Save"
      title="Save"
      aria-disabled={$currentFileContent !== null && $currentFileModified
        ? null
        : "true"}
    >
      <Icon path={mdiContentSave} />
    </Toolbar.Button>
  {/if}
</Toolbar.Root>
