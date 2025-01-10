<script lang="ts">
  import { Dialog, Menubar, RadioGroup } from "bits-ui";
  import { mdiCheckCircle, mdiSourceBranchPlus } from "@mdi/js";
  import { getContext } from "svelte";
  import type { Writable } from "svelte/store";
  import type { CreateQueryResult } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";

  const branches = getContext("branches") as CreateQueryResult<Branch[]>;
  const currentBranch = getContext("currentBranch") as Writable<Branch | null>;
  let newBranchDialogOpen = false;
</script>

<Menubar.Menu>
  <Menubar.Trigger
    >μEditor{#if $currentBranch !== null}&nbsp;({$currentBranch.title}){/if}</Menubar.Trigger
  >
  <Menubar.Content>
    <Menubar.Item
      on:click={() => {
        newBranchDialogOpen = true;
      }}
    >
      <Icon path={mdiSourceBranchPlus} class="w-4 h-4"></Icon>
      <span>New Branch</span>
    </Menubar.Item>
    <Menubar.Separator></Menubar.Separator>
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

<Dialog.Root bind:open={newBranchDialogOpen}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title>Create a new Branch</Dialog.Title>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
