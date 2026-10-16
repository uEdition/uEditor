<script lang="ts">
  import { Menubar } from "bits-ui";
  import { mdiCog, mdiCogPlay, mdiOpenInNew } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { appState } from "../../state.svelte";

  const queryClient = useQueryClient();

  async function startGenerate() {
    const response = await window.fetch(
      "/api/branches/" + appState.currentBranch?.id + "/preview/generate",
      { method: "POST" },
    );
    if (response.status == 204) {
      queryClient.invalidateQueries({
        queryKey: ["branches", appState.currentBranch?.id, "preview"],
      });
    }
  }
</script>

{#if appState.preview !== null}
  <Menubar.Menu>
    <Menubar.Trigger>Preview</Menubar.Trigger>
    <Menubar.Content>
      {#if appState.preview === "generating"}
        <Menubar.Item>
          <Icon class="w-4 h-4 animate-spin" path={mdiCog}></Icon>
          <span>Generating preview</span>
        </Menubar.Item>
      {:else}
        <Menubar.Item
          onclick={() => {
            startGenerate();
          }}
        >
          <Icon class="w-4 h-4" path={mdiCogPlay}></Icon>
          <span>Generate preview</span>
        </Menubar.Item>
      {/if}
      {#if appState.preview === "generated"}
        <Menubar.Item
          onclick={() => {
            window.open(
              "/api/branches/" + appState.currentBranch?.id + "/preview/view/",
              "ueditor-preview-" + appState.currentBranch?.id,
            );
          }}
        >
          <Icon class="w-4 h-4" path={mdiOpenInNew}></Icon>
          <span>Open preview</span>
        </Menubar.Item>
      {/if}
    </Menubar.Content>
  </Menubar.Menu>
{/if}
