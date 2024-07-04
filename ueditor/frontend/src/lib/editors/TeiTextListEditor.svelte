<script lang="ts">
  import { Combobox, Toolbar, Dialog } from "bits-ui";
  import { mdiChevronDown, mdiChevronUp, mdiPlus, mdiTrashCan } from "@mdi/js";
  import { createEventDispatcher, getContext } from "svelte";
  import type { CreateQueryResult } from "@tanstack/svelte-query";
  import { v1 as uuidv1 } from "uuid";

  import Icon from "../Icon.svelte";
  import TeiTextEditor from "./TeiTextEditor.svelte";
  import { textForFirstNodeOfTipTapDocument } from "../../util";

  export let section: TEITextlistSection | null = null;
  export let sections: TEIDocument;

  const dispatch = createEventDispatcher();
  const uEditorConfig = getContext(
    "uEditorConfig",
  ) as CreateQueryResult<UEditorSettings>;
  let selected: { value: unknown; label?: string } = { value: null };
  let texts = [] as TEITextlistDocument[];
  let selectedDocument: TEITextSection | null = null;
  let showDeleteText = false;

  $: if (section !== null) {
    texts = section.content;
  } else {
    texts = [];
  }

  $: if (selected.value !== null && section) {
    const tmp = texts.filter((text) => {
      return text.attrs.id === selected.value;
    });
    if (tmp.length === 1) {
      selectedDocument = {
        name: "",
        title: "",
        type: {
          name: "",
          title: "",
          type: "text",
          selector: "",
          sidebar: section.type.sidebar,
        },
        content: tmp[0].content,
      };
    } else {
      selectedDocument = null;
    }
  } else {
    selectedDocument = null;
  }

  /**
   * Update the selected document.
   *
   * @param ev The combobox event triggering the update.
   */
  function updateSelected(ev: CustomEvent) {
    if (selected.value !== null && section) {
      const tmp = texts.filter((text) => {
        return text.attrs.id === selected.value;
      });
      if (tmp.length === 1) {
        tmp[0].content = ev.detail;
      }
      dispatch("update", texts);
    }
  }

  /**
   * Add a new text to the list of texts.
   *
   * The text's structure is taken from the first block configured.
   */
  function addText() {
    if (
      $uEditorConfig.isSuccess &&
      $uEditorConfig.data?.tei.blocks.length > 0
    ) {
      texts.push({
        attrs: { id: section?.name + "-" + uuidv1() },
        content: {
          type: "doc",
          content: [
            {
              type: $uEditorConfig.data.tei.blocks[0].name as string,
              attrs: {},
              content: [{ type: "text", marks: [], text: "New" }],
            },
          ],
        },
      });
      dispatch("update", texts);
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
    let selectedIdx = -1;
    for (let idx = 0; idx < texts.length; idx++) {
      if (selected.value == texts[idx].attrs.id) {
        selectedIdx = idx;
        break;
      }
    }
    if (selectedIdx >= 0) {
      texts.splice(selectedIdx, 1);
      selected = { value: null };
      selectedDocument = null;
      dispatch("update", texts);
    }
  }
</script>

<div class="flex flex-col w-full h-full overflow-hidden">
  <div
    class="flex flex-row items-center space-x-4 border-b border-gray-300 px-2 py-1"
  >
    <Combobox.Root
      items={texts.map((text) => {
        return {
          value: text.attrs["id"],
          label: textForFirstNodeOfTipTapDocument(text.content),
        };
      })}
      bind:selected
    >
      <div class="relative">
        <Combobox.Input
          placeholder="Select the text to edit"
          aria-label="Select the text to edit"
          class="relative pr-6 z-10 bg-transparent"
        />
        <div class="absolute top-1/2 right-0 -translate-y-1/2">
          <Icon path={mdiChevronDown} class="w-6 h-6 combobox-expand" />
          <Icon path={mdiChevronUp} class="w-6 h-6 combobox-collapse" />
        </div>
      </div>
      <Combobox.Content>
        {#each texts as text}
          <Combobox.Item
            value={text.attrs["id"]}
            label={textForFirstNodeOfTipTapDocument(text.content)}
            >{textForFirstNodeOfTipTapDocument(text.content)}</Combobox.Item
          >
        {/each}
      </Combobox.Content>
    </Combobox.Root>
    <Toolbar.Root>
      <Toolbar.Button
        on:click={addText}
        aria-label="Add a text"
        title="Add a text"
      >
        <Icon path={mdiPlus} />
      </Toolbar.Button>
      <Toolbar.Button
        on:click={() => {
          showDeleteText = true;
        }}
        aria-label="Delete the current text"
        title="Delete the current text"
        aria-disabled={selected.value === null ? "true" : null}
      >
        <Icon path={mdiTrashCan} />
      </Toolbar.Button>
    </Toolbar.Root>
  </div>
  <div class="flex-1 overflow-hidden">
    {#if selectedDocument !== null}
      <TeiTextEditor
        section={selectedDocument}
        {sections}
        on:update={updateSelected}
      />
    {/if}
  </div>
</div>

<Dialog.Root bind:open={showDeleteText}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Delete Text</Dialog.Title>
      <form data-dialog-content-area on:submit={deleteText}>
        <p>
          Please confirm that you wish to delete the text {selected.label}.
        </p>
        <div data-dialog-buttons>
          <Dialog.Close data-button>Don't delete</Dialog.Close>
          <button type="submit" data-button>Delete</button>
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
