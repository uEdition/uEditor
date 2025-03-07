<script lang="ts">
  import { Menubar } from "bits-ui";

  import UEditorMenu from "./UEditorMenu.svelte";
  import FileMenu from "./FileMenu.svelte";
  import FolderMenu from "./FolderMenu.svelte";
  import { currentFile } from "../../stores";
  import UserMenu from "./UserMenu.svelte";
</script>

<Menubar.Root class="border-b border-gray-300 px-2 pt-px">
  <UEditorMenu />
  {#if $currentFile}
    {#if $currentFile.type === "file"}
      <FileMenu />
    {:else if $currentFile.type === "folder"}
      <FolderMenu />
    {/if}
  {/if}
  <span class="flex-1"></span>
  <UserMenu />
</Menubar.Root>
