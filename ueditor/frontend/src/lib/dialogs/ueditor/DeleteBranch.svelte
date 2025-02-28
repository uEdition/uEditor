<script lang="ts">
  import { Dialog } from "bits-ui";
  import { mdiSync } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import Icon from "../../Icon.svelte";
  import { useCurrentBranch } from "../../../stores";
  import { Dialogs, activeDialog } from "../Index.svelte";

  const queryClient = useQueryClient();
  const currentBranch = useCurrentBranch();
  let open = false;
  let confirmBranchTitle = "";
  let errorMessage = "";

  function openDialog(open: boolean) {
    if (open) {
      confirmBranchTitle = "";
    }
  }

  const deleteBranch = createMutation({
    mutationFn: async () => {
      const response = await window.fetch(
        "/api/branches/" + $currentBranch?.id,
        {
          method: "DELETE",
          headers: {
            Accept: "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["branches"] });
        currentBranch.set(null);
        activeDialog.set(Dialogs.NONE);
      } else {
        errorMessage = (await response.json()).detail[0].msg;
        errorMessage =
          errorMessage[0].toUpperCase() + errorMessage.substring(1);
      }
    },
  });

  function startDeleteBranch(ev: Event) {
    ev.preventDefault();
    if ($currentBranch?.title === confirmBranchTitle) {
      errorMessage = "";
      $deleteBranch.mutate();
    } else {
      errorMessage = "Please enter the exact name of the branch to delete.";
    }
  }
</script>

<Base bind:open onOpenChange={openDialog}>
  <Dialog.Title>Create a new branch</Dialog.Title>
  <form data-dialog-content-area on:submit={startDeleteBranch}>
    <p class="mb-4">
      Please confirm you wish to delete the branch <span
        class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
        >{$currentBranch?.title}</span
      >. This cannot be undone. To confirm the action, please enter the name of
      the branch to delete.
    </p>
    <label>
      <span data-form-field-label>Confirm branch name</span>
      <input bind:value={confirmBranchTitle} type="text" data-form-field-text />
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      {#if $deleteBranch.isPending}
        <span data-button class="inline-flex"
          ><Icon path={mdiSync} class="block w-6 h-6 animate-spin" /><span
            >Deleting...</span
          ></span
        >
      {:else}
        <Dialog.Close data-button>Don't delete</Dialog.Close>
        <button type="submit" data-button>Delete</button>
      {/if}
    </div>
  </form>
</Base>
