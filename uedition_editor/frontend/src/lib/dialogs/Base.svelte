<script lang="ts">
  import { Dialog } from "bits-ui";
  import { onMount } from "svelte";

  import { activeDialog, Dialogs } from "./Index.svelte";

  export const onOpenChange: ((open: boolean) => void) | null = null;
  export let open = false;

  function localOnOpenChange(open: boolean) {
    if (onOpenChange) {
      onOpenChange(open);
    }
    if (!open) {
      activeDialog.set(Dialogs.NONE);
    }
  }

  onMount(() => {
    open = true;
  });
</script>

<Dialog.Root bind:open onOpenChange={localOnOpenChange}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      <slot />
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
