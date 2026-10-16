<script lang="ts">
  import { QueryClient, QueryClientProvider } from "@tanstack/svelte-query";

  import Root from "./Root.svelte";
  import ApiStatusWrapper from "./lib/wrappers/ApiStatusWrapper.svelte";
  import AuthWrapper from "./lib/wrappers/AuthWrapper.svelte";
  import BranchWrapper from "./lib/wrappers/BranchWrapper.svelte";
  import ConfigWrapper from "./lib/wrappers/ConfigWrapper.svelte";
  import PreviewWrapper from "./lib/wrappers/PreviewWrapper.svelte";

  const queryClient = new QueryClient();
</script>

<QueryClientProvider client={queryClient}>
  <ApiStatusWrapper>
    <AuthWrapper>
      <BranchWrapper>
        <ConfigWrapper>
          <PreviewWrapper>
            <Root />
          </PreviewWrapper>
        </ConfigWrapper>
      </BranchWrapper>
    </AuthWrapper>
  </ApiStatusWrapper>
</QueryClientProvider>
