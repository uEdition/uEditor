<script lang="ts">
  import { Menubar } from "bits-ui";
  import { mdiPencil, mdiTrashCanOutline } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import { activeDialog, Dialogs } from "../dialogs/Index.svelte";
</script>

<Menubar.Menu>
  <Menubar.Trigger>File</Menubar.Trigger>
  <Menubar.Content>
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.FILE_RENAME);
      }}
    >
      <Icon path={mdiPencil} class="w-4 h-4"></Icon>
      <span>Rename</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.FILE_DELETE);
      }}
    >
      <Icon path={mdiTrashCanOutline} class="w-4 h-4"></Icon>
      <span>Delete</span>
    </Menubar.Item>
  </Menubar.Content>
</Menubar.Menu>
