<script lang="ts">
  import { Menubar } from "bits-ui";
  import {
    mdiCheckCircle,
    mdiSourceBranchPlus,
    mdiSourceBranchRemove,
  } from "@mdi/js";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";
  import type { CreateQueryResult } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { activeDialog, Dialogs } from "../dialogs/Index.svelte";

  const branches = getContext("branches") as CreateQueryResult<Branch[]>;
  const currentBranch = getContext("currentBranch") as Writable<Branch | null>;
</script>

<Menubar.Menu>
  <Menubar.Trigger
    >μEditor{#if $currentBranch !== null}&nbsp;({$currentBranch.title}){/if}</Menubar.Trigger
  >
  <Menubar.Content>
    <Menubar.Item
      on:click={() => {
        activeDialog.set(Dialogs.UEDITOR_NEW_BRANCH);
      }}
    >
      <Icon path={mdiSourceBranchPlus} class="w-4 h-4"></Icon>
      <span>New Branch</span>
    </Menubar.Item>
    <Menubar.Separator></Menubar.Separator>
    {#if $currentBranch !== null}
      <Menubar.Item
        on:click={() => {
          activeDialog.set(Dialogs.UEDITOR_DELETE_BRANCH);
        }}
      >
        <Icon path={mdiSourceBranchRemove} class="w-4 h-4"></Icon>
        <span>Delete Branch {$currentBranch.title}</span>
      </Menubar.Item>
      <Menubar.Separator></Menubar.Separator>
    {/if}
    {#if $branches.isSuccess}
      <Menubar.RadioGroup
        onValueChange={(value) => {
          if ($branches.isSuccess) {
            for (let branch of $branches.data) {
              if (branch.id === value) {
                currentBranch.set(branch);
              }
            }
          }
        }}
      >
        {#each $branches.data as branch}
          <Menubar.RadioItem value={branch.id}>
            {#if $currentBranch !== null && $currentBranch.id === branch.id}
              <Icon path={mdiCheckCircle} class="w-4 h-4"></Icon>
            {:else}
              <Icon class="w-4 h-4"></Icon>
            {/if}
            <span>{branch.title}</span>
          </Menubar.RadioItem>
        {/each}
      </Menubar.RadioGroup>
    {/if}
  </Menubar.Content>
</Menubar.Menu>
