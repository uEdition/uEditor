<script lang="ts">
  import { Menubar } from "bits-ui";

  import UEditorMenu from "./UEditorMenu.svelte";
  import FileMenu from "./FileMenu.svelte";
  import FolderMenu from "./FolderMenu.svelte";
  import { currentFile, useApiStatus, useCurrentBranch } from "../../stores";
  import UserMenu from "./UserMenu.svelte";

  const apiStatus = useApiStatus();
  const currentBranch = useCurrentBranch();
</script>

<Menubar.Root class="border-b border-gray-300 px-2 pt-px">
  <UEditorMenu />
  {#if $currentFile && (!$apiStatus.data?.git.protect_default_branch || $apiStatus.data?.git.default_branch !== $currentBranch?.id)}
    {#if $currentFile.type === "file"}
      <FileMenu />
    {:else if $currentFile.type === "folder"}
      <FolderMenu />
    {/if}
  {/if}
  <span class="flex-1"></span>
  <UserMenu />
</Menubar.Root>
