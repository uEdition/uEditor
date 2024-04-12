<script lang="ts">
  import { Menubar, Dialog } from "bits-ui";
  import { mdiSourceBranchPlus } from "@mdi/js";

  import Icon from "./lib/Icon.svelte";

  let newBranchDialogOpen = false;
</script>

<svelte:head>
  <title>μEditor</title>
</svelte:head>

<main class="flex flex-col w-screen h-screen overflow-hidden">
  <Menubar.Root class="border-b border-slate-300 px-2 pt-px">
    <Menubar.Menu>
      <Menubar.Trigger>μEditor</Menubar.Trigger>
      <Menubar.Content>
        <Menubar.Item
          on:click={() => {
            newBranchDialogOpen = true;
          }}
        >
          <Icon path={mdiSourceBranchPlus} size="w-4 h-4"></Icon>
          <span>New Branch</span>
        </Menubar.Item>
        <Menubar.Separator></Menubar.Separator>
        <Menubar.Item>
          <Icon size="w-4 h-4"></Icon>
          <span>Branch 1</span>
        </Menubar.Item>
        <Menubar.Item>
          <Icon size="w-4 h-4"></Icon>
          <span>Branch 2</span>
        </Menubar.Item>
      </Menubar.Content>
    </Menubar.Menu>
  </Menubar.Root>
  <!--<nav aria-label="Toolbar" class="bg-blue-100">Editor Toolbar</nav>-->
  <div class="flex flex-row flex-1">
    <nav aria-label="Files" class="w-3/12 bg-red-100">Navigation</nav>
    <div class="flex-1 bg-green-100">Editor Content</div>
    <div class="w-3/12 bg-orange-100">Editor Sidebar</div>
  </div>
  <footer class="bg-yellow-100">Editor footer</footer>
</main>

<Dialog.Root bind:open={newBranchDialogOpen}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Create a new Branch</Dialog.Title>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
