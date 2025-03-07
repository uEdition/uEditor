<script lang="ts">
  import { Toolbar, Separator } from "bits-ui";
  import {
    mdiCancel,
    mdiChevronDown,
    mdiChevronUp,
    mdiPlus,
    mdiTrashCan,
  } from "@mdi/js";
  import { createTreeView } from "@melt-ui/svelte";
  import { createEventDispatcher, setContext } from "svelte";
  import { derived } from "svelte/store";

  import Tree from "./TeiMetadataTree.svelte";
  import Icon from "../Icon.svelte";

  export let section: TEIMetadataSection | null = null;

  const dispatch = createEventDispatcher();
  const ctx = createTreeView({ defaultExpanded: ["file-tree--1-0"] });
  setContext("tree", ctx);

  const {
    elements: { tree },
    states: { selectedItem },
  } = ctx;

  function findNodeByPath(node: TeiMetadataNode, dataId: string) {
    const idPath = dataId
      .substring(14)
      .split("-")
      .map((value) => {
        return Number.parseInt(value);
      });
    for (let idx of idPath) {
      if (node) {
        node = node.content[idx];
      }
    }
    if (node) {
      return node;
    }
  }

  const selectedNode = derived(selectedItem, (selectedItem) => {
    if (selectedItem !== null && section) {
      const dataId = selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          section as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          return node;
        }
      }
    }
    return null;
  });

  /**
   * Update the tag name of the node.
   *
   * @param ev The event containing the new tag name.
   */
  function updateTag(ev: Event) {
    ev.preventDefault();
    if ($selectedItem !== null && section) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          section as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          node.type = (ev.target as HTMLInputElement).value;
          dispatch("update", section);
          section = section;
        }
      }
    }
  }

  /**
   * Update the text of the selected node.
   *
   * @param ev The change event with the updated data.
   */
  function updateText(ev: Event) {
    ev.preventDefault();
    if ($selectedItem !== null && section) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          section as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          node.text = (ev.target as HTMLInputElement).value;
          dispatch("update", section);
        }
      }
    }
  }

  /**
   * Add a new node.
   *
   * @param ev The event that caused this.
   */
  function addNewNode(ev: Event) {
    ev.preventDefault();
    if (section) {
      const newNode = {
        type: "newNode",
        text: "",
        attrs: [],
        content: [],
      };
      if ($selectedItem) {
        const dataId = $selectedItem.getAttribute("data-id");
        if (dataId) {
          const node = findNodeByPath(
            section as unknown as TeiMetadataNode,
            dataId,
          );
          if (node) {
            node.content.push(newNode);
          }
        }
      } else {
        section.content.push(newNode);
      }
      dispatch("update", section);
      section = section;
    }
  }

  /**
   * Delete the selected node.
   *
   * @param ev The event that triggered this.
   */
  function deleteSelectedNode(ev: Event) {
    ev.preventDefault();
    if (section && $selectedItem) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const idPath = dataId.split("-");
        const parentIdPath = idPath.slice(0, idPath.length - 1);
        const parent = findNodeByPath(
          section as unknown as TeiMetadataNode,
          parentIdPath.join("-"),
        );
        if (parent) {
          parent.content.splice(Number.parseInt(idPath[idPath.length - 1]), 1);
          dispatch("update", section);
          section = section;
        } else {
          section.content.splice(Number.parseInt(idPath[idPath.length - 1]), 1);
          dispatch("update", section);
          section = section;
        }
      }
    }
  }

  /**
   * Move the selected node up one place in its list of siblings.
   *
   * @param ev The event that caused this.
   */
  function moveSelectedNodeUp(ev: Event) {
    ev.preventDefault();
    if (section && $selectedItem) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const idPath = dataId.split("-");
        const parentIdPath = idPath.slice(0, idPath.length - 1);
        const parent = findNodeByPath(
          section as unknown as TeiMetadataNode,
          parentIdPath.join("-"),
        );
        const selectedIdx = Number.parseInt(idPath[idPath.length - 1]);
        if (parent && selectedIdx > 0) {
          const removed = parent.content.splice(selectedIdx, 1);
          parent.content.splice(selectedIdx - 1, 0, ...removed);
          selectedItem.set(null);
          dispatch("update", section);
          section = section;
        } else if (selectedIdx > 0) {
          const removed = section.content.splice(selectedIdx, 1);
          section.content.splice(selectedIdx - 1, 0, ...removed);
          selectedItem.set(null);
          dispatch("update", section);
          section = section;
        }
      }
    }
  }

  /**
   * Move the selected node down one place in its list of siblings.
   *
   * @param ev The event that caused this.
   */
  function moveSelectedNodeDown(ev: Event) {
    ev.preventDefault();
    if (section && $selectedItem) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const idPath = dataId.split("-");
        const parentIdPath = idPath.slice(0, idPath.length - 1);
        const parent = findNodeByPath(
          section as unknown as TeiMetadataNode,
          parentIdPath.join("-"),
        );
        const selectedIdx = Number.parseInt(idPath[idPath.length - 1]);
        if (parent && selectedIdx < parent.content.length - 1) {
          const removed = parent.content.splice(selectedIdx, 1);
          parent.content.splice(selectedIdx + 1, 0, ...removed);
          selectedItem.set(null);
          dispatch("update", section);
          section = section;
        } else if (selectedIdx < section.content.length - 1) {
          const removed = section.content.splice(selectedIdx, 1);
          section.content.splice(selectedIdx + 1, 0, ...removed);
          selectedItem.set(null);
          dispatch("update", section);
          section = section;
        }
      }
    }
  }

  function addAttribute(ev: Event) {
    ev.preventDefault();
    if ($selectedItem !== null && section) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          section as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          node.attrs.push({ type: "", value: "" });
          dispatch("update", section);
          section = section;
          selectedItem.set($selectedItem);
        }
      }
    }
  }
  function updateAttributeName(ev: Event, idx: number) {
    ev.preventDefault();
    if ($selectedItem !== null && section) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          section as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          if (idx >= 0 && idx < node.attrs.length) {
            node.attrs[idx].type = (ev.target as HTMLInputElement).value;
            dispatch("update", section);
            section = section;
            selectedItem.set($selectedItem);
          }
        }
      }
    }
  }
  function updateAttributeValue(ev: Event, idx: number) {
    ev.preventDefault();
    if ($selectedItem !== null && section) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          section as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          if (idx >= 0 && idx < node.attrs.length) {
            node.attrs[idx].value = (ev.target as HTMLInputElement).value;
            dispatch("update", section);
            section = section;
            selectedItem.set($selectedItem);
          }
        }
      }
    }
  }

  function deleteAttribute(ev: Event, idx: number) {
    ev.preventDefault();
  }
</script>

<div class="flex flex-row w-full h-full overflow-auto">
  <div class="w-1/4 overflow-auto border-r border-gray-300">
    {#if section}
      <Toolbar.Root class="border-b border-gray-300">
        <Toolbar.Button title="Add a metadata node" on:click={addNewNode}>
          <Icon path={mdiPlus} />
        </Toolbar.Button>
        <Separator.Root class="border-r border-gray-300 mx-2" />
        <Toolbar.Button
          title="Move the selected metadata node up"
          aria-disabled={$selectedNode !== null ? null : "true"}
          on:click={moveSelectedNodeUp}
        >
          <Icon path={mdiChevronUp} />
        </Toolbar.Button>
        <Toolbar.Button
          title="Move the selected metadata node down"
          aria-disabled={$selectedNode !== null ? null : "true"}
          on:click={moveSelectedNodeDown}
        >
          <Icon path={mdiChevronDown} />
        </Toolbar.Button>
        <Toolbar.Button
          title="Remove the selected metadata node"
          aria-disabled={$selectedNode !== null ? null : "true"}
          on:click={deleteSelectedNode}
        >
          <Icon path={mdiTrashCan} />
        </Toolbar.Button>
        <div class="flex-1" />
        <Toolbar.Button
          title="Clear the selection"
          aria-disabled={$selectedNode !== null ? null : "true"}
          on:click={() => {
            selectedItem.set(null);
          }}
        >
          <Icon path={mdiCancel} />
        </Toolbar.Button>
      </Toolbar.Root>
      <ol {...$tree}>
        <Tree treeItems={section.content} />
      </ol>
    {/if}
  </div>
  <div class="flex-1 px-2 py-1">
    {#if $selectedNode}
      <label class="block mb-2">
        <span data-form-field-label>Tag</span>
        <input
          type="text"
          value={$selectedNode.type}
          data-form-field-text
          on:change={updateTag}
        />
      </label>
      <label class="block mb-2">
        <span data-form-field-label>Text</span>
        <input
          type="text"
          value={$selectedNode.text}
          data-form-field-text
          on:change={updateText}
        />
      </label>
      {#each $selectedNode.attrs as attr, idx}
        <div class="flex flex-row mb-2">
          <label class="flex-1">
            <span data-form-field-label>Name</span>
            <input
              type="text"
              value={attr.type}
              data-form-field-text
              on:change={(ev) => {
                updateAttributeName(ev, idx);
              }}
            />
          </label>
          <label class="flex-1">
            <span data-form-field-label>Value</span>
            <input
              type="text"
              value={attr.value}
              data-form-field-text
              on:change={(ev) => {
                updateAttributeValue(ev, idx);
              }}
            />
          </label>
          <Toolbar.Root class="border-b border-gray-300">
            <Toolbar.Button
              title="Move the selected metadata node up"
              aria-disabled={$selectedNode !== null ? null : "true"}
              on:click={(ev) => {
                deleteAttribute(ev, idx);
              }}
            >
              <Icon path={mdiTrashCan} />
            </Toolbar.Button>
          </Toolbar.Root>
        </div>
      {/each}
      <Toolbar.Root>
        <div class="flex-1"></div>
        <Toolbar.Button title="Add a metadata node" on:click={addAttribute}>
          <Icon path={mdiPlus} />
        </Toolbar.Button>
      </Toolbar.Root>
    {:else}
      <p>Please select a metadata node on the left</p>
    {/if}
  </div>
</div>
