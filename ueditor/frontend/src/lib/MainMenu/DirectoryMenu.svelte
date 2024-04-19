<script lang="ts">
  import { Dialog, Menubar } from "bits-ui";
  import {
    mdiFolderEditOutline,
    mdiFolderMoveOutline,
    mdiFolderMultipleOutline,
    mdiFolderRemoveOutline,
  } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import { currentFile } from "../../stores";
  import DirectoryDelete from "../actions/DirectoryDelete.svelte";

  enum Action {
    Nothing = 1,
    Rename,
    Move,
    Copy,
    Delete,
  }

  let action: Action = Action.Nothing;
</script>

<Menubar.Menu>
  <Menubar.Trigger>Directory</Menubar.Trigger>
  <Menubar.Content>
    <Menubar.Item
      on:click={() => {
        action = Action.Rename;
      }}
    >
      <Icon path={mdiFolderEditOutline} size="w-4 h-4"></Icon>
      <span>Rename</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        action = Action.Move;
      }}
    >
      <Icon path={mdiFolderMoveOutline} size="w-4 h-4"></Icon>
      <span>Move</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        action = Action.Copy;
      }}
    >
      <Icon path={mdiFolderMultipleOutline} size="w-4 h-4"></Icon>
      <span>Copy</span>
    </Menubar.Item>
    <Menubar.Item
      on:click={() => {
        action = Action.Delete;
      }}
    >
      <Icon path={mdiFolderRemoveOutline} size="w-4 h-4"></Icon>
      <span>Delete</span>
    </Menubar.Item>
  </Menubar.Content>
</Menubar.Menu>

{#if action === Action.Delete}
  <DirectoryDelete
    on:close={() => {
      console.log("Resetting action");
      action = Action.Nothing;
    }}
  />
{/if}
