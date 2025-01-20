<script lang="ts">
  import { Menubar } from "bits-ui";
  import {
    mdiFileDocumentPlusOutline,
    mdiFileUploadOutline,
    mdiFolderEditOutline,
    mdiFolderPlusOutline,
    mdiFolderRemoveOutline,
  } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import { activeDialog, Dialogs } from "../dialogs/Index.svelte";
  import DirectoryDelete from "../dialogs/folder/Delete.svelte";

  enum Action {
    Nothing = 1,
    Rename,
    Move,
    Copy,
    Delete,
  }

  let action: Action = Action.Nothing;
</script>

<Menubar.Menu>
  <Menubar.Trigger>Folder</Menubar.Trigger>
  <Menubar.Content>
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.FOLDER_CREATE);
      }}
    >
      <Icon path={mdiFolderPlusOutline} class="w4 h-4" />
      <span>New Folder</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.FILE_CREATE);
      }}
    >
      <Icon path={mdiFileDocumentPlusOutline} class="w4 h-4" />
      <span>New File</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.FILE_UPLOAD);
      }}
    >
      <Icon path={mdiFileUploadOutline} class="w4 h-4" />
      <span>Upload Files</span>
    </Menubar.Item>
    <Menubar.Separator />
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.FOLDER_RENAME);
      }}
    >
      <Icon path={mdiFolderEditOutline} class="w-4 h-4"></Icon>
      <span>Rename</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.FOLDER_DELETE);
      }}
    >
      <Icon path={mdiFolderRemoveOutline} class="w-4 h-4"></Icon>
      <span>Delete</span>
    </Menubar.Item>
  </Menubar.Content>
</Menubar.Menu>

{#if action === Action.Delete}
  <DirectoryDelete
    on:close={() => {
      console.log("Resetting action");
      action = Action.Nothing;
    }}
  />
{/if}
