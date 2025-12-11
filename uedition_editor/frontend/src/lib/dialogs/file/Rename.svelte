<script lang="ts">
  import { Dialog } from "bits-ui";
  import { useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import { appState } from "../../../state.svelte";

  const queryClient = useQueryClient();
  let newFileName = $state("");
  let errorMessage = $state("");

  async function renameFile(ev: Event) {
    ev.preventDefault();
    if (newFileName.trim() === "") {
      errorMessage = "Please enter a folder name";
    } else if (appState.currentFile?.fullpath) {
      const newPath = appState.currentFile.fullpath
        .split("/")
        .slice(0, appState.currentFile.fullpath.split("/").length - 1)
        .join("/");
      const response = await fetch(
        "/api/branches/" +
          appState.currentBranch?.id +
          "/files/" +
          newPath +
          "/" +
          newFileName.trim(),
        {
          method: "POST",
          headers: {
            "X-uEditor-New-Type": "file",
            "X-uEditor-Rename-From": appState.currentFile?.fullpath,
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({
          queryKey: ["branches", appState.currentBranch?.id, "files/"],
        });
        appState.currentFile = null;
        appState.activeDialog = null;
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
    }
  }
</script>

<Base onOpenChange={openDialog}>
  <Dialog.Title
    >Rename "{appState.currentFile?.fullpath
      ? appState.currentFile?.fullpath
      : "/"}"</Dialog.Title
  >
  <form data-dialog-content-area onsubmit={renameFile}>
    <label>
      <span data-form-field-label>New Filename</span>
      <input bind:value={newFileName} type="text" data-form-field-text />
      {#if errorMessage}
        <span data-form-field-error>{errorMessage}</span>
      {/if}
    </label>
    <div data-dialog-buttons>
      <Dialog.Close type="button" data-button>Don't rename</Dialog.Close>
      <button type="submit" data-button>Rename</button>
    </div>
  </form>
</Base>
