<script lang="ts">
  import { Dialog } from "bits-ui";
  import { mdiSync } from "@mdi/js";
  import { derived } from "svelte/store";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import Icon from "../../Icon.svelte";
  import { appState } from "../../../state.svelte";

  const queryClient = useQueryClient();
  let importBranchId = $state("");
  let errorMessage = $state("");

  function openDialog(open: boolean) {
    if (open) {
      importBranchId = "";
    }
  }

  const importableBranches = $derived.by(() => {
    if (appState.branches) {
      return appState.branches.remote
        .filter((remoteBranch) => {
          let found = false;
          for (const branch of appState.branches.local) {
            if (remoteBranch.id.endsWith("/" + branch.id)) {
              found = true;
              break;
            }
          }
          return !found;
        })
        .map((remoteBranch) => {
          return {
            id: remoteBranch.id.substring(remoteBranch.id.indexOf("/") + 1),
            title: remoteBranch.title,
            nogit: false,
          };
        });
    } else {
      return [];
    }
  });

  const createBranch = createMutation(() => ({
    mutationFn: async (newBranch: { title: string }) => {
      const response = await window.fetch("/api/branches", {
        method: "POST",
        body: JSON.stringify({
          title: newBranch.title,
        }),
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
          "X-UEditor-Import-Branch": "true",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["branches"] });
        const newBranch = (await response.json()) as Branch;
        appState.currentBranch = newBranch;
        appState.activeDialog = null;
      } else {
        errorMessage = (await response.json()).detail[0].msg;
        errorMessage =
          errorMessage[0].toUpperCase() + errorMessage.substring(1);
      }
    },
  }));

  async function createNewBranch(ev: Event) {
    ev.preventDefault();
    createBranch.mutate({ title: importBranchId });
  }
</script>

<Base onOpenChange={openDialog}>
  <Dialog.Title>Import a remote branch</Dialog.Title>
  <form data-dialog-content-area onsubmit={createNewBranch}>
    <label>
      <span data-form-field-label>New branch title</span>
      <select bind:value={importBranchId} data-form-field-text>
        {#each importableBranches as branch}
          <option value={branch.id}>{branch.title}</option>
        {/each}
      </select>
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      {#if createBranch.isPending}
        <span data-button class="inline-flex"
          ><Icon path={mdiSync} class="block w-6 h-6 animate-spin" /><span
            >Importing...</span
          ></span
        >
      {:else}
        <Dialog.Close type="button" data-button>Don't import</Dialog.Close>
        <button type="submit" data-button>Import</button>
      {/if}
    </div>
  </form>
</Base>
