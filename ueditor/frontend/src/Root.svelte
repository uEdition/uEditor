<script lang="ts">
  import { Menubar, Select } from "bits-ui";
  import { mdiBarn, mdiChevronDown } from "@mdi/js";

  let selected = { value: "" };
</script>

<svelte:head>
  <title>uEditor</title>
</svelte:head>

<main class="flex flex-col w-screen h-screen overflow-hidden">
  <Menubar.Root class="border-b border-silver-600">
    <Menubar.Menu>
      <Select.Root bind:selected>
        <Select.Trigger class="px-2 py-1">
          <svg viewBox="0 0 24 24" class="inline-block w-6 h-6"
            ><path d={mdiBarn} /></svg
          >
          <Select.Value placeholder="Select the Branch to work on"
          ></Select.Value>
          <svg viewBox="0 0 24 24" class="inline-block w-6 h-6"
            ><path d={mdiChevronDown} /></svg
          >
        </Select.Trigger>
        <Select.Content class="z-50 bg-white">
          <Select.Item value="a" label="A label goes here" class="w-full bg-blue-500 data-[highlighted]:bg-red-500"
            >A label goes here
            </Select.Item
          >
          <Select.Item value="b" label="B label goes here" class="w-full bg-blue-500 data-[highlighted]:bg-red-500"
            >B label goes here</Select.Item
          >
        </Select.Content>
      </Select.Root>
    </Menubar.Menu>
  </Menubar.Root>
  <!--<nav aria-label="Toolbar" class="bg-blue-100">Editor Toolbar</nav>-->
  <div class="flex flex-row flex-1">
    <nav aria-label="Files" class="w-3/12 bg-red-100">
      Navigation - {selected.value ? selected.value : ""}
    </nav>
    <div class="flex-1 bg-green-100">Editor Content</div>
    <div class="w-3/12 bg-orange-100">Editor Sidebar</div>
  </div>
  <footer class="bg-yellow-100">Editor footer</footer>
</main>
