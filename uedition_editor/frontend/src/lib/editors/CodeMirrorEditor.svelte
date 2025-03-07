<script lang="ts">
  import { LanguageSupport } from "@codemirror/language";
  import { markdown } from "@codemirror/lang-markdown";
  import { yaml } from "@codemirror/lang-yaml";
  import { json } from "@codemirror/lang-json";
  import { onDestroy } from "svelte";
  import CodeMirror from "svelte-codemirror-editor";
  import { useQueryClient } from "@tanstack/svelte-query";

  import LoadingIndicator from "../LoadingIndicator.svelte";
  import {
    currentFile,
    currentFileContent,
    currentFileModified,
    useCurrentBranch,
  } from "../../stores";
  import { runAction } from "../actions/Index.svelte";

  let focusElement: HTMLHeadingElement | null = null;
  let value: string | null = "";
  let lang: LanguageSupport | null = null;
  const queryClient = useQueryClient();
  const currentBranch = useCurrentBranch();

  const currentFileUnsubscribe = currentFile.subscribe((currentFile) => {
    if (currentFile) {
      if (currentFile.mimetype === "application/json") {
        lang = json();
      } else if (currentFile.mimetype === "application/yaml") {
        lang = yaml();
      } else if (currentFile.mimetype === "text/markdown") {
        lang = markdown();
      } else {
        lang = null;
      }
      runAction({
        action: "LoadTextFile",
        branch: $currentBranch as Branch,
        filename: currentFile.fullpath,
        callback: (data: string) => {
          value = data;
          currentFileContent.set(data);
          currentFileModified.set(false);
        },
      });
    } else {
      lang = null;
    }
  });
  const currentFileContentUnsubscribe = currentFileContent.subscribe(
    (content) => {
      value = content;
    }
  );

  function shortCutTracker(ev: KeyboardEvent) {
    if ($currentFile !== null && $currentFileContent !== null) {
      if (ev.key === "s" && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        runAction({
          action: "SaveCurrentFile",
          branch: $currentBranch as Branch,
          filename: $currentFile.fullpath,
          data: $currentFileContent,
          callback() {
            currentFileModified.set(false);
            if (
              $currentFile.name === "uEdition.yml" ||
              $currentFile.name === "uEdition.yaml" ||
              $currentFile.name === "uEditor.yml" ||
              $currentFile.name === "uEditor.yaml"
            ) {
              queryClient.invalidateQueries({ queryKey: ["configs"] });
            }
          },
        });
      }
    }
  }

  onDestroy(() => {
    currentFileUnsubscribe();
    currentFileContentUnsubscribe();
    value = null;
  });

  $: {
    if ($currentFileContent !== value) {
      currentFileModified.set(true);
    }
    currentFileContent.set(value);
  }
</script>

{#if value === null}
  <LoadingIndicator />
{:else}
  <div
    on:keydown={shortCutTracker}
    bind:this={focusElement}
    class="flex-1 overflow-hidden"
    tabindex="-1"
  >
    <span class="sr-only"
      >In the editor the Tab key will indent the text content. To escape the
      editor with the keyboard press the Escape key, followed by the Tab key.</span
    >
    <CodeMirror bind:value {lang} />
  </div>
{/if}
