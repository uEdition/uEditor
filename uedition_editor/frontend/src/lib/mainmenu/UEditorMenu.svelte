<script lang="ts">
  import { Menubar } from "bits-ui";
  import {
    mdiCheckCircle,
    mdiSourceBranchPlus,
    mdiSourceBranchRemove,
    mdiSourceBranchSync,
  } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { runAction } from "../actions/Index.svelte";
  import { activeDialog, Dialogs } from "../dialogs/Index.svelte";
  import { title } from "../../util";
  import { appState } from "../../state.svelte";

  const queryClient = useQueryClient();
</script>

<Menubar.Menu>
  <Menubar.Trigger
    >μEditor{#if appState.currentBranch !== null}&nbsp;({appState.currentBranch
        .title}){/if}</Menubar.Trigger
  >
  <Menubar.Content>
    {#if appState.apiStatus?.git.enabled}
      <Menubar.Item
        onclick={() => {
          activeDialog.set(Dialogs.UEDITOR_NEW_BRANCH);
        }}
      >
        <Icon path={mdiSourceBranchPlus} class="w-4 h-4"></Icon>
        <span>New Branch</span>
      </Menubar.Item>
      {#if appState.branches && appState.branches.remote.length > 0}
        <Menubar.Item
          onclick={() => {
            activeDialog.set(Dialogs.UEDITOR_IMPORT_REMOTE_BRANCH);
          }}
        >
          <Icon class="w-4 h-4" />
          <span>Import Branch</span>
        </Menubar.Item>
      {/if}
      {#if appState.branches}
        <Menubar.Item
          onclick={() => {
            runAction({
              action: "SynchroniseBranches",
              callback: () => {
                queryClient.invalidateQueries({ queryKey: ["branches"] });
              },
            });
          }}
        >
          <Icon class="w-4 h-4" />
          <span>Synchronise Branches</span>
        </Menubar.Item>
      {/if}
      <Menubar.Separator></Menubar.Separator>
      {#if appState.currentBranch}
        {#if appState.currentBranch.update_from_default}
          <Menubar.Item
            onclick={() => {
              activeDialog.set(Dialogs.UEDITOR_MERGE_FROM_DEFAULT);
            }}
          >
            <Icon path={mdiSourceBranchSync} class="w-4 h-4" />
            <span
              >Merge Updates from {title(
                appState.apiStatus?.git.default_branch as string,
              )}</span
            >
          </Menubar.Item>
          <Menubar.Separator></Menubar.Separator>
        {/if}
        {#if appState.apiStatus?.git.default_branch !== appState.currentBranch.id}
          <Menubar.Item
            onclick={() => {
              activeDialog.set(Dialogs.UEDITOR_DELETE_BRANCH);
            }}
          >
            <Icon path={mdiSourceBranchRemove} class="w-4 h-4"></Icon>
            <span>Delete Branch {appState.currentBranch.title}</span>
          </Menubar.Item>
          <Menubar.Separator></Menubar.Separator>
        {/if}
      {/if}
      {#if appState.branches !== null && appState.branches.local.length > 0}
        <Menubar.RadioGroup
          onValueChange={(value) => {
            if (appState.branches !== null) {
              for (let branch of appState.branches.local) {
                if (branch.id === value) {
                  appState.currentBranch = branch;
                }
              }
            }
          }}
        >
          {#each appState.branches.local as branch}
            <Menubar.RadioItem value={branch.id}>
              {#if appState.currentBranch !== null && appState.currentBranch.id === branch.id}
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
