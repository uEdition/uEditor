<script lang="ts">
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

  let value = [];

  const uEditorConfig = getContext(
    "uEditorConfig"
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
            value = JSON.parse(data);
            const newSections: TEIDocument = [];
            for (let section of uEditorConfig.data.tei.sections) {
              for (let part of value) {
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
    null as null | TEIDocument
  );
</script>

<h1 class="sr-only">{$currentFile?.name}</h1>
{#if $teiDocument}
  <Tabs.Root class="flex-1 flex flex-col ">
    <Tabs.List>
      {#each $teiDocument as section}
        <Tabs.Trigger value={section.type.name}
          >{section.type.title}</Tabs.Trigger
        >
      {/each}
    </Tabs.List>
    {#each $teiDocument as section}
      <Tabs.Content value={section.type.name} class="flex-1 overflow-hidden">
        {#if section.type.type === "metadata"}
          <TeiMetadataEditor />
        {:else if section.type.type === "text"}
          <TeiTextEditor {section} sections={$teiDocument} />
        {:else if section.type.type === "textlist"}
          <TeiTextListEditor {section} sections={$teiDocument} />
        {/if}
      </Tabs.Content>
    {/each}
  </Tabs.Root>
{:else}
  <LoadingIndicator />
{/if}
