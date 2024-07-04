<script lang="ts">
  import deepEql from "deep-eql";
  import type { CreateQueryResult } from "@tanstack/svelte-query";
  import { Tabs } from "bits-ui";
  import { getContext, onDestroy } from "svelte";
  import { derived } from "svelte/store";

  import { runAction } from "../actions/Index.svelte";
  import {
    currentBranch,
    currentFile,
    currentFileContent,
    currentFileModified,
  } from "../../stores";
  import LoadingIndicator from "../LoadingIndicator.svelte";
  import TeiMetadataEditor from "./TeiMetadataEditor.svelte";
  import TeiTextEditor from "./TeiTextEditor.svelte";
  import TeiTextListEditor from "./TeiTextListEditor.svelte";

  let updatedDocument: TEIDocument = [];
  let updateDebounce = -1;
  let initialDocument: TEIDocument = [];

  const uEditorConfig = getContext(
    "uEditorConfig",
  ) as CreateQueryResult<UEditorSettings>;

  const teiDocument = derived(
    [uEditorConfig, currentFile],
    ([uEditorConfig, currentFile], set) => {
      if (
        uEditorConfig.isSuccess &&
        currentFile &&
        currentFile.name.endsWith(".tei")
      ) {
        runAction({
          action: "LoadTextFile",
          branch: $currentBranch,
          filename: currentFile.fullpath,
          callback: (data: string) => {
            currentFileContent.set(data);
            currentFileModified.set(false);
            updatedDocument = JSON.parse(data);
            initialDocument = JSON.parse(data);
            const tmpDocument = JSON.parse(data);
            const newSections: TEIDocument = [];
            for (let section of uEditorConfig.data.tei.sections) {
              for (let part of tmpDocument) {
                if (section.name === part.name) {
                  part.type = section;
                  newSections.push(part);
                  break;
                }
              }
            }
            set(newSections);
          },
        });
      }
    },
    null as null | TEIDocument,
  );

  const currentFileModifiedUnsubscribe = currentFileModified.subscribe(
    (currentFileModified) => {
      if (!currentFileModified && $currentFileContent) {
        try {
          initialDocument = JSON.parse($currentFileContent);
        } catch (e) {}
      }
    },
  );

  function updateDocumentSection(idx: number, ev: CustomEvent) {
    if (
      (updatedDocument[idx].type as any as string) === "text" ||
      (updatedDocument[idx].type as any as string) === "textlist"
    ) {
      (updatedDocument[idx] as TEITextSection | TEITextlistSection).content =
        ev.detail;
    }
    window.clearTimeout(updateDebounce);
    updateDebounce = window.setTimeout(() => {
      if (!deepEql(updatedDocument, initialDocument)) {
        currentFileContent.set(JSON.stringify(updatedDocument));
        currentFileModified.set(true);
      } else {
        currentFileModified.set(false);
      }
    }, 100);
  }

  function shortCutTracker(ev: KeyboardEvent) {
    if ($currentFile !== null && $currentFileContent !== null) {
      if (ev.key === "s" && (ev.ctrlKey || ev.metaKey)) {
        ev.preventDefault();
        runAction({
          action: "SaveCurrentFile",
          branch: $currentBranch,
          filename: $currentFile.fullpath,
          data: $currentFileContent,
          callback() {
            currentFileModified.set(false);
          },
        });
      }
    }
  }

  onDestroy(currentFileModifiedUnsubscribe);
</script>

<h1 class="sr-only">{$currentFile?.name}</h1>
{#if $teiDocument}
  <div class="flex-1 flex overflow-hidden" on:keydown={shortCutTracker}>
    <Tabs.Root class="flex-1 flex flex-col">
      <Tabs.List>
        {#each $teiDocument as section}
          <Tabs.Trigger value={section.type.name}
            >{section.type.title}</Tabs.Trigger
          >
        {/each}
      </Tabs.List>
      {#each $teiDocument as section, idx}
        <Tabs.Content value={section.type.name} class="flex-1 overflow-hidden">
          {#if section.type.type === "metadata"}
            <TeiMetadataEditor />
          {:else if section.type.type === "text"}
            <TeiTextEditor
              {section}
              sections={$teiDocument}
              on:update={(ev) => {
                updateDocumentSection(idx, ev);
              }}
            />
          {:else if section.type.type === "textlist"}
            <TeiTextListEditor
              {section}
              sections={$teiDocument}
              on:update={(ev) => {
                updateDocumentSection(idx, ev);
              }}
            />
          {/if}
        </Tabs.Content>
      {/each}
    </Tabs.Root>
  </div>
{:else}
  <LoadingIndicator />
{/if}
