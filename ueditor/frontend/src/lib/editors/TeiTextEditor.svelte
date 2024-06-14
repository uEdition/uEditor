<script lang="ts">
  import { onMount, onDestroy, getContext } from "svelte";
  import { Editor, Node } from "@tiptap/core";
  import { Document } from "@tiptap/extension-document";
  import { Text } from "@tiptap/extension-text";
  import type { CreateQueryResult } from "@tanstack/svelte-query";

  export let section: TEITextSection | null = null;

  const uEditorConfig = getContext(
    "uEditorConfig"
  ) as CreateQueryResult<UEditorSettings>;
  let editorElement: HTMLElement | null = null;
  let editor: Editor | null = null;

  onMount(() => {
    if (editorElement !== null && $uEditorConfig.isSuccess) {
      const extensions = [Document, Text];
      for (let blockConfig of $uEditorConfig.data.tei.blocks) {
        extensions.push(
          Node.create({
            name: blockConfig.name,
            group: "block",
            content: "inline*",
            renderHTML({ HTMLAttributes }) {
              return ["div", HTMLAttributes, 0];
            },
          })
        );
        console.log(blockConfig);
      }
      console.log(section);
      editor = new Editor({
        element: editorElement,
        extensions: extensions,
        content: section?.content,
      });
    }
  });
</script>

<div class="flex flex-row w-full h-full overflow-hidden">
  <div class="flex-1" bind:this={editorElement}></div>
  <div class="w-3/12 border-l border-gray-300 overflow-auto">Sidebar</div>
</div>
