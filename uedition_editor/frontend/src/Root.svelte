<script lang="ts">
  import type { CreateQueryResult } from "@tanstack/svelte-query";

  import ActivityIndicator from "./lib/actions/ActivityIndicator.svelte";
  import Dialogs from "./lib/dialogs/Index.svelte";
  import Editor from "./lib/editors/Index.svelte";
  import FileNavigation from "./lib/FileNavigation.svelte";
  import MainMenu from "./lib/mainmenu/Index.svelte";
  import Toolbar from "./lib/Toolbar.svelte";
  import { appState } from "./state.svelte";

  const appTitle = $derived.by(() => {
    if (
      appState.uEditionConfig?.languages &&
      appState.uEditionConfig?.languages.length > 0 &&
      appState.uEditionConfig?.languages[0].code &&
      appState.uEditionConfig?.title &&
      appState.uEditionConfig?.title[appState.uEditionConfig?.languages[0].code]
    ) {
      return (
        "μEditor - " +
        appState.uEditionConfig?.title[
          appState.uEditionConfig?.languages[0].code
        ]
      );
    } else {
      return "μEditor";
    }
  });

  const uEditorConfigTimestamp = $derived.by(() => {
    if (appState.uEditionConfig) {
      return new Date().getTime();
    } else {
      return new Date().getTime();
    }
  });
</script>

<svelte:head>
  <title>{appTitle}</title>
  <link
    rel="stylesheet"
    href="/api/branches/{appState.currentBranch
      ?.id}/configs/ui-stylesheet?timestamp={uEditorConfigTimestamp}"
  />
</svelte:head>

<main class="flex flex-col w-screen h-screen overflow-hidden">
  <MainMenu />
  <Toolbar />
  {#if appState.currentBranch !== null}
    <div class="flex flex-row flex-1 overflow-hidden">
      <FileNavigation />
      <Editor />
    </div>
  {:else}
    <div class="flex-1">
      <p class="px-4 py-2">
        Please select the branch you wish to work on from the μEditor menu.
      </p>
    </div>
  {/if}
  <footer
    class="flex flex-row space-x-4 px-2 py-1 border-t border-slate-300 text-sm items-center"
  >
    {#if appState.apiStatus?.git.protect_default_branch && appState.apiStatus?.git.default_branch === appState.currentBranch?.id}
      <div class="text-red-500">
        This branch is protected and cannot be edited directly
      </div>
    {/if}
    <div class="font-mono font-bold">
      {#if appState.currentFile !== null}{appState.currentFile.fullpath}{/if}
    </div>
    <div class="flex-1"></div>
    <ActivityIndicator />
  </footer>
</main>

<Dialogs />
