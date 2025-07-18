<script lang="ts">
  import { Dialog } from "bits-ui";
  import { setContext } from "svelte";
  import { fade } from "svelte/transition";
  import { createQuery } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { version } from "../../about";

  const apiStatus = createQuery({
    queryKey: [""],
    queryFn: apiQueryHandler<APIStatus>,
    refetchInterval: 60000,
  });
  setContext("apiStatus", apiStatus);
</script>

{#if $apiStatus.isSuccess}
  <slot></slot>
  {#if $apiStatus.data.version !== version}
    <Dialog.Root open={true} closeOnEscape={false} closeOnOutsideClick={false}>
      <Dialog.Trigger class="hidden" />
      <Dialog.Portal>
        <Dialog.Content
          class="flex flex-col overflow-hidden"
          data-update-dialog
        >
          <Dialog.Title>μEditor update required</Dialog.Title>
          <div data-dialog-content-area>
            The μEditor has been updated and you need to reload the μEditor in
            order to benefit from the latest updates.
            <div data-dialog-buttons>
              <a href="/" data-button>Reload</a>
            </div>
          </div>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  {/if}
{/if}

<Dialog.Root
  open={$apiStatus.isSuccess && !$apiStatus.data.ready}
  closeOnEscape={false}
  closeOnOutsideClick={false}
>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay transition={fade} />
    <Dialog.Content
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
