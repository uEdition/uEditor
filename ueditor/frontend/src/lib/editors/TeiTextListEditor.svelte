<script lang="ts">
  import { Combobox, Toolbar } from "bits-ui";
  import { mdiPlus, mdiTrashCan } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import TeiTextEditor from "./TeiTextEditor.svelte";

  let selected: { value: unknown; label?: string } = { value: null };
</script>

<div class="flex flex-col w-full h-full overflow-hidden">
  <div
    class="flex flex-row items-center space-x-4 border-b border-gray-300 px-2 py-1"
  >
    <Combobox.Root
      items={[{ value: "1" }, { value: "2" }, { value: "3" }, { value: "4" }]}
      bind:selected
    >
      <Combobox.Input
        placeholder="Select the text to edit"
        aria-label="Select the text to edit"
      />
      <Combobox.Content>
        <Combobox.Item value="1" label="Text 1">Text 1</Combobox.Item>
        <Combobox.Item value="2" label="Text 2">Text 2</Combobox.Item>
        <Combobox.Item value="3" label="Text 3">Text 3</Combobox.Item>
        <Combobox.Item value="4" label="Text 4">Text 4</Combobox.Item>
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
