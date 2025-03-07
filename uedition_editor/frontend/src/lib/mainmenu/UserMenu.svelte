<script lang="ts">
  import { Menubar } from "bits-ui";
  import { mdiExitToApp } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { useApiStatus, useCurrentUser } from "../../stores";

  const currentUser = useCurrentUser();
  const apiStatus = useApiStatus();
  const queryClient = useQueryClient();

  async function logout() {
    const response = await window.fetch("/api/auth/login", {
      method: "DELETE",
    });
    if (response.ok) {
      queryClient.cancelQueries();
      queryClient.invalidateQueries({ queryKey: ["auth"] });
    }
  }
</script>

{#if $apiStatus.isSuccess && $apiStatus.data.auth.provider !== "no-auth"}
  <Menubar.Menu>
    <Menubar.Trigger>{$currentUser.data?.name}</Menubar.Trigger>
    <Menubar.Content>
      <Menubar.Item on:click={logout}>
        <Icon path={mdiExitToApp} class="w-4 h-4"></Icon>
        <span>Logout</span>
      </Menubar.Item>
    </Menubar.Content>
  </Menubar.Menu>
{/if}
