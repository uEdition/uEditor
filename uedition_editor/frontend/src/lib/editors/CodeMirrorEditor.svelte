<script lang="ts">
  import { LanguageSupport } from "@codemirror/language";
  import { markdown } from "@codemirror/lang-markdown";
  import { yaml } from "@codemirror/lang-yaml";
  import { json } from "@codemirror/lang-json";
  import CodeMirror from "svelte-codemirror-editor";
  import { useQueryClient } from "@tanstack/svelte-query";

  import LoadingIndicator from "../LoadingIndicator.svelte";
  import { runAction } from "../actions/util.svelte";
  import { appState } from "../../state.svelte";

  const queryClient = useQueryClient();
  let focusElement: HTMLHeadingElement | null = $state(null);
  let fileBranch: Branch | null = $state(null);
  let filePath: string | null = $state(null);
  let value: string | null = $state("");

  let lang: LanguageSupport | null = $derived.by(() => {
    if (appState.currentFile) {
      if (appState.currentFile.mimetype === "application/json") {
        return json();
      } else if (appState.currentFile.mimetype === "application/yaml") {
        return yaml();
      } else if (appState.currentFile.mimetype === "text/markdown") {
        return markdown();
      }
    }
    return null;
  });

  $effect(() => {
    if (appState.currentFile !== null) {
      if (
        fileBranch !== appState.currentBranch ||
        filePath !== appState.currentFile.fullpath
      ) {
        fileBranch = appState.currentBranch;
        filePath = appState.currentFile.fullpath;
        runAction({
          action: "LoadTextFile",
          branch: appState.currentBranch as Branch,
          filename: appState.currentFile.fullpath,
          callback: (data: string) => {
            value = data;
            appState.currentFileContent = data;
            appState.ui.currentFileModified = false;
          },
        });
      }
    }
  });

  function shortCutTracker(ev: KeyboardEvent) {
    if (appState.currentFile !== null && appState.currentFileContent !== null) {
      if (ev.key === "s" && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        if (
          !appState.apiStatus?.git.protect_default_branch ||
          appState.apiStatus?.git.default_branch !== appState.currentBranch?.id
        ) {
          runAction({
            action: "SaveCurrentFile",
            branch: appState.currentBranch as Branch,
            filename: appState.currentFile.fullpath,
            data: appState.currentFileContent,
            callback() {
              appState.ui.currentFileModified = false;
              if (
                appState.currentFile !== null &&
                (appState.currentFile.name === "uEdition.yml" ||
                  appState.currentFile.name === "uEdition.yaml" ||
                  appState.currentFile.name === "uEditor.yml" ||
                  appState.currentFile.name === "uEditor.yaml")
              ) {
                queryClient.invalidateQueries({ queryKey: ["configs"] });
              }
            },
          });
        }
      }
    }
  }

  $effect(() => {
    appState.ui.currentFileModified = appState.currentFileContent !== value;
  });

  // onDestroy(() => {
  //   currentFileUnsubscribe();
  //   currentFileContentUnsubscribe();
  //   value = null;
  // });

  // $: {
  //   if ($currentFileContent !== value) {
  //     currentFileModified.set(true);
  //   }
  //   currentFileContent.set(value);
  // }
</script>

{#if value === null}
  <LoadingIndicator />
{:else}
  <div
    onkeydown={shortCutTracker}
    bind:this={focusElement}
    class="flex-1 overflow-hidden"
    tabindex="-1"
  >
    <span class="sr-only"
      >In the editor the Tab key will indent the text content. To escape the
      editor with the keyboard press the Escape key, followed by the Tab key.</span
    >
    <CodeMirror bind:value={appState.currentFileContent} {lang} />
  </div>
{/if}
