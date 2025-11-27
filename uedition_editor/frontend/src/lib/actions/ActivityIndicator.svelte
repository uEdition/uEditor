<script lang="ts">
  import { Popover } from "bits-ui";
  import { useIsFetching } from "@tanstack/svelte-query";

  import { appState } from "../../state.svelte";

  const isFetching = useIsFetching();
  const activeActivities = $derived.by(() => {
    const activities = [];
    if (isFetching.current > 0) {
      activities.push({ label: "Fetching data" });
    }
    for (const action of appState.actions) {
      if (action.action === "LoadTextFile") {
        activities.push({ label: "Loading file contents" });
      } else if (action.action === "SaveCurrentFile") {
        activities.push({ label: "Saving file contents" });
      } else if (action.action === "SynchroniseBranches") {
        activities.push({ label: "Synchronising branches" });
      }
    }
    return activities;
  });
</script>

<Popover.Root>
  <Popover.Trigger class="inline-flex items-center">
    {#if activeActivities.length === 0}
      <span>Idle</span>
    {:else if activeActivities.length === 1}
      <span>1 activity running</span>
    {:else}
      <span>{activeActivities.length} activities running</span>
    {/if}
  </Popover.Trigger>
  <Popover.Content class="z-50 bg-white shadow-lg">
    <ul class="border border-slate-300">
      {#each activeActivities as activity}
        <li class="px-3 py-1">
          {activity.label}
        </li>
      {:else}
        <li class="px-3 py-1">Nothing is happening</li>
      {/each}
    </ul>
  </Popover.Content>
</Popover.Root>
