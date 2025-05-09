<script lang="ts">
  import { Menubar } from "bits-ui";
  import {
    mdiCheckCircle,
    mdiSourceBranchPlus,
    mdiSourceBranchRemove,
    mdiSourceBranchSync,
  } from "@mdi/js";
  import { derived } from "svelte/store";

  import Icon from "../Icon.svelte";
  import { runAction } from "../actions/Index.svelte";
  import { activeDialog, Dialogs } from "../dialogs/Index.svelte";
  import {
    useApiStatus,
    useBranches,
    useCurrentBranch,
    useRemoteBranches,
  } from "../../stores";

  const apiStatus = useApiStatus();
  const branches = useBranches();
  const remoteBranches = useRemoteBranches();
  const currentBranch = useCurrentBranch();

  const liveCurrentBranch = derived(
    [branches, currentBranch],
    ([branches, currentBranch]) => {
      if (branches.isSuccess && currentBranch !== null) {
        for (const branch of branches.data) {
          if (branch.id === currentBranch.id) {
            return branch;
          }
        }
      }
      return null;
    },
  );
</script>

<Menubar.Menu>
  <Menubar.Trigger
    >μEditor{#if $currentBranch !== null}&nbsp;({$currentBranch.title}){/if}</Menubar.Trigger
  >
  <Menubar.Content>
    {#if $apiStatus.isSuccess && $apiStatus.data.git.enabled}
      <Menubar.Item
        on:click={() => {
          activeDialog.set(Dialogs.UEDITOR_NEW_BRANCH);
        }}
      >
        <Icon path={mdiSourceBranchPlus} class="w-4 h-4"></Icon>
        <span>New Branch</span>
      </Menubar.Item>
      {#if $remoteBranches.isSuccess && $remoteBranches.data.length > 0}
        <Menubar.Item
          on:click={() => {
            activeDialog.set(Dialogs.UEDITOR_IMPORT_REMOTE_BRANCH);
          }}
        >
          <Icon class="w-4 h-4" />
          <span>Import Branch</span>
        </Menubar.Item>
      {/if}
      <Menubar.Item
        on:click={() => {
          runAction({ action: "SynchroniseBranches" });
        }}
      >
        <Icon class="w-4 h-4" />
        <span>Synchronise Branches</span>
      </Menubar.Item>
      <Menubar.Separator></Menubar.Separator>
      {#if $liveCurrentBranch !== null}
        {#if $liveCurrentBranch.update_from_default}
          <Menubar.Item
            on:click={() => {
              activeDialog.set(Dialogs.UEDITOR_MERGE_FROM_DEFAULT);
            }}
          >
            <Icon path={mdiSourceBranchSync} class="w-4 h-4" />
            <span>Merge from {$apiStatus.data.git.default_branch}</span>
          </Menubar.Item>
          <Menubar.Separator></Menubar.Separator>
        {/if}
        {#if $apiStatus.data.git.default_branch !== $liveCurrentBranch.id}
          <Menubar.Item
            on:click={() => {
              activeDialog.set(Dialogs.UEDITOR_DELETE_BRANCH);
            }}
          >
            <Icon path={mdiSourceBranchRemove} class="w-4 h-4"></Icon>
            <span>Delete Branch {$liveCurrentBranch.title}</span>
          </Menubar.Item>
          <Menubar.Separator></Menubar.Separator>
        {/if}
      {/if}
      {#if $branches.isSuccess && $branches.data.length > 0}
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
    {/if}
  </Menubar.Content>
</Menubar.Menu>
