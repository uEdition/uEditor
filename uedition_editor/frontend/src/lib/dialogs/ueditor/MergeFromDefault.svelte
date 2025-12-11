<script lang="ts">
  import { Dialog } from "bits-ui";
  import { mdiSync } from "@mdi/js";
  import { createMutation, useQueryClient } from "@tanstack/svelte-query";

  import Base from "../Base.svelte";
  import Icon from "../../Icon.svelte";
  import { appState } from "../../../state.svelte";
  import { title } from "../../../util";

  const queryClient = useQueryClient();
  let confirmBranchTitle = $state("");
  let errorMessage = $state("");

  function openDialog(open: boolean) {
    if (open) {
      confirmBranchTitle = "";
    }
  }

  const mergeBranchFromDefault = createMutation(() => ({
    mutationFn: async () => {
      const response = await window.fetch(
        "/api/branches/" + appState.currentBranch?.id + "/merge-from-default",
        {
          method: "POST",
          headers: {
            Accept: "application/json",
          },
        },
      );
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["branches"] });
        appState.activeDialog = null;
      } else {
        errorMessage = (await response.json()).detail[0].msg;
        errorMessage =
          errorMessage[0].toUpperCase() + errorMessage.substring(1);
      }
    },
  }));

  function startMergeBranchFromDefault(ev: Event) {
    ev.preventDefault();
    mergeBranchFromDefault.mutate();
  }
</script>

<Base onOpenChange={openDialog}>
  <Dialog.Title>Merge changes from the default branch</Dialog.Title>
  <form data-dialog-content-area onsubmit={startMergeBranchFromDefault}>
    <p class="mb-4">
      Please confirm you wish to merge all changes from the default branch <span
        class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
        >{title(appState.apiStatus?.git.default_branch)}</span
      >
      into the current branch<span
        class="inline-block mx-1 px-2 border border-fuchsia-700 rounded font-bold"
        >{appState.currentBranch?.title}</span
      >. This cannot be undone.
    </p>
    {#if errorMessage}
      <p data-form-field-error>{errorMessage}</p>
    {/if}
    <div data-dialog-buttons>
      {#if mergeBranchFromDefault.isPending}
        <span data-button class="inline-flex"
          ><Icon path={mdiSync} class="block w-6 h-6 animate-spin" /><span
            >Merging...</span
          ></span
        >
      {:else}
        <Dialog.Close type="button" data-button>Don't merge</Dialog.Close>
        <button type="submit" data-button>Merge</button>
      {/if}
    </div>
  </form>
</Base>
