<script lang="ts">
  import { Dialog } from "bits-ui";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import { appState } from "../../../state.svelte";

  const queryClient = useQueryClient();
  let newFileName = $state("");
  let errorMessage = $state("");

  async function createNewFile(ev: Event) {
    ev.preventDefault();
    if (newFileName.trim() === "") {
      errorMessage = "Please enter a folder name";
    } else {
      const response = await fetch(
        "/api/branches/" +
          appState.currentBranch?.id +
          "/files/" +
          appState.currentFile?.fullpath +
          "/" +
          newFileName.trim(),
        {
          method: "POST",
          headers: { "X-uEditor-New-Type": "folder" },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["branches", appState.currentBranch?.id, "files/"],
        });
        appState.activeDialog = null;
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
    }
  }
</script>

<Base onOpenChange={openDialog}>
  <Dialog.Title
    >Create a new Folder in "{appState.currentFile?.fullpath
      ? appState.currentFile?.fullpath
      : "/"}"</Dialog.Title
  >
  <form data-dialog-content-area onsubmit={createNewFile}>
    <label>
      <span data-form-field-label>New Folder Name</span>
      <input bind:value={newFileName} type="text" data-form-field-text />
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      <Dialog.Close type="button" data-button>Don't create</Dialog.Close>
      <button type="submit" data-button>Create</button>
    </div>
  </form>
</Base>
