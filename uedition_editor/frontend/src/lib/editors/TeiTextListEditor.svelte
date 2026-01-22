<script lang="ts">
  import { Toolbar, Dialog } from "bits-ui";
  import { mdiPlus, mdiTrashCan } from "@mdi/js";
  import { v1 as uuidv1 } from "uuid";

  import Icon from "../Icon.svelte";
  import TeiTextEditor from "./TeiTextEditor.svelte";
  import { textForFirstNodeOfTipTapDocument } from "../../util";
  import { appState } from "../../state.svelte";

  type TeiTextListEditorProps = {
    sectionName: string;
    sectionConfig: UEditorTEITextListSection;
    sectionContent: TEITextlistSection;
    editorState: TEIEditorState;
    jumpToTextlistDocument: (sectionName: string, documentId: string) => void;
  };

  const {
    sectionName,
    sectionConfig,
    sectionContent,
    editorState,
    jumpToTextlistDocument,
  }: TeiTextListEditorProps = $props();

  let selectedTextId: string | null = $state(null);
  let selectedText: any = $state(null);
  let showDeleteText: boolean = $state(false);

  $effect(() => {
    if (selectedTextId !== null) {
      selectedText = null;
      for (const text of sectionContent.content) {
        if (text.attrs["id"] === selectedTextId) {
          selectedText = text;
        }
      }
    }
  });

  $effect(() => {
    if (editorState.selectTextlistId !== null) {
      for (const text of sectionContent.content) {
        if (text.attrs["id"] === editorState.selectTextlistId) {
          selectedTextId = editorState.selectTextlistId;
          editorState.selectTextlistId = null;
          break;
        }
      }
      if (editorState.selectTextlistId !== null) {
        addText(editorState.selectTextlistId);
        editorState.selectTextlistId = null;
      }
    }
  });

  /**
   * Add a new text to the list of texts.
   *
   * The text's structure is taken from the first block configured.
   */
  function addText(newTextId: string | undefined) {
    if (appState.tei.blocks.length > 0) {
      const newText = {
        attrs: { id: newTextId ? newTextId : sectionName + "-" + uuidv1() },
        content: {
          type: "doc",
          content: [
            {
              type: appState.tei.blocks[0].name as string,
              attrs: {},
              content: [{ type: "text", marks: [], text: "New" }],
            },
          ],
        },
      } as TEITextlistDocument;
      sectionContent.content.push(newText);
      selectedTextId = newText.attrs.id;
    }
  }

  /**
   * Delete a text from the list of texts.
   *
   * @param ev The form submission event that triggers this.
   */
  function deleteText(ev: Event) {
    ev.preventDefault();
    showDeleteText = false;
    sectionContent.content = sectionContent.content.filter((text) => {
      return text.attrs.id !== selectedTextId;
    });
    selectedText = null;
    selectedTextId = "";
    editorState.notifyModified();
  }

  let sortedTexts = $derived.by(() => {
    const uEditionSections =
      appState.uEditionConfig?.sphinx_config?.tei?.sections;
    // Default sorter is simply alphabetical
    let sorter = (
      [aId, aText]: [string, string],
      [bId, bText]: [string, string]
    ) => {
      if (aText > bText) {
        return 1;
      } else if (aText < bText) {
        return -1;
      } else {
        return 0;
      }
    };
    if (uEditionSections) {
      for (const section of uEditionSections) {
        if (
          section.name == sectionName &&
          section.sort &&
          section.sort.selector &&
          section.sort.order
        ) {
          if (section.sort.order === "page,line-page,line") {
            // Sorter that understands page,line pairs
            sorter = (
              [aId, aText]: [string, string],
              [bId, bText]: [string, string]
            ) => {
              const aMatch = aText.match(/([0-9-,]+).*/);
              const bMatch = bText.match(/([0-9-,]+).*/);
              let aKey = [0];
              let bKey = [0];
              if (aMatch !== null) {
                aKey = [];
                aMatch[1].split(",").forEach((v) => {
                  v.split("-").forEach((v2) => {
                    aKey.push(parseInt(v2));
                  });
                });
              }
              if (bMatch !== null) {
                bKey = [];
                bMatch[1].split(",").forEach((v) => {
                  v.split("-").forEach((v2) => {
                    bKey.push(parseInt(v2));
                  });
                });
              }
              for (
                let idx = 0;
                idx < Math.max(aKey.length, bKey.length);
                idx++
              ) {
                if (idx < aKey.length && idx < bKey.length) {
                  if (aKey[idx] > bKey[idx]) {
                    return 1;
                  } else if (aKey[idx] < bKey[idx]) {
                    return -1;
                  }
                } else if (idx < aKey.length) {
                  return 1;
                } else if (idx < bKey.length) {
                  return -1;
                }
              }
              return 0;
            };
          } else if (section.sort.order === "numeric") {
            // Sort numerically by the first number found
            sorter = (
              [aId, aText]: [string, string],
              [bId, bText]: [string, string]
            ) => {
              const aMatch = aText.match(/([0-9]+).*/);
              const bMatch = bText.match(/([0-9]+).*/);
              if (
                aMatch !== null &&
                (bMatch === null || parseInt(aMatch[1]) > parseInt(bMatch[1]))
              ) {
                return 1;
              } else if (
                bMatch !== null &&
                (aMatch === null || parseInt(aMatch[1]) < parseInt(bMatch[1]))
              ) {
                return -1;
              } else {
                return 0;
              }
            };
          }
        }
      }
    }
    const texts: [string, string][] = [];
    for (const text of sectionContent.content) {
      texts.push([
        text.attrs["id"],
        textForFirstNodeOfTipTapDocument(text.content),
      ]);
    }
    texts.sort(sorter);
    return texts;
  });
</script>

<div class="flex flex-col w-full h-full overflow-hidden">
  <div
    class="flex flex-row items-center space-x-4 border-b border-gray-300 px-2 py-1"
  >
    <select bind:value={selectedTextId} data-combobox-input="">
      {#each sortedTexts as [tid, text]}
        <option value={tid}>{text}</option>
      {/each}
    </select>
    <Toolbar.Root>
      <Toolbar.Button
        aria-label="Add a text"
        title="Add a text"
        onclick={addText}
      >
        <Icon path={mdiPlus} />
      </Toolbar.Button>
      <Toolbar.Button
        aria-label="Delete the current text"
        title="Delete the current text"
        aria-disabled={selectedTextId === null ? "true" : null}
        onclick={() => {
          showDeleteText = true;
        }}
      >
        <Icon path={mdiTrashCan} />
      </Toolbar.Button>
    </Toolbar.Root>
  </div>
  <div class="flex-1 overflow-hidden">
    {#if selectedText !== null}
      {#key selectedText}
        <TeiTextEditor
          {sectionName}
          {sectionConfig}
          sectionContent={selectedText}
          {editorState}
          {jumpToTextlistDocument}
        />
      {/key}
    {/if}
  </div>
</div>

<Dialog.Root bind:open={showDeleteText}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Delete Text</Dialog.Title>
      <form data-dialog-content-area onsubmit={deleteText}>
        <p>
          Please confirm that you wish to delete the text {#if selectedText !== null}{textForFirstNodeOfTipTapDocument(
              selectedText.content
            )}{/if}.
        </p>
        <div data-dialog-buttons>
          <Dialog.Close type="button" data-button>Don't delete</Dialog.Close>
          <button type="submit" data-button>Delete</button>
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
