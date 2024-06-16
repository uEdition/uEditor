<script lang="ts">
  import type { CreateQueryResult } from "@tanstack/svelte-query";
  import { Tabs } from "bits-ui";
  import { getContext, onDestroy } from "svelte";

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
  let sections: TEIDocument = {};

  const uEditorConfig = getContext(
    "uEditorConfig",
  ) as CreateQueryResult<UEditorSettings>;

  const currentFileUnsubscribe = currentFile.subscribe((currentFile) => {
    if (currentFile && currentFile.name.endsWith(".tei")) {
      runAction({
        action: "LoadTextFile",
        branch: $currentBranch,
        filename: currentFile.fullpath,
        callback: (data: string) => {
          value = JSON.parse(data);
          for (let part of value) {
            sections[part.name] = part;
          }
          sections = sections;
          currentFileContent.set(data);
          currentFileModified.set(false);
        },
      });
    }
  });

  onDestroy(currentFileUnsubscribe);
</script>

<h1 class="sr-only">{$currentFile?.name}</h1>
{#if $uEditorConfig.isSuccess}
  <Tabs.Root class="flex-1 flex flex-col ">
    <Tabs.List>
      {#each $uEditorConfig.data.tei.sections as section}
        <Tabs.Trigger value={section.name}>{section.title}</Tabs.Trigger>
      {/each}
    </Tabs.List>
    {#each $uEditorConfig.data.tei.sections as section}
      <Tabs.Content value={section.name} class="flex-1 overflow-hidden">
        {#if section.type === "metadata"}
          <TeiMetadataEditor />
        {:else if section.type === "text"}
          <TeiTextEditor section={sections[section.name]} config={section} />
        {:else if section.type === "textlist"}
          <TeiTextListEditor section={sections[section.name]} />
        {/if}
      </Tabs.Content>
    {/each}
  </Tabs.Root>
{:else}
  <LoadingIndicator />
{/if}
