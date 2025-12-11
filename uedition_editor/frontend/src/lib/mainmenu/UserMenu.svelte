<script lang="ts">
  import { Menubar } from "bits-ui";
  import { mdiExitToApp } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { appState } from "../../state.svelte";

  const queryClient = useQueryClient();

  async function logout() {
    const response = await window.fetch("/api/auth/login", {
      method: "DELETE",
    });
    if (response.ok) {
      queryClient.cancelQueries();
      queryClient.invalidateQueries();
      appState.ui.hasLoggedOut = true;
    }
  }
</script>

{#if appState.currentUser !== null}
  <Menubar.Menu>
    <Menubar.Trigger>{appState.currentUser.name}</Menubar.Trigger>
    <Menubar.Content>
      <Menubar.Item onclick={logout}>
        <Icon path={mdiExitToApp} class="w-4 h-4"></Icon>
        <span>Logout</span>
      </Menubar.Item>
    </Menubar.Content>
  </Menubar.Menu>
{/if}
