<script lang="ts">
  export let label: string | null = null;
  export let path: string | null = null;
  let cls = "w-6 h-6";
  export { cls as class };
</script>

{#if path === null}
  <span class="block {cls}"></span>
{:else}
  <svg
    class="fill-current {cls}"
    viewBox="0 0 24 24"
    aria-hidden={label === null ? "true" : "false"}
  >
    {#if label !== null}
      <title>{label}</title>
    {/if}
    <path d={path} />
  </svg>
{/if}
