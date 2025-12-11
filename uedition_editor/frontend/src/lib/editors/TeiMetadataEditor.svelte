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
  import { onDestroy, setContext } from "svelte";

  import Tree from "./TeiMetadataTree.svelte";
  import Icon from "../Icon.svelte";

  type TeiMetadataEditorProps = {
    sectionName: string;
    editorState: TEIEditorState;
  };

  const { sectionName, editorState }: TeiMetadataEditorProps = $props();
  let selectedNode: TeiMetadataNode | null = $state(null);

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

  const selectedItemUnsubscribe = selectedItem.subscribe((selectedElement) => {
    if (selectedElement !== null && editorState.sections[sectionName]) {
      const dataId = selectedElement.getAttribute("data-id");
      selectedNode = null;
      if (dataId) {
        const node = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          selectedNode = node;
        }
      }
    } else {
      selectedNode = null;
    }
  });

  onDestroy(selectedItemUnsubscribe);

  /**
   * Update the tag name of the node.
   *
   * @param ev The event containing the new tag name.
   */
  function updateTag(ev: Event) {
    ev.preventDefault();
    if ($selectedItem !== null && editorState.sections[sectionName]) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          node.type = (ev.target as HTMLInputElement).value;
          editorState.notifyModified();
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
    if ($selectedItem !== null && editorState.sections[sectionName]) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          node.text = (ev.target as HTMLInputElement).value;
          editorState.notifyModified();
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
    if (editorState.sections[sectionName]) {
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
            editorState.sections[sectionName] as unknown as TeiMetadataNode,
            dataId,
          );
          if (node) {
            node.content.push(newNode);
            editorState.notifyModified();
          }
        }
      } else {
        editorState.sections[sectionName].content.push(newNode);
        editorState.notifyModified();
      }
    }
  }

  /**
   * Delete the selected node.
   *
   * @param ev The event that triggered this.
   */
  function deleteSelectedNode(ev: Event) {
    ev.preventDefault();
    if (editorState.sections[sectionName] && $selectedItem) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const idPath = dataId.split("-");
        const parentIdPath = idPath.slice(0, idPath.length - 1);
        const parent = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          parentIdPath.join("-"),
        );
        if (parent) {
          parent.content.splice(Number.parseInt(idPath[idPath.length - 1]), 1);
        } else {
          editorState.sections[sectionName].content.splice(
            Number.parseInt(idPath[idPath.length - 1]),
            1,
          );
        }
        editorState.notifyModified();
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
    if (editorState.sections[sectionName] && $selectedItem) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const idPath = dataId.split("-");
        const parentIdPath = idPath.slice(0, idPath.length - 1);
        const parent = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          parentIdPath.join("-"),
        );
        const selectedIdx = Number.parseInt(idPath[idPath.length - 1]);
        if (parent && selectedIdx > 0) {
          const removed = parent.content.splice(selectedIdx, 1);
          parent.content.splice(selectedIdx - 1, 0, ...removed);
          selectedItem.set(null);
        } else if (selectedIdx > 0) {
          const removed = editorState.sections[sectionName].content.splice(
            selectedIdx,
            1,
          );
          editorState.sections[sectionName].content.splice(
            selectedIdx - 1,
            0,
            ...removed,
          );
          selectedItem.set(null);
        }
        editorState.notifyModified();
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
    if (editorState.sections[sectionName] && $selectedItem) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const idPath = dataId.split("-");
        const parentIdPath = idPath.slice(0, idPath.length - 1);
        const parent = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          parentIdPath.join("-"),
        );
        const selectedIdx = Number.parseInt(idPath[idPath.length - 1]);
        if (parent && selectedIdx < parent.content.length - 1) {
          const removed = parent.content.splice(selectedIdx, 1);
          parent.content.splice(selectedIdx + 1, 0, ...removed);
          selectedItem.set(null);
        } else if (
          selectedIdx <
          editorState.sections[sectionName].content.length - 1
        ) {
          const removed = editorState.sections[sectionName].content.splice(
            selectedIdx,
            1,
          );
          editorState.sections[sectionName].content.splice(
            selectedIdx + 1,
            0,
            ...removed,
          );
          selectedItem.set(null);
        }
        editorState.notifyModified();
      }
    }
  }

  function addAttribute(ev: Event) {
    ev.preventDefault();
    if ($selectedItem !== null && editorState.sections[sectionName]) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          node.attrs.push({ type: "", value: "" });
          selectedItem.set($selectedItem);
          editorState.notifyModified();
        }
      }
    }
  }
  function updateAttributeName(ev: Event, idx: number) {
    ev.preventDefault();
    if ($selectedItem !== null && editorState.sections[sectionName]) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          if (idx >= 0 && idx < node.attrs.length) {
            node.attrs[idx].type = (ev.target as HTMLInputElement).value;
            selectedItem.set($selectedItem);
            editorState.notifyModified();
          }
        }
      }
    }
  }
  function updateAttributeValue(ev: Event, idx: number) {
    ev.preventDefault();
    if ($selectedItem !== null && editorState.sections[sectionName]) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          if (idx >= 0 && idx < node.attrs.length) {
            node.attrs[idx].value = (ev.target as HTMLInputElement).value;
            selectedItem.set($selectedItem);
            editorState.notifyModified();
          }
        }
      }
    }
  }

  function deleteAttribute(ev: Event, idx: number) {
    ev.preventDefault();
    if ($selectedItem !== null && editorState.sections[sectionName]) {
      const dataId = $selectedItem.getAttribute("data-id");
      if (dataId) {
        const node = findNodeByPath(
          editorState.sections[sectionName] as unknown as TeiMetadataNode,
          dataId,
        );
        if (node) {
          if (idx < node.attrs.length) {
            node.attrs.splice(idx, 1);
          }
          editorState.notifyModified();
        }
      }
    }
  }
</script>

<div class="flex flex-row w-full h-full overflow-auto">
  <div class="w-1/4 overflow-auto border-r border-gray-300">
    {#if editorState.sections[sectionName]}
      <Toolbar.Root class="border-b border-gray-300">
        <Toolbar.Button title="Add a metadata node" onclick={addNewNode}>
          <Icon path={mdiPlus} />
        </Toolbar.Button>
        <Separator.Root class="border-r border-gray-300 mx-2" />
        <Toolbar.Button
          title="Move the selected metadata node up"
          aria-disabled={selectedNode !== null ? null : "true"}
          onclick={moveSelectedNodeUp}
        >
          <Icon path={mdiChevronUp} />
        </Toolbar.Button>
        <Toolbar.Button
          title="Move the selected metadata node down"
          aria-disabled={selectedNode !== null ? null : "true"}
          onclick={moveSelectedNodeDown}
        >
          <Icon path={mdiChevronDown} />
        </Toolbar.Button>
        <Toolbar.Button
          title="Remove the selected metadata node"
          aria-disabled={selectedNode !== null ? null : "true"}
          onclick={deleteSelectedNode}
        >
          <Icon path={mdiTrashCan} />
        </Toolbar.Button>
        <div class="flex-1"></div>
        <Toolbar.Button
          title="Clear the selection"
          aria-disabled={selectedNode !== null ? null : "true"}
          onclick={() => {
            selectedItem.set(null);
          }}
        >
          <Icon path={mdiCancel} />
        </Toolbar.Button>
      </Toolbar.Root>
      <ol {...$tree}>
        <Tree treeItems={editorState.sections[sectionName].content} />
      </ol>
    {/if}
  </div>
  <div class="flex-1 px-2 py-1">
    {#if selectedNode}
      <label class="block mb-2">
        <span data-form-field-label>Tag</span>
        <input
          type="text"
          value={selectedNode.type}
          data-form-field-text
          onchange={updateTag}
        />
      </label>
      <label class="block mb-2">
        <span data-form-field-label>Text</span>
        <input
          type="text"
          value={selectedNode.text}
          data-form-field-text
          onchange={updateText}
        />
      </label>
      {#each selectedNode.attrs as attr, idx}
        <div class="flex flex-row mb-2">
          <label class="flex-1">
            <span data-form-field-label>Name</span>
            <input
              type="text"
              value={attr.type}
              data-form-field-text
              onchange={(ev) => {
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
              onchange={(ev) => {
                updateAttributeValue(ev, idx);
              }}
            />
          </label>
          <Toolbar.Root class="border-b border-gray-300">
            <Toolbar.Button
              title="Move the selected metadata node up"
              aria-disabled={selectedNode !== null ? null : "true"}
              onclick={(ev) => {
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
        <Toolbar.Button title="Add a metadata node" onclick={addAttribute}>
          <Icon path={mdiPlus} />
        </Toolbar.Button>
      </Toolbar.Root>
    {:else}
      <p>Please select a metadata node on the left</p>
    {/if}
  </div>
</div>
