<script lang="ts">
  import { Dialog } from "bits-ui";
  import { useQueryClient } from "@tanstack/svelte-query";

  import { currentBranch, currentFile } from "../../stores";

  export let newType: "file" | "directory";
  const queryClient = useQueryClient();
  let dialogOpen = false;
  let newFileName = "";

  async function createNewFile(ev: Event) {
    ev.preventDefault();
    const response = await fetch(
      "/api/files/" + $currentFile?.fullpath + "/" + newFileName,
      {
        method: "POST",
      },
    );
    if (response.ok) {
      dialogOpen = false;
      queryClient.invalidateQueries({
        queryKey: ["branches", $currentBranch, "files/"],
      });
    }
  }
</script>

<Dialog.Root bind:open={dialogOpen}>
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
          <span class="block text-sm pl-2">New Filename</span>
          <input
            bind:value={newFileName}
            class="block w-full px-3 py-2 border transition-colors border-slate-300 focus:border-fuchsia-700 rounded"
            type="text"
          />
        </label>
        <div data-dialog-buttons>
          <Dialog.Close data-button>Don't create</Dialog.Close>
          <button type="submit" data-button>Create</button>
        </div>
      </form>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
