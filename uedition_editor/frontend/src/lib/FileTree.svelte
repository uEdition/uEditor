<script lang="ts">
  import {
    mdiFolderOpenOutline,
    mdiFolderOutline,
    mdiFileDocumentOutline,
    mdiFileOutline,
    mdiFileCogOutline,
    mdiFileImageOutline,
  } from "@mdi/js";
  import { melt, type TreeView } from "@melt-ui/svelte";
  import slugify from "slugify";
  import { getContext } from "svelte";

  import Icon from "./Icon.svelte";
  import FileTree from "./FileTree.svelte";
  import { appState } from "../state.svelte";

  type FileTreeProps = {
    treeItems: FileTreeEntry[];
    level: number;
  };

  let { treeItems, level = 1 }: FileTreeProps = $props();

  const {
    elements: { item, group },
    helpers: { isExpanded, isSelected },
  } = getContext<TreeView>("tree");

  function isModified(path: string, modified_files: string[]) {
    for (const modified of modified_files) {
      if (modified.startsWith(path)) {
        return true;
      }
    }
    return false;
  }
</script>

{#each treeItems as { name, type, fullpath, content, mimetype }, i}
  {@const itemId = `file-tree-${slugify(name, { strict: true })}-${level}-${i}`}
  {@const hasChildren = !!content?.length}

  <li role="none">
    <button
      class="flex items-center gap-1 p-1 {appState.currentBranch
        ?.modified_files &&
      isModified(fullpath, appState.currentBranch.modified_files)
        ? 'font-bold'
        : ''}"
      use:melt={$item({
        id: itemId,
        hasChildren,
      })}
      data-file-path={fullpath}
    >
      {#if type === "folder" && hasChildren && $isExpanded(itemId)}
        <Icon path={mdiFolderOpenOutline} />
      {:else if type === "folder"}
        <Icon path={mdiFolderOutline} />
      {:else if type === "file"}
        {#if mimetype === "text/markdown" || mimetype === "application/tei+xml"}
          <Icon path={mdiFileDocumentOutline} />
        {:else if mimetype.startsWith("image/")}
          <Icon path={mdiFileImageOutline} />
        {:else if mimetype === "application/yaml" || mimetype === "application/toml" || mimetype === "application/gitignore"}
          <Icon path={mdiFileCogOutline} />
        {:else}
          <Icon path={mdiFileOutline} />
        {/if}
      {/if}

      <span class="select-none">{name}</span>
    </button>

    {#if content}
      <ol use:melt={$group({ id: itemId })}>
        <FileTree treeItems={content} level={level + 1} />
      </ol>
    {/if}
  </li>
{/each}
