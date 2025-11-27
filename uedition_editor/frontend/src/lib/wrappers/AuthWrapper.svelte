<script lang="ts">
  import { Dialog } from "bits-ui";
  import {
    createMutation,
    createQuery,
    useQueryClient,
  } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { appState } from "../../state.svelte";

  const { children } = $props();

  const queryClient = useQueryClient();

  const currentUser = createQuery(() => ({
    queryKey: ["auth", "user"],
    queryFn: apiQueryHandler<CurrentUser>,
    retry: false,
    refetchInterval: 20000,
  }));

  const authStatus = $derived.by(() => {
    if (currentUser.isSuccess) {
      return "authenticated";
    } else if (currentUser.isError) {
      if (
        appState.apiStatus?.auth.provider === "no-auth" ||
        appState.apiStatus?.auth.provider === "email"
      ) {
        window
          .fetch("/api/auth/login", {
            method: "POST",
          })
          .then((response) => {
            if (response.ok) {
              queryClient.invalidateQueries({ queryKey: ["auth"] });
            }
          });
        return "authenticating";
      } else {
        return "error";
      }
    } else {
      return currentUser.status;
    }
  });

  $effect(() => {
    if (currentUser.isSuccess) {
      appState.currentUser = currentUser.data;
    } else {
      appState.currentUser = null;
    }
  });

  let authEmail = $state("");
  let authPassword = $state("");
  const emailPasswordLogin = createMutation(() => ({
    mutationFn: async ([email, password]: [string, string]) => {
      const response = await window.fetch("/api/auth/login", {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });
      if (response.ok) {
        queryClient.invalidateQueries({ queryKey: ["auth"] });
        queryClient.invalidateQueries({ queryKey: ["branches"] });
        authEmail = "";
        authPassword = "";
      } else {
        throw "Authentication failed";
      }
    },
  }));
</script>

{#if authStatus === "authenticated"}
  {@render children()}
{/if}

<Dialog.Root open={authStatus === "pending"}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay class="z-40" />
    <Dialog.Content
      class="flex flex-col overflow-hidden z-50"
      escapeKeydownBehavior="ignore"
      interactOutsideBehavior="ignore"
    >
      <Dialog.Title>Authenticating</Dialog.Title>
      <div data-dialog-content-area>
        <p>You are being authenticated. Please wait.</p>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root open={!appState.ui.hasLoggedOut && authStatus === "error"}>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay class="z-40" />
    <Dialog.Content
      class="flex flex-col overflow-hidden z-50"
      escapeKeydownBehavior="ignore"
      interactOutsideBehavior="ignore"
    >
      <Dialog.Title>Login</Dialog.Title>
      {#if appState.apiStatus?.auth.provider === "email-password"}
        <form
          data-dialog-content-area
          onsubmit={(ev) => {
            ev.preventDefault();
            if (!emailPasswordLogin.isPending) {
              emailPasswordLogin.mutate([authEmail, authPassword]);
            }
          }}
        >
          <label>
            <span data-form-field-label>E-Mail</span>
            <input bind:value={authEmail} type="text" data-form-field-text />
            {#if emailPasswordLogin.isError}
              <span data-form-field-error
                >Incorred e-mail address or password</span
              >
            {/if}
          </label>
          <label>
            <span data-form-field-label>Password</span>
            <input
              bind:value={authPassword}
              type="password"
              data-form-field-text
            />
            {#if emailPasswordLogin.isError}
              <span data-form-field-error
                >Incorred e-mail address or password</span
              >
            {/if}
          </label>
          <div data-dialog-buttons>
            {#if emailPasswordLogin.isPending}
              <span data-button class="inline-flex">Logging in...</span>
            {:else}
              <button type="submit" data-button>Login</button>
            {/if}
          </div>
        </form>
      {:else if appState.apiStatus?.auth.provider === "github"}
        <div data-dialog-content-area>
          <p>Click on the link below to log in via GitHub.</p>
          <div class="my-8 text-center">
            <a href="/api/auth/oidc/login" data-button>Log in via GitHub</a>
          </div>
        </div>
      {/if}
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>

<Dialog.Root
  open={appState.ui.hasLoggedOut}
  onOpenChange={(isOpen) => {
    if (!isOpen) {
      appState.ui.hasLoggedOut = false;
    }
  }}
>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay class="z-40" />
    <Dialog.Content class="flex flex-col overflow-hidden z-50">
      <Dialog.Title>Logged out</Dialog.Title>
      <div data-dialog-content-area>
        <p class="mb-4">
          You have logged out. You can now close the browser tab or window.
        </p>
        <div data-dialog-buttons>
          <Dialog.Close data-button>Close</Dialog.Close>
        </div>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
