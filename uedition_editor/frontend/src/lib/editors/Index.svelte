<script lang="ts">
  import { derived } from "svelte/store";

  import { appState } from "../../state.svelte";

  const CODEMIRROR_MIMETYPES = [
    "application/gitignore",
    "application/json",
    "application/toml",
    "application/yaml",
  ];
  const TEI_MIMETYPES = ["application/tei+xml"];
  let CurrentEditor: any | null = $state(null);
  let loading = $state(false);

  $effect(() => {
    let promise = null;
    if (appState.currentFile) {
      if (appState.currentFile.type === "folder") {
        promise = import("./FolderEditor.svelte");
      } else if (
        CODEMIRROR_MIMETYPES.indexOf(appState.currentFile.mimetype) >= 0 ||
        appState.currentFile.mimetype.startsWith("text/")
      ) {
        promise = import("./CodeMirrorEditor.svelte");
      } else if (TEI_MIMETYPES.indexOf(appState.currentFile.mimetype) >= 0) {
        promise = import("./TeiEditor.svelte");
      } else if (appState.currentFile.mimetype.startsWith("image/")) {
        promise = import("./ImageEditor.svelte");
      } else if (appState.currentFile.mimetype === "application/pdf") {
        promise = import("./PdfEditor.svelte");
      }
    }
    if (promise !== null) {
      loading = true;
      promise
        .then((loadedModule) => {
          CurrentEditor = loadedModule.default;
        })
        .finally(() => {
          loading = false;
        });
    } else {
      CurrentEditor = null;
    }
  });
</script>

{#if appState.currentFile !== null && appState.currentBranch !== null}
  {#if CurrentEditor !== null}
    {#key appState.currentBranch.id}
      <CurrentEditor></CurrentEditor>
    {/key}
  {:else if loading}
    <div class="flex-1 px-2 py-1">Loading the editor. Please wait...</div>
  {:else}
    <div class="flex-1 px-2 py-1 text-rose-700">
      Unfortunately the μEditor does not know how to edit this file ({appState
        .currentFile.mimetype}).
    </div>
  {/if}
{:else}
  <div class="flex-1 relative px-2 py-1 text-gray-700">
    Please select a file or folder from the file-browser on the left
  </div>
{/if}
