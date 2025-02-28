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
  let newBranchTitle = "";
  let errorMessage = "";

  function openDialog(open: boolean) {
    if (open) {
      newBranchTitle = "";
    }
  }

  const createBranch = createMutation({
    mutationFn: async (newBranch: { title: string }) => {
      const response = await window.fetch("/api/branches", {
        method: "POST",
        body: JSON.stringify({
          title: newBranch.title,
        }),
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["branches"] });
        const newBranch = (await response.json()) as Branch;
        currentBranch.set(newBranch);
        activeDialog.set(Dialogs.NONE);
      } else {
        errorMessage = (await response.json()).detail[0].msg;
        errorMessage =
          errorMessage[0].toUpperCase() + errorMessage.substring(1);
      }
    },
  });

  async function createNewBranch(ev: Event) {
    ev.preventDefault();
    $createBranch.mutate({ title: newBranchTitle });
  }
</script>

<Base bind:open onOpenChange={openDialog}>
  <Dialog.Title>Create a new branch</Dialog.Title>
  <form data-dialog-content-area on:submit={createNewBranch}>
    <label>
      <span data-form-field-label>New branch title</span>
      <input bind:value={newBranchTitle} type="text" data-form-field-text />
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      {#if $createBranch.isPending}
        <span data-button class="inline-flex"
          ><Icon path={mdiSync} class="block w-6 h-6 animate-spin" /><span
            >Creating...</span
          ></span
        >
      {:else}
        <Dialog.Close data-button>Don't create</Dialog.Close>
        <button type="submit" data-button>Create</button>
      {/if}
    </div>
  </form>
</Base>
