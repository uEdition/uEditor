<script lang="ts">
  import { Dialog } from "bits-ui";

  import Base from "../Base.svelte";
  import { appState } from "../../../state.svelte";
  import { version } from "../../../about";

  let uEditorTimestamp = $derived.by(() => {
    if (appState.apiStatus?.version) {
      return new Date().getTime();
    } else {
      return new Date().getTime();
    }
  });
</script>

<Base>
  <Dialog.Title>About the μEditor</Dialog.Title>
  <div data-dialog-content-area>
    <p class="mb-2">
      The <a href="https://ueditor.readthedocs.io/en/latest/" target="_blank"
        >μEditor</a
      >
      is a web-based editor for
      <a href="https://uedition.readthedocs.io/latest/" target="_blank"
        >μEditions</a
      >. It is fully accessible and compatible will all modern browsers.
    </p>
    <p class="mb-2">
      Help and documentation can be found on the <a
        href="https://ueditor.readthedocs.io/en/latest/"
        target="_blank">μEditor ReadTheDocs</a
      > site.
    </p>
    <p class="mb-2">
      If you run into any issues, then please report them on the <a
        href="https://github.com/uEdition/uEditor/issues"
        target="_blank">μEditor Github Issues</a
      >.
    </p>
    <p class="mb-2">
      You are running version {appState.apiStatus
        ?.version}.{#if appState.apiStatus?.version !== version}
        The version of the frontend does not match the version of the server.
        Please <a href="/?timestamp={uEditorTimestamp}">reload the page</a
        >.{/if}
    </p>
    {#if appState.apiStatus?.git.enabled}
      <p class="mb-2">Git support is enabled.</p>
    {/if}
    <div data-dialog-buttons>
      <Dialog.Close type="button" data-button>Close</Dialog.Close>
    </div>
  </div>
</Base>
