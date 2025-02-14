<script lang="ts">
  import { getContext } from "svelte";
  import { derived, type Readable } from "svelte/store";
  import type { CreateQueryResult } from "@tanstack/svelte-query";

  import Actions from "./lib/actions/Index.svelte";
  import Dialogs from "./lib/dialogs/Index.svelte";
  import Editor from "./lib/editors/Index.svelte";
  import FileNavigation from "./lib/FileNavigation.svelte";
  import MainMenu from "./lib/mainmenu/Index.svelte";
  import Toolbar from "./lib/Toolbar.svelte";
  import { currentFile } from "./stores";

  const uEditionConfig = getContext(
    "uEditionConfig",
  ) as CreateQueryResult<UEditionSettings>;
  const uEditorConfig = getContext(
    "uEditorConfig",
  ) as CreateQueryResult<UEditorSettings>;
  const currentBranch = getContext("currentBranch") as Readable<Branch | null>;

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

  const uEditorConfigTimestamp = derived(uEditionConfig, (uEditorConfig) => {
    return new Date().getTime();
  });
</script>

<svelte:head>
  <title>{$appTitle}</title>
  <link
    rel="stylesheet"
    href="/api/branches/{$currentBranch !== null
      ? $currentBranch.id
      : '-'}/configs/ui-stylesheet?timestamp={$uEditorConfigTimestamp}"
  />
</svelte:head>

<main class="flex flex-col w-screen h-screen overflow-hidden">
  <MainMenu />
  <Toolbar />
  {#if $currentBranch !== null && $uEditorConfig.isSuccess}
    <div class="flex flex-row flex-1 overflow-hidden">
      <FileNavigation />
      <Editor />
    </div>
  {:else if $currentBranch === null}
    <div class="flex-1">
      <p class="px-4 py-2">
        Please select the branch you wish to work on from the File menu.
      </p>
    </div>
  {:else}
    <div class="flex-1"></div>
  {/if}
  <footer class="flex flex-row px-2 py-1 border-t border-slate-300 text-sm">
    <div class="font-mono font-bold">
      {#if $currentFile}{$currentFile.fullpath}{/if}
    </div>
    <div class="flex-1"></div>
    <Actions />
  </footer>
</main>

<Dialogs />
