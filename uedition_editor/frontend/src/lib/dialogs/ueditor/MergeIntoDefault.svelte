<script lang="ts">
  import { Dialog } from "bits-ui";
  import { mdiSync } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import Icon from "../../Icon.svelte";
  import { appState } from "../../../state.svelte";
  import { title } from "../../../util";

  const queryClient = useQueryClient();
  let confirmBranchTitle = $state("");
  let errorMessage = $state("");

  function openDialog(open: boolean) {
    if (open) {
      confirmBranchTitle = "";
    }
  }

  const mergeBranchIntoDefault = createMutation(() => ({
    mutationFn: async () => {
      const response = await window.fetch(
        "/api/branches/" + appState.currentBranch?.id + "/merge-into-default",
        {
          method: "POST",
          headers: {
            Accept: "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["branches"] });
        queryClient.invalidateQueries({ queryKey: ["files"] });
        appState.activeDialog = null;
        let found = false;
        if (appState.branches) {
          for (const branch of appState.branches?.local) {
            if (branch.id === appState.apiStatus?.git.default_branch) {
              appState.currentBranch = branch;
              found = true;
              break;
            }
          }
        }
        if (!found) {
          appState.currentBranch = null;
        }
      } else {
        errorMessage = (await response.json()).detail[0].msg;
        errorMessage =
          errorMessage[0].toUpperCase() + errorMessage.substring(1);
      }
    },
  }));

  function startMergeBranchFromDefault(ev: Event) {
    ev.preventDefault();
    if (appState.currentBranch?.title === confirmBranchTitle) {
      errorMessage = "";
      mergeBranchIntoDefault.mutate();
    } else {
      errorMessage = "Please enter the exact name of the branch to merge.";
    }
  }
</script>

<Base onOpenChange={openDialog}>
  <Dialog.Title>Merge changes into the default branch</Dialog.Title>
  <form data-dialog-content-area onsubmit={startMergeBranchFromDefault}>
    <p class="mb-4">
      Please confirm you wish to merge all changes from the current branch <span
        class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
        >{appState.currentBranch?.title}</span
      >
      into the default branch
      <span
        class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
        >{title(appState.apiStatus?.git.default_branch as string)}</span
      >. This cannot be undone and will also delete the current branch. To
      confirm the action, please enter the name of the branch to delete.
    </p>
    <label class="block mb-4">
      <span data-form-field-label>Confirm branch name</span>
      <input bind:value={confirmBranchTitle} type="text" data-form-field-text />
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    {#if errorMessage}
      <p data-form-field-error>{errorMessage}</p>
    {/if}
    <div data-dialog-buttons>
      {#if mergeBranchIntoDefault.isPending}
        <span data-button class="inline-flex"
          ><Icon path={mdiSync} class="block w-6 h-6 animate-spin" /><span
            >Merging...</span
          ></span
        >
      {:else}
        <Dialog.Close type="button" data-button>Don't merge</Dialog.Close>
        <button type="submit" data-button>Merge</button>
      {/if}
    </div>
  </form>
</Base>
