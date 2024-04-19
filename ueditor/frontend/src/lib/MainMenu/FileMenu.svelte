<script lang="ts">
  import { Dialog, Menubar } from "bits-ui";
  import { mdiPencil, mdiTrashCanOutline } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import { currentFile } from "../../stores";

  let renameDialogOpen = false;
  let deleteDialogOpen = false;
</script>

<Menubar.Menu>
  <Menubar.Trigger>File</Menubar.Trigger>
  <Menubar.Content>
    <Menubar.Item
      on:click={() => {
        renameDialogOpen = true;
      }}
    >
      <Icon path={mdiPencil} size="w-4 h-4"></Icon>
      <span>Rename</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        deleteDialogOpen = true;
      }}
    >
      <Icon path={mdiTrashCanOutline} size="w-4 h-4"></Icon>
      <span>Delete</span>
    </Menubar.Item>
  </Menubar.Content>
</Menubar.Menu>

<Dialog.Root bind:open={renameDialogOpen}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>
        Rename <span class="font-mono">{$currentFile?.fullpath}</span>
      </Dialog.Title>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root bind:open={deleteDialogOpen}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>
        Delete <span class="font-mono">{$currentFile?.fullpath}</span>
      </Dialog.Title>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
