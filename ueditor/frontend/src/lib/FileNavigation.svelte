<script lang="ts">
  import { mdiSync } from "@mdi/js";
  import { createTreeView } from "@melt-ui/svelte";
  import { onDestroy, setContext } from "svelte";
  import { createQuery } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../util";
  import { currentBranch, currentFile } from "../stores";

  import Tree from "./FileTree.svelte";
  import LoadingIndicator from "./LoadingIndicator.svelte";

  const fileList = createQuery({
    queryKey: ["branches", $currentBranch, "files/"],
    queryFn: apiQueryHandler<FileTreeEntry[]>,
  });

  const ctx = createTreeView({ defaultExpanded: ["file-tree--1-0"] });
  setContext("tree", ctx);

  const {
    elements: { tree },
    states: { selectedItem },
  } = ctx;

  function recursiveFileSeach(
    entries: FileTreeEntry[],
    fullpath: string
  ): FileTreeEntry | null {
    for (let entry of entries) {
      if (entry.fullpath === fullpath) {
        return entry;
      }
      if (entry.content) {
        const tmp = recursiveFileSeach(entry.content, fullpath);
        if (tmp !== null) {
          return tmp;
        }
      }
    }
    return null;
  }

  const unsubscribe = selectedItem.subscribe((selectedElement) => {
    if (
      selectedItem !== null &&
      selectedElement?.getAttribute("data-file-path") !== null &&
      $fileList.isSuccess
    ) {
      const selectedFileTreeEntry = recursiveFileSeach(
        $fileList.data,
        selectedElement?.getAttribute("data-file-path") as string
      );
      currentFile.set(selectedFileTreeEntry);
    } else {
      currentFile.set(null);
    }
  });
  onDestroy(unsubscribe);
</script>

<nav
  aria-label="Files"
  class="relative px-2 py-1 w-3/12 overflow-auto border-r border-gray-300"
>
  {#if $fileList.isSuccess}
    <ol {...$tree}>
      <Tree treeItems={$fileList.data} />
    </ol>
  {:else if $fileList.isLoading}
    <LoadingIndicator>Loading the file list. Please wait...</LoadingIndicator>
  {/if}
</nav>
