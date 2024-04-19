<script lang="ts">
  import { Dialog } from "bits-ui";
  import { useQueryClient } from "@tanstack/svelte-query";

  import { currentBranch, currentFile } from "../../stores";

  export let newType: "file" | "directory";
  const queryClient = useQueryClient();
  let dialogOpen = false;
  let newFileName = "";
  let errorMessage = "";

  async function createNewFile(ev: Event) {
    ev.preventDefault();
    const response = await fetch(
      "/api/branches/" +
        $currentBranch +
        "/files/" +
        $currentFile?.fullpath +
        "/" +
        newFileName,
      {
        method: "POST",
        headers: { "X-uEditor-New-Type": newType },
      },
    );
    if (response.ok) {
      dialogOpen = false;
      queryClient.invalidateQueries({
        queryKey: ["branches", $currentBranch, "files/"],
      });
    } else {
      errorMessage = (await response.json()).detail[0].msg;
      errorMessage = errorMessage[0].toUpperCase() + errorMessage.substring(1);
    }
  }

  function openDialog() {
    newFileName = "";
    errorMessage = "";
  }
</script>

<Dialog.Root bind:open={dialogOpen} onOpenChange={openDialog}>
  <Dialog.Trigger data-button
    >Create a new {newType === "file" ? "File" : "Directory"}</Dialog.Trigger
  >
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <Dialog.Title
        >Create a new {newType === "file" ? "File" : "Directory"} in
        <span class="font-mono"
          >{$currentFile?.fullpath ? $currentFile?.fullpath : "/"}</span
        ></Dialog.Title
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
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
