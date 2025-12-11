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
  import { appState, Dialogs } from "../../state.svelte";
</script>

<Menubar.Menu>
  <Menubar.Trigger>Folder</Menubar.Trigger>
  <Menubar.Content>
    <Menubar.Item
      onclick={() => {
        appState.activeDialog = Dialogs.FOLDER_CREATE;
      }}
    >
      <Icon path={mdiFolderPlusOutline} class="w4 h-4" />
      <span>New Folder</span>
    </Menubar.Item>
    <Menubar.Item
      onclick={() => {
        appState.activeDialog = Dialogs.FILE_CREATE;
      }}
    >
      <Icon path={mdiFileDocumentPlusOutline} class="w4 h-4" />
      <span>New File</span>
    </Menubar.Item>
    <Menubar.Item
      onclick={() => {
        appState.activeDialog = Dialogs.FILE_UPLOAD;
      }}
    >
      <Icon path={mdiFileUploadOutline} class="w4 h-4" />
      <span>Upload Files</span>
    </Menubar.Item>
    <Menubar.Separator />
    <Menubar.Item
      onclick={() => {
        appState.activeDialog = Dialogs.FOLDER_RENAME;
      }}
    >
      <Icon path={mdiFolderEditOutline} class="w-4 h-4"></Icon>
      <span>Rename</span>
    </Menubar.Item>
    <Menubar.Item
      onclick={() => {
        appState.activeDialog = Dialogs.FOLDER_DELETE;
      }}
    >
      <Icon path={mdiFolderRemoveOutline} class="w-4 h-4"></Icon>
      <span>Delete</span>
    </Menubar.Item>
  </Menubar.Content>
</Menubar.Menu>
