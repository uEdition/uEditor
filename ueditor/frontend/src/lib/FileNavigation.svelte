<script lang="ts">
  import { createTreeView } from "@melt-ui/svelte";
  import { onDestroy, onMount, setContext, tick } from "svelte";
  import { type Unsubscriber } from "svelte/store";
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
    states: { selectedItem, expanded },
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

  const unsubscribeSelectedItem = selectedItem.subscribe((selectedElement) => {
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
      if (selectedFileTreeEntry) {
        window.location.hash = selectedFileTreeEntry.fullpath;
      }
    } else {
      currentFile.set(null);
    }
  });
  onDestroy(unsubscribeSelectedItem);

  function calculateExpanded(button: HTMLElement): string[] {
    const expansion: string[] = [];
    while (button && button.getAttribute("role") === "treeitem") {
      expansion.splice(0, 0, button.getAttribute("data-id") as string);
      button =
        button.parentElement?.parentElement?.parentElement?.querySelector(
          ":scope > [role=treeitem]"
        ) as HTMLElement;
    }
    return expansion;
  }

  onMount(() => {
    if (window.location.hash !== "") {
      let fileListUnsubscribe: Unsubscriber | undefined;
      fileListUnsubscribe = fileList.subscribe((entries) => {
        if (entries.isSuccess) {
          tick().then(() => {
            const selectedButton = document.querySelector(
              '[data-file-path="' + window.location.hash.substring(1) + '"]'
            ) as HTMLElement;
            if (selectedButton) {
              expanded.set(calculateExpanded(selectedButton));
              selectedItem.set(selectedButton);
            }
          });
          if (fileListUnsubscribe) {
            fileListUnsubscribe();
          }
        }
      });
    }
  });
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
