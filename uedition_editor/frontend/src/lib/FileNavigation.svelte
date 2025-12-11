<script lang="ts">
  import { createTreeView } from "@melt-ui/svelte";
  import { onDestroy, setContext, tick } from "svelte";
  import { createQuery } from "@tanstack/svelte-query";

  import Tree from "./FileTree.svelte";
  import LoadingIndicator from "./LoadingIndicator.svelte";
  import {
    apiQueryHandler,
    deleteApplicationParameter,
    getApplicationParameter,
    setApplicationParameter,
  } from "../util";
  import { appState } from "../state.svelte";

  let initialPath = getApplicationParameter("path");

  const fileList = createQuery(() => ({
    queryKey: ["branches", appState.currentBranch?.id, "files/"],
    queryFn: apiQueryHandler<FileTreeEntry[]>,
    enabled: appState.currentUser !== null && appState.currentBranch !== null,
  }));

  $effect(() => {
    if (fileList.isSuccess && initialPath !== null) {
      tick().then(() => {
        const selectedButton = document.querySelector(
          '[data-file-path="' + initialPath + '"]',
        ) as HTMLElement;
        if (selectedButton) {
          expanded.set(calculateExpanded(selectedButton));
          selectedItem.set(selectedButton);
        }
        initialPath = null;
      });
    }
  });

  const ctx = createTreeView({ defaultExpanded: ["file-tree--1-0"] });
  setContext("tree", ctx);

  const {
    elements: { tree },
    states: { selectedItem, expanded },
  } = ctx;

  function recursiveFileSeach(
    entries: FileTreeEntry[],
    fullpath: string,
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
      fileList.isSuccess
    ) {
      const selectedFileTreeEntry = recursiveFileSeach(
        fileList.data,
        selectedElement?.getAttribute("data-file-path") as string,
      );
      appState.currentFile = selectedFileTreeEntry;
      if (appState.currentFile !== null) {
        appState.currentFileContent = null;
        setApplicationParameter("path", appState.currentFile.fullpath);
      } else {
        deleteApplicationParameter("path");
      }
    } else {
      appState.currentFile = null;
    }
  });
  onDestroy(unsubscribeSelectedItem);

  function calculateExpanded(button: HTMLElement): string[] {
    const expansion: string[] = [];
    while (button && button.getAttribute("role") === "treeitem") {
      expansion.splice(0, 0, button.getAttribute("data-id") as string);
      button =
        button.parentElement?.parentElement?.parentElement?.querySelector(
          ":scope > [role=treeitem]",
        ) as HTMLElement;
    }
    return expansion;
  }
</script>

<nav
  aria-label="Files"
  class="relative px-2 py-1 w-3/12 overflow-auto border-r border-gray-300"
>
  {#if fileList.isSuccess}
    <ol {...$tree}>
      <Tree treeItems={fileList.data} />
    </ol>
  {:else if fileList.isLoading}
    <LoadingIndicator>Loading the file list. Please wait...</LoadingIndicator>
  {/if}
</nav>
