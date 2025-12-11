<script lang="ts">
  import { Menubar } from "bits-ui";
  import { mdiGithub, mdiHelp } from "@mdi/js";

  import Icon from "../Icon.svelte";
  import { appState, Dialogs } from "../../state.svelte";
</script>

<Menubar.Menu>
  <Menubar.Trigger>Help</Menubar.Trigger>
  <Menubar.Content>
    <Menubar.Item
      onclick={() => {
        window.open("https://ueditor.readthedocs.io/en/latest/", "_blank");
      }}
    >
      <Icon class="w-4 h-4" path={mdiHelp}></Icon>
      <span>Help</span>
    </Menubar.Item>
    <Menubar.Item
      onclick={() => {
        appState.activeDialog = Dialogs.HELP_ABOUT;
      }}
    >
      <Icon class="w-4 h-4"></Icon>
      <span>About</span>
    </Menubar.Item>
    <Menubar.Separator></Menubar.Separator>
    <Menubar.Item
      onclick={() => {
        window.open("https://github.com/uEdition/uEditor/issues", "_blank");
      }}
    >
      <Icon class="w-4 h-4" path={mdiGithub}></Icon>
      <span>Report an Issue</span>
    </Menubar.Item>
  </Menubar.Content>
</Menubar.Menu>
