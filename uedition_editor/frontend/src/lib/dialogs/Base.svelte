<script lang="ts">
  import { Dialog } from "bits-ui";
  import { onMount, type Snippet } from "svelte";

  import { appState } from "../../state.svelte";

  type BaseProps = {
    open?: boolean;
    onOpenChange?: ((open: boolean) => void) | undefined;
    children: Snippet;
  };

  let {
    open = $bindable(false),
    children,
    onOpenChange = undefined,
  }: BaseProps = $props();

  function localOnOpenChange(open: boolean) {
    if (onOpenChange) {
      onOpenChange(open);
    }
    if (!open) {
      appState.activeDialog = null;
    }
  }

  onMount(() => {
    open = true;
  });
</script>

<Dialog.Root bind:open onOpenChange={localOnOpenChange}>
  <Dialog.Portal>
    <Dialog.Overlay />
    <Dialog.Content>
      {@render children()}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
