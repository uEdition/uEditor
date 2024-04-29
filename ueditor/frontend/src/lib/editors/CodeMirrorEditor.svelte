<script lang="ts">
  import { LanguageSupport } from "@codemirror/language";
  import { markdown } from "@codemirror/lang-markdown";
  import { yaml } from "@codemirror/lang-yaml";
  import { onDestroy } from "svelte";
  import CodeMirror from "svelte-codemirror-editor";

  import LoadingIndicator from "../LoadingIndicator.svelte";
  import {
    currentBranch,
    currentFile,
    currentFileContent,
    currentFileModified,
  } from "../../stores";
  import { runAction } from "../actions/Index.svelte";

  let focusElement: HTMLHeadingElement | null = null;
  let value: string | null = "";
  let lang: LanguageSupport | null = null;

  const currentFileUnsubscribe = currentFile.subscribe((currentFile) => {
    if (currentFile) {
      if (currentFile.mimetype === "application/yaml") {
        lang = yaml();
      } else if (currentFile.mimetype === "text/markdown") {
        lang = markdown();
      } else {
        lang = null;
      }
      runAction({
        action: "LoadTextFile",
        branch: $currentBranch,
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
  <div bind:this={focusElement} class="flex-1 overflow-hidden" tabindex="-1">
    <span class="sr-only"
      >In the editor the Tab key will indent the text content. To escape the
      editor with the keyboard press the Escape key, followed by the Tab key.</span
    >
    <CodeMirror bind:value {lang} />
  </div>
{/if}
