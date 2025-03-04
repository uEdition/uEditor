<script lang="ts">
  import { Dialog } from "bits-ui";
  import { onDestroy, setContext } from "svelte";
  import { derived } from "svelte/store";
  import { fade } from "svelte/transition";
  import { createQuery, useQueryClient } from "@tanstack/svelte-query";

  import { apiQueryHandler } from "../../util";
  import { useApiStatus } from "../../stores";

  const queryClient = useQueryClient();
  const apiStatus = useApiStatus();

  const currentUser = createQuery({
    queryKey: ["auth", "user"],
    queryFn: apiQueryHandler<CurrentUser>,
    retry: false,
    refetchInterval: 20000,
  });
  setContext("currentUser", currentUser);

  const authStatus = derived(
    [apiStatus, currentUser],
    ([apiStatus, currentUser]) => {
      if (apiStatus.isSuccess) {
        if (currentUser.isSuccess) {
          return "authenticated";
        } else if (currentUser.isError) {
          if (
            apiStatus.data.auth.provider === "no-auth" ||
            apiStatus.data.auth.provider === "email"
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
      }
      return apiStatus.status;
    }
  );
</script>

<slot></slot>

<Dialog.Root
  open={$authStatus === "pending" || $authStatus === "error"}
  closeOnEscape={false}
  closeOnOutsideClick={false}
>
  <Dialog.Trigger class="hidden" />
  <Dialog.Portal>
    <Dialog.Overlay transition={fade} class="z-40" />
    <Dialog.Content class="flex flex-col overflow-hidden z-50">
      <Dialog.Title>Login</Dialog.Title>
      <div data-dialog-content-area>
        <p>You are being authenticated. Please wait.</p>
      </div>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
