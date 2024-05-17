<script lang="ts">
  import type { CreateQueryResult } from "@tanstack/svelte-query";
  import { Tabs } from "bits-ui";
  import { getContext } from "svelte";

  import { runAction } from "../actions/Index.svelte";
  import { currentFile } from "../../stores";
  import LoadingIndicator from "../LoadingIndicator.svelte";
  import TeiMetadataEditor from "./TeiMetadataEditor.svelte";
  import TeiTextEditor from "./TeiTextEditor.svelte";
  import TeiTextListEditor from "./TeiTextListEditor.svelte";

  const uEditorConfig = getContext(
    "uEditorConfig",
  ) as CreateQueryResult<UEditorSettings>;
</script>

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
          <TeiTextEditor />
        {:else if section.type === "textlist"}
          <TeiTextListEditor />
        {/if}
      </Tabs.Content>
    {/each}
  </Tabs.Root>
{:else}
  <LoadingIndicator />
{/if}
