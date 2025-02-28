<script lang="ts">
  import { Dialog } from "bits-ui";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import { currentFile, useCurrentBranch } from "../../../stores";
  import { Dialogs, activeDialog } from "../Index.svelte";

  const queryClient = useQueryClient();
  const currentBranch = useCurrentBranch();
  let open = false;
  let error = "";
  let confirmationText = "";

  async function deleteDirectory(ev: Event) {
    ev.preventDefault();
    error = "";
    if (
      confirmationText === $currentFile?.fullpath ||
      confirmationText == $currentFile?.name
    ) {
      const response = await fetch(
        "/api/branches/" +
          $currentBranch?.id +
          "/files/" +
          $currentFile.fullpath,
        {
          method: "DELETE",
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["branches", $currentBranch?.id, "files/"],
        });
        currentFile.set(null);
        open = false;
        activeDialog.set(Dialogs.NONE);
      }
    } else {
      error = "Please check that you have typed in the correct name.";
    }
  }

  function onOpenChange(open: boolean) {
    if (open) {
      confirmationText = "";
      error = "";
    } else {
      activeDialog.set(Dialogs.NONE);
    }
  }
</script>

<Base bind:open {onOpenChange}>
  <Dialog.Title class="bg-rose-700">
    Delete <span class="font-bold">{$currentFile?.fullpath}</span>
  </Dialog.Title>
  <form on:submit={deleteDirectory} data-dialog-content-area>
    <p class="mb-4">
      Please confirm you wish to delete the file <span
        class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
        >{$currentFile?.fullpath}</span
      >. To confirm the action, please enter the name of the file to delete.
    </p>
    <label class="block">
      <span data-form-field-label>Confirm filename</span>
      <input bind:value={confirmationText} type="text" data-form-field-text />
      {#if error}
        <span data-form-field-error>{error}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      <Dialog.Close data-button>Don't delete</Dialog.Close>
      <button
        type="submit"
        data-button
        class="border-rose-700 hover:bg-rose-700 focus:bg-rose-700"
        >Delete</button
      >
    </div>
  </form>
</Base>
