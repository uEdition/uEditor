<script lang="ts">
  import { LanguageSupport } from "@codemirror/language";
  import { markdown } from "@codemirror/lang-markdown";
  import { yaml } from "@codemirror/lang-yaml";
  import { onMount, onDestroy } from "svelte";
  import { derived } from "svelte/store";
  import CodeMirror from "svelte-codemirror-editor";
  import { createQuery } from "@tanstack/svelte-query";

  import LoadingIndicator from "../LoadingIndicator.svelte";
  import { currentBranch, currentFile, currentFileContent, currentFileModified } from "../../stores";
  import { fileQueryHandler } from "../../util";

  let focusElement: HTMLHeadingElement | null = null;
  let value: string | null = "";
  let lang: LanguageSupport | null = null;

  const fileContentQueryParams = derived(currentFile, (currentFile) => {
    if (currentFile) {
      if (currentFile.mimetype === "application/yaml") {
        lang = yaml();
      } else if (currentFile.mimetype === "text/markdown") {
        lang = markdown();
      }
    } else {
      lang = null;
    }
    return {
      queryKey: ["branches", $currentBranch, "files", currentFile?.fullpath],
      queryFn: fileQueryHandler,
      enabled: currentFile?.type === "file",
    };
  });

  const fileContentQuery = createQuery(fileContentQueryParams);

  const fileContentQueryUnsubscribe = fileContentQuery.subscribe(
    (fileContentQuery) => {
      value = null;
      if (fileContentQuery.isSuccess) {
        const decoder = new TextDecoder();
        value = decoder.decode(fileContentQuery.data);
      }
    },
  );

  onMount(() => {
    if (focusElement) {
      focusElement.focus();
    }
  });

  onDestroy(fileContentQueryUnsubscribe);

  $: {
    if (value !== null) {
      currentFileContent.update((currentValue) => {
        if (currentValue !== null && currentValue !== value) {
          currentFileModified.set(true);
        } else {
          currentFileModified.set(false);
        }
        return value;
      });
    } else {
      currentFileContent.set(null);
      currentFileModified.set(false);
    }
  }
</script>

{#if $fileContentQuery.isLoading}
  <LoadingIndicator />
{:else if value !== null}
  <div bind:this={focusElement} class="flex-1 overflow-hidden" tabindex="-1">
    <span class="sr-only"
      >In the editor the Tab key will indent the text content. To escape the
      editor with the keyboard press the Escape key, followed by the Tab key.</span
    >
    <CodeMirror bind:value {lang} />
  </div>
  {:else}
  <div bind:this={focusElement} class="flex-1 overflow-hidden" tabindex="-1">
    <p class="text-rose-700">Unfortunately the file could not be loaded into the text editor.</p>
  </div>
{/if}
