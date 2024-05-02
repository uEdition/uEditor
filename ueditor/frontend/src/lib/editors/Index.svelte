<script lang="ts">
  import { derived } from "svelte/store";

  import { currentFile } from "../../stores";

  let loading = false;
  const CODEMIRROR_MIMETYPES = [
    "application/yaml",
    "text/markdown",
    "application/gitignore",
  ];

  const currentEditorType = derived(currentFile, (currentFile) => {
    if (currentFile) {
      if (currentFile.type === "folder") {
        return "Folder";
      } else if (CODEMIRROR_MIMETYPES.indexOf(currentFile.mimetype) >= 0) {
        return "CodeMirror";
      }
    }
    return null;
  });

  const currentEditor = derived(
    currentEditorType,
    (currentEditorType, set) => {
      let promise = null;
      if (currentEditorType === "Folder") {
        promise = import("./FolderEditor.svelte");
      } else if (currentEditorType === "CodeMirror") {
        promise = import("./CodeMirrorEditor.svelte");
      }
      if (promise) {
        loading = true;
        promise.then(
          (loadedModule) => {
            set(loadedModule.default);
            loading = false;
          },
          () => {
            loading = false;
          },
        );
      } else {
        set(null);
      }
    },
    null as any,
  );
</script>

{#if $currentFile !== null}
  {#if $currentEditor !== null}
    <svelte:component this={$currentEditor} />
  {:else if loading}
    <div class="flex-1 px-2 py-1">Loading the editor. Please wait...</div>
  {:else}
    <div class="flex-1 px-2 py-1 text-rose-700">
      Unfortunately the μEditor does not know how to edit this file.
    </div>
  {/if}
{:else}
  <div class="flex-1 relative px-2 py-1 text-gray-700">
    Please select a file or folder from the file-browser on the left
  </div>
{/if}