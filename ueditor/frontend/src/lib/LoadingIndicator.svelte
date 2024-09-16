<script lang="ts">
  import { mdiSync } from "@mdi/js";

  import Icon from "./Icon.svelte";
</script>

<div
  class="absolute left-1/2 top-1/2 transform -translate-x-1/2 -translate-y-1/2"
>
  <p class="sr-only"><slot></slot></p>
  <Icon path={mdiSync} class="w-12 h-12 animate-spin"></Icon>
</div>
