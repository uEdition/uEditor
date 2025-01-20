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
      errorMessage = "Please enter a folder name";
    } else if ($currentFile?.fullpath) {
      const newPath = $currentFile.fullpath
        .split("/")
        .slice(0, $currentFile.fullpath.split("/").length - 1)
        .join("/");
      const response = await fetch(
        "/api/branches/" +
          $currentBranch?.id +
          "/files/" +
          newPath +
          "/" +
          newFileName.trim(),
        {
          method: "POST",
          headers: {
            "X-uEditor-New-Type": "folder",
            "X-uEditor-Rename-From": $currentFile?.fullpath,
          },
        }
      );
      if (response.ok) {
        open = false;
        queryClient.invalidateQueries({
          queryKey: ["branches", $currentBranch?.id, "files/"],
        });
        currentFile.set(null);
        activeDialog.set(Dialogs.NONE);
      } else {
        errorMessage = (await response.json()).detail[0].msg;
        errorMessage =
          errorMessage[0].toUpperCase() + errorMessage.substring(1);
      }
    } else {
      errorMessage = "Cannot rename the root folder";
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
    >Rename "{$currentFile?.fullpath
      ? $currentFile?.fullpath
      : "/"}"</Dialog.Title
  >
  <form data-dialog-content-area on:submit={createNewFile}>
    <label>
      <span data-form-field-label>New Folder Name</span>
      <input bind:value={newFileName} type="text" data-form-field-text />
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      <Dialog.Close data-button>Don't rename</Dialog.Close>
      <button type="submit" data-button>Rename</button>
    </div>
  </form>
</Base>
