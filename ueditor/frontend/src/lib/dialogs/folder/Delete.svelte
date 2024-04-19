<script lang="ts">
  import { Dialog } from "bits-ui";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import { currentBranch, currentFile } from "../../../stores";

  const queryClient = useQueryClient();
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
        "/api/branches/" + $currentBranch + "/files/" + $currentFile.fullpath,
        {
          method: "DELETE",
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["branches", $currentBranch, "files/"],
        });
        currentFile.set(null);
        open = false;
      }
    } else {
      error = "Please check that you have typed in the correct name.";
    }
  }

  function onOpenChange(open: boolean) {
    if (open) {
      confirmationText = "";
      error = "";
    }
  }
</script>

<Base bind:open {onOpenChange}>
  <Dialog.Title class="bg-rose-700">
    Delete <span class="font-bold">{$currentFile?.fullpath}</span>
  </Dialog.Title>
  <form on:submit={deleteDirectory} data-dialog-content-area>
    <p class="mb-4">
      Please confirm you wish to delete the folder <span
        class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
        >{$currentFile?.fullpath}</span
      >
      and all the files and folders within that. To confirm the action, please enter
      the name of the folder to delete.
    </p>
    <label class="block">
      <span data-form-field-label>Confirmation Folder Name</span>
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
