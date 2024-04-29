<script lang="ts">
  import { Dialog, Menubar } from "bits-ui";
  import { mdiSourceBranchPlus } from "@mdi/js";

  import Icon from "../Icon.svelte";

  let newBranchDialogOpen = false;
</script>

<Menubar.Menu>
  <Menubar.Trigger>μEditor</Menubar.Trigger>
  <Menubar.Content>
    <Menubar.Item
      on:click={() => {
        newBranchDialogOpen = true;
      }}
    >
      <Icon path={mdiSourceBranchPlus} class="w-4 h-4"></Icon>
      <span>New Branch</span>
    </Menubar.Item>
    <Menubar.Separator></Menubar.Separator>
    <Menubar.Item>
      <Icon class="w-4 h-4"></Icon>
      <span>Branch 1</span>
    </Menubar.Item>
    <Menubar.Item>
      <Icon class="w-4 h-4"></Icon>
      <span>Branch 2</span>
    </Menubar.Item>
  </Menubar.Content>
</Menubar.Menu>

<Dialog.Root bind:open={newBranchDialogOpen}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Create a new Branch</Dialog.Title>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
