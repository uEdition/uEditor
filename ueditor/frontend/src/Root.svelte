<script lang="ts">
  import { Dialog } from "bits-ui";
  import { setContext } from "svelte";
  import { derived } from "svelte/store";
  import { fade } from "svelte/transition";
  import { createQuery } from "@tanstack/svelte-query";

  import Actions from "./lib/actions/Index.svelte";
  import Dialogs from "./lib/dialogs/Index.svelte";
  import Editor from "./lib/editors/Index.svelte";
  import FileNavigation from "./lib/FileNavigation.svelte";
  import MainMenu from "./lib/mainmenu/Index.svelte";
  import Toolbar from "./lib/Toolbar.svelte";
  import { apiQueryHandler } from "./util";
  import { currentFile, currentFileModified } from "./stores";

  const uEditionConfig = createQuery({
    queryKey: ["configs", "uedition"],
    queryFn: apiQueryHandler<UEditionSettings>,
  });
  setContext("uEditionConfig", uEditionConfig);
  const uEditorConfig = createQuery({
    queryKey: ["configs", "ueditor"],
    queryFn: apiQueryHandler<UEditorSettings>,
  });
  setContext("uEditorConfig", uEditorConfig);

  const appTitle = derived(uEditionConfig, (config) => {
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
</script>

<svelte:head>
  <title>{$appTitle}</title>
</svelte:head>

<main class="flex flex-col w-screen h-screen overflow-hidden">
  <MainMenu />
  <Toolbar />
  <div class="flex flex-row flex-1 overflow-hidden">
    <FileNavigation />
    <Editor />
  </div>
  <footer class="flex flex-row px-2 py-1 border-t border-slate-300 text-sm">
    <div class="font-mono font-bold">
      {#if $currentFile}{$currentFile.fullpath}{/if}
    </div>
    <div class="flex-1"></div>
    <Actions />
  </footer>
</main>

<Dialogs />

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
