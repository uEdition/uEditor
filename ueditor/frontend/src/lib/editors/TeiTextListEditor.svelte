<script lang="ts">
  import { Combobox, Toolbar } from "bits-ui";
  import { mdiChevronDown, mdiChevronUp, mdiPlus, mdiTrashCan } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import TeiTextEditor from "./TeiTextEditor.svelte";

  let selected: { value: unknown; label?: string } = { value: null };
  export let section: any = null;
  let texts = [] as any[];

  $: {
    texts = section.content;
    console.log(texts);
  }
</script>

<div class="flex flex-col w-full h-full overflow-hidden">
  <div
    class="flex flex-row items-center space-x-4 border-b border-gray-300 px-2 py-1"
  >
    <Combobox.Root
      items={texts.map((text) => {
        return {
          value: text.attributes["{http://www.w3.org/XML/1998/namespace}id"],
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
            value={text.attributes["{http://www.w3.org/XML/1998/namespace}id"]}
            >{text.attributes[
              "{http://www.w3.org/XML/1998/namespace}id"
            ]}</Combobox.Item
          >
        {/each}
      </Combobox.Content>
    </Combobox.Root>
    <Toolbar.Root>
      <Toolbar.Button aria-label="Add a text" title="Add a text">
        <Icon path={mdiPlus} />
      </Toolbar.Button>
      <Toolbar.Button
        aria-label="Delete the current text"
        title="Delete the current text"
        aria-disabled={selected.value === null ? "true" : null}
      >
        <Icon path={mdiTrashCan} />
      </Toolbar.Button>
    </Toolbar.Root>
  </div>
  <div class="flex-1 overflow-hidden">
    <TeiTextEditor />
  </div>
</div>
