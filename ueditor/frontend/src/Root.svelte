<script lang="ts">
  import { Menubar, Dialog } from "bits-ui";
  import { mdiSourceBranchPlus } from "@mdi/js";
  import { derived } from "svelte/store";
  import { fade } from "svelte/transition";
  import { createQuery } from "@tanstack/svelte-query";

  import Icon from "./lib/Icon.svelte";
  import { apiQueryHandler } from "./util";

  const uEditionConfig = createQuery({
    queryKey: ["/configs/uedition"],
    queryFn: apiQueryHandler<UEditionSettings>,
  });

  const appTitle = derived(uEditionConfig, (config) => {
    console.log(config.data);
    if (
      config.isSuccess &&
      config.data.languages &&
      config.data.languages.length > 0 &&
      config.data.languages[0].code &&
      config.data.title &&
      config.data.title[config.data.languages[0].code]
    ) {
      return "μEditor - " + config.data.title[config.data.languages[0].code];
    }
    return "μEditor";
  });

  let newBranchDialogOpen = false;
</script>

<svelte:head>
  <title>{$appTitle}</title>
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

<Dialog.Root
  bind:open={$uEditionConfig.isPending}
  closeOnEscape={false}
  closeOnOutsideClick={false}
>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay transition={fade} />
    <Dialog.Content class="flex flex-col overflow-hidden">
      <Dialog.Title>Loading the Configuration</Dialog.Title>
      <div data-dialog-content-area>
        <p>The configuration is being loaded. Please wait...</p>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root
  bind:open={$uEditionConfig.isError}
  closeOnEscape={false}
  closeOnOutsideClick={false}
>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay transition={fade} />
    <Dialog.Content class="flex flex-col overflow-hidden">
      <Dialog.Title class="bg-rose-700"
        >Loading the Configuration Failed</Dialog.Title
      >
      <div data-dialog-content-area>
        <p>
          Unfortunately loading the configuration failed. Please check the error
          messages on the console to see what the problem is.
        </p>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
