<script lang="ts">
  import { Dialog } from "bits-ui";
  import { createEventDispatcher } from "svelte";
  import { useQueryClient } from "@tanstack/svelte-query";

  import { currentBranch, currentFile } from "../../stores";

  const dispatch = createEventDispatcher();
  const queryClient = useQueryClient();
  let open = true;
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
        open = false;
      }
    } else {
      error = "Please check that you have typed in the correct name.";
    }
  }

  $: {
    if (!open) {
      dispatch("close");
    }
  }
</script>

<Dialog.Root
  bind:open
  onOutsideClick={() => {
    console.log("test");
  }}
>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title class="bg-rose-700">
        Delete <span class="font-bold">{$currentFile?.fullpath}</span>
      </Dialog.Title>
      <form on:submit={deleteDirectory} data-dialog-content-area>
        <p class="mb-4">
          Please confirm you wish to delete the directory <span
            class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
            >{$currentFile?.fullpath}</span
          >
          and all the files and directories within that. To confirm the action, please
          enter the name of the directory to delete.
        </p>
        <label class="block">
          <span data-form-field-label>Confirmation Directoryname</span>
          <input
            bind:value={confirmationText}
            type="text"
            data-form-field-text
          />
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
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
