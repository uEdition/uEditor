<script lang="ts">
  import { Dialog } from "bits-ui";
  import { mdiCheck, mdiCloseThick, mdiSync, mdiTimerSandEmpty } from "@mdi/js";
  import { useQueryClient } from "@tanstack/svelte-query";

  import { currentFile, useCurrentBranch } from "../../../stores";
  import { Dialogs, activeDialog } from "../Index.svelte";
  import Base from "../Base.svelte";
  import Icon from "../../Icon.svelte";

  enum UploadStatus {
    READY = 0,
    ACTIVE,
    SUCCESS,
    FAILED,
  }

  const queryClient = useQueryClient();
  const currentBranch = useCurrentBranch();
  let fileElement: HTMLInputElement | null = null;
  let submitElement: HTMLButtonElement | null = null;
  let dropFile = false;
  let open = false;
  let filesToUpload: [File, UploadStatus][] = [];
  let uploadComplete = false;

  /**
   * Event handler for when the dialog opens/closes
   *
   * @param open Whether the dialog is open or closed
   */
  function openDialog(open: boolean) {
    if (!open) {
      activeDialog.set(Dialogs.NONE);
    }
  }

  /**
   * Handle the form submission
   *
   * @param ev Form submission event
   */
  async function uploadFile(ev: Event) {
    ev.preventDefault();
    if (fileElement && fileElement.files) {
      filesToUpload = [];
      for (let file of fileElement.files) {
        filesToUpload.push([file, UploadStatus.READY]);
      }
      if (filesToUpload.length > 0) {
        uploadFiles();
      }
    }
  }

  /**
   * Handle the drag-and-drop form upload event.
   *
   * @param ev The drag event
   */
  async function uploadDroppedFile(ev: DragEvent) {
    ev.preventDefault();
    filesToUpload = [];
    if (ev.dataTransfer && ev.dataTransfer.items) {
      for (let item of ev.dataTransfer.items) {
        if (item.kind === "file") {
          const file = item.getAsFile();
          if (file !== null) {
            filesToUpload.push([file, UploadStatus.READY]);
          }
        }
      }
      if (filesToUpload.length > 0) {
        uploadFiles();
      }
    }
  }

  /**
   * Handle the actual file upload.
   */
  async function uploadFiles() {
    uploadComplete = false;
    for (let upload of filesToUpload) {
      if (!open) {
        break;
      }
      upload[1] = UploadStatus.ACTIVE;
      filesToUpload = filesToUpload;
      const response = await fetch(
        "/api/branches/" +
          $currentBranch?.id +
          "/files/" +
          $currentFile?.fullpath +
          "/" +
          upload[0].name,
        {
          method: "POST",
          headers: { "X-uEditor-New-Type": "file" },
        }
      );
      if (response.ok) {
        const formData = new FormData();
        formData.append("content", upload[0]);
        const response = await fetch(
          "/api/branches/" +
            $currentBranch?.id +
            "/files/" +
            $currentFile?.fullpath +
            "/" +
            upload[0].name,
          {
            method: "PUT",
            body: formData,
          }
        );
        if (response.ok) {
          upload[1] = UploadStatus.SUCCESS;
        } else {
          upload[1] = UploadStatus.FAILED;
        }
        filesToUpload = filesToUpload;
      } else {
        upload[1] = UploadStatus.FAILED;
        filesToUpload = filesToUpload;
      }
    }
    queryClient.invalidateQueries({
      queryKey: ["branches", $currentBranch?.id, "files/"],
    });
    uploadComplete = true;
  }
</script>

<Base bind:open onOpenChange={openDialog}>
  <Dialog.Title
    >{#if filesToUpload.length > 0}Uploading{:else}Upload{/if} Files to "{$currentFile?.fullpath
      ? $currentFile?.fullpath
      : "/"}"</Dialog.Title
  >
  {#if filesToUpload.length === 0}
    <form data-dialog-content-area on:submit={uploadFile}>
      <label
        on:drop={uploadDroppedFile}
        on:dragover={(ev) => {
          ev.preventDefault();
          dropFile = true;
        }}
        on:dragleave={() => {
          dropFile = false;
        }}
        class="flex justify-center items-center h-20 border-fuchsia-700 border-2 {dropFile
          ? 'border-solid'
          : 'border-dashed'} rounded"
      >
        <span>Drop a file to upload or click to select a file to upload.</span>
        <input
          bind:this={fileElement}
          type="file"
          class="sr-only"
          on:change={() => {
            if (submitElement) {
              submitElement.click();
            }
          }}
        />
      </label>
      <div data-dialog-buttons>
        <Dialog.Close data-button>Don't upload</Dialog.Close>
        <button
          bind:this={submitElement}
          type="submit"
          data-button
          class="sr-only">Upload</button
        >
      </div>
    </form>
  {:else}
    <div data-dialog-content-area="">
      <ul>
        {#each filesToUpload as [file, status]}
          <li class="flex flex-row space-x-4">
            <span class="flex-1">{file.name}</span>
            {#if status === UploadStatus.READY}
              <span class="sr-only">waiting to upload</span>
              <Icon path={mdiTimerSandEmpty} />
            {:else if status == UploadStatus.ACTIVE}
              <span class="sr-only">uploading</span>
              <Icon
                path={mdiSync}
                class="w-6 h-6 animate-spin text-fuchsia-700"
              />
            {:else if status === UploadStatus.SUCCESS}
              <span class="sr-only">successfully uploaded</span>
              <Icon path={mdiCheck} class="w-6 h-6 text-lime-500" />
            {:else if status === UploadStatus.FAILED}
              <span class="sr-only">failed to upload</span>
              <Icon path={mdiCloseThick} class="w-6 h-6 text-rose-700" />
            {/if}
          </li>
        {/each}
      </ul>
      <div data-dialog-buttons="">
        <Dialog.Close data-button
          >{#if uploadComplete}Close{:else}Cancel upload{/if}</Dialog.Close
        >
      </div>
    </div>
  {/if}
</Base>
