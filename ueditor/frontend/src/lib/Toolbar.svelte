<script lang="ts">
  import { Toolbar } from "bits-ui";
  import { mdiContentSave } from "@mdi/js";

  import Icon from "./Icon.svelte";
  import { currentFileContent, currentFileModified } from "../stores";
</script>

<Toolbar.Root class="flex flex-row border-b border-gray-300 px-2 py-1">
  <div class="flex items-center">
    <Toolbar.Button aria-label="Save" class="p-1 border-2 border-transparent rounded {$currentFileContent !== null && $currentFileModified ? 'text-black hover:border-fuchsia-700 focus:border-fuchsia-700' : 'text-gray-400 cursor-not-allowed'}">
      <Icon path={mdiContentSave}/>
    </Toolbar.Button>
  </div>
</Toolbar.Root>
