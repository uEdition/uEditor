<script lang="ts">
  import { Dialog } from "bits-ui";
  import { createQuery } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { version } from "../../about";
  import { appState } from "../../state.svelte";

  let { children } = $props();

  const apiStatus = createQuery(() => ({
    queryKey: [""],
    queryFn: apiQueryHandler<APIStatus>,
    refetchInterval: 60000,
  }));

  $effect(() => {
    if (apiStatus.isSuccess) {
      appState.apiStatus = apiStatus.data;
    } else {
      appState.apiStatus = null;
    }
  });

  let uEditorTimestamp = $derived.by(() => {
    if (appState.apiStatus?.version) {
      return new Date().getTime();
    } else {
      return new Date().getTime();
    }
  });
</script>

{#if appState.apiStatus && appState.apiStatus.ready}
  {@render children()}
  {#if appState.apiStatus.version !== version}
    <Dialog.Root open={true}>
      <Dialog.Trigger class="hidden" />
      <Dialog.Portal>
        <Dialog.Content
          escapeKeydownBehavior="ignore"
          interactOutsideBehavior="ignore"
          class="flex flex-col overflow-hidden"
          data-update-dialog
        >
          <Dialog.Title>μEditor update required</Dialog.Title>
          <div data-dialog-content-area>
            The μEditor has been updated and you need to reload the μEditor in
            order to benefit from the latest updates.
            <div data-dialog-buttons>
              <a href="/?timestamp={uEditorTimestamp}" data-button>Reload</a>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  {/if}
{/if}

<Dialog.Root
  open={(apiStatus.isSuccess && !apiStatus.data.ready) || apiStatus.isError}
>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content
      escapeKeydownBehavior="ignore"
      interactOutsideBehavior="ignore"
      data-dialog-role="error"
      class="flex flex-col overflow-hidden left-10"
    >
      <Dialog.Title>μEditor not ready</Dialog.Title>
      <div data-dialog-content-area>
        <p>
          Unfortunately the μEditor server is not ready. Please check the server
          logs to determine what the issue is.
        </p>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
