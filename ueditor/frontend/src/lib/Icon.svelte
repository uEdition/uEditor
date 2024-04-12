<script lang="ts">
  export let size = "w-6 h-6";
  export let label: string | null = null;
  export let path: string | null = null;
</script>

{#if path === null}
  <span class="block {size}"></span>
{:else}
  <svg
    class="{size} fill-current"
    viewBox="0 0 24 24"
    aria-hidden={label === null ? "true" : "false"}
  >
    {#if label !== null}
      <title>{label}</title>
    {/if}
    <path d={path} />
  </svg>
{/if}
