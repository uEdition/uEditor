<script lang="ts">
  import { Dialog } from "bits-ui";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import { currentFile, useCurrentBranch } from "../../../stores";
  import { Dialogs, activeDialog } from "../Index.svelte";

  const queryClient = useQueryClient();
  const currentBranch = useCurrentBranch();
  let open = false;
  let newFileName = "";
  let errorMessage = "";

  async function createNewFile(ev: Event) {
    ev.preventDefault();
    if (newFileName.trim() === "") {
      errorMessage = "Please enter a filename";
    } else {
      const response = await fetch(
        "/api/branches/" +
          $currentBranch?.id +
          "/files/" +
          $currentFile?.fullpath +
          "/" +
          newFileName,
        {
          method: "POST",
          headers: { "X-uEditor-New-Type": "file" },
        }
      );
      if (response.ok) {
        open = false;
        queryClient.invalidateQueries({
          queryKey: ["branches", $currentBranch?.id, "files/"],
        });
        activeDialog.set(Dialogs.NONE);
      } else {
        errorMessage = (await response.json()).detail[0].msg;
        errorMessage =
          errorMessage[0].toUpperCase() + errorMessage.substring(1);
      }
    }
  }

  function openDialog(open: boolean) {
    if (open) {
      newFileName = "";
      errorMessage = "";
    } else {
      activeDialog.set(Dialogs.NONE);
    }
  }
</script>

<Base bind:open onOpenChange={openDialog}>
  <Dialog.Title
    >Create a new File in "{$currentFile?.fullpath
      ? $currentFile?.fullpath
      : "/"}"</Dialog.Title
  >
  <form data-dialog-content-area on:submit={createNewFile}>
    <label>
      <span data-form-field-label>New Filename</span>
      <input bind:value={newFileName} type="text" data-form-field-text />
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      <Dialog.Close data-button>Don't create</Dialog.Close>
      <button type="submit" data-button>Create</button>
    </div>
  </form>
</Base>
