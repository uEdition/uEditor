<script lang="ts">
  import type { CreateQueryResult } from "@tanstack/svelte-query";
  import { Tabs } from "bits-ui";
  import { getContext } from "svelte";
  import LoadingIndicator from "../LoadingIndicator.svelte";

  const uEditorConfig = getContext(
    "uEditorConfig"
  ) as CreateQueryResult<UEditorSettings>;
</script>

{#if $uEditorConfig.isSuccess}
  <Tabs.Root>
    <Tabs.List>
      {#each $uEditorConfig.data.tei.sections as section}
        <Tabs.Trigger value={section.name}>{section.title}</Tabs.Trigger>
      {/each}
    </Tabs.List>
    {#each $uEditorConfig.data.tei.sections as section}
      <Tabs.Content value={section.name}>
        {section.title}
      </Tabs.Content>
    {/each}
  </Tabs.Root>
{:else}
  <LoadingIndicator />
{/if}
