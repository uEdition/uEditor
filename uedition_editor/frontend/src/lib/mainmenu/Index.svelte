<script lang="ts">
  import { Menubar } from "bits-ui";

  import UEditorMenu from "./UEditorMenu.svelte";
  import FileMenu from "./FileMenu.svelte";
  import FolderMenu from "./FolderMenu.svelte";
  import UserMenu from "./UserMenu.svelte";
  import { appState } from "../../state.svelte";
</script>

<Menubar.Root class="border-b border-gray-300 px-2 pt-px">
  <UEditorMenu />
  {#if appState.currentFile !== null && (!appState.apiStatus?.git.protect_default_branch || appState.apiStatus?.git.default_branch !== appState.currentBranch?.id)}
    {#if appState.currentFile.type === "file"}
      <FileMenu />
    {:else if appState.currentFile.type === "folder"}
      <FolderMenu />
    {/if}
  {/if}
  <span class="flex-1"></span>
  <UserMenu />
</Menubar.Root>
