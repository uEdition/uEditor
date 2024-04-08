<script lang="ts"></script>

<svelte:head>
  <title>uEditor</title>
</svelte:head>

<main class="flex flex-col w-screen h-screen overflow-hidden">
  <nav aria-label="Toolbar" class="bg-blue-100">Editor Toolbar</nav>
  <div class="flex flex-row flex-1">
    <nav aria-label="Files" class="w-3/12 bg-red-100">
      Navigation
    </nav>
    <div class="flex-1 bg-green-100">
      Editor Content
    </div>
    <div class="w-3/12 bg-orange-100">
      Editor Sidebar
    </div>
  </div>
  <footer class="bg-yellow-100">Editor footer</footer>
</main>
