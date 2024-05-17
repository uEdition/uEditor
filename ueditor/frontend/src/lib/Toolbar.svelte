<script lang="ts">
  import { Toolbar } from "bits-ui";
  import { mdiContentSave } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "./Icon.svelte";
  import {
    currentBranch,
    currentFile,
    currentFileContent,
    currentFileModified,
  } from "../stores";
  import { runAction } from "./actions/Index.svelte";

  const queryClient = useQueryClient();

  function saveCurrentFile() {
    if ($currentFile !== null && $currentFileContent !== null) {
      runAction({
        action: "SaveCurrentFile",
        branch: $currentBranch,
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

<Toolbar.Root class="flex flex-row border-b border-gray-300 px-2 py-1">
  <div class="flex items-center">
    <Toolbar.Button
      on:click={saveCurrentFile}
      aria-label="Save"
      class="p-1 border-2 border-transparent rounded {$currentFileContent !==
        null && $currentFileModified
        ? 'text-black hover:border-fuchsia-700 focus:border-fuchsia-700'
        : 'text-gray-400 cursor-not-allowed'}"
    >
      <Icon path={mdiContentSave} />
    </Toolbar.Button>
  </div>
</Toolbar.Root>
