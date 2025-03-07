<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import { Editor, Node } from "@tiptap/core";
  import { Document } from "@tiptap/extension-document";
  import { Text } from "@tiptap/extension-text";

  let element: HTMLElement | null = null;
  let editor: Editor | null = null;

  const Block = Node.create({
    name: "block",
    group: "block",
    content: "inline*",
    renderHTML({ HTMLAttributes }) {
      return ["div", HTMLAttributes, 0];
    },
  });

  onMount(() => {
    if (element) {
      editor = new Editor({
        element: element,
        extensions: [Document, Text, Block],
        content: "",
        onTransaction: () => {
          if (editor) {
            editor = editor;
          }
        },
      });
    }
  });

  onDestroy(() => {
    if (editor) {
      editor.destroy();
    }
  });
</script>

{#if editor}
  <button
    on:click={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
    class:active={editor.isActive("heading", { level: 1 })}
  >
    H1
  </button>
  <button
    on:click={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
    class:active={editor.isActive("heading", { level: 2 })}
  >
    H2
  </button>
  <button
    on:click={() => editor.chain().focus().setParagraph().run()}
    class:active={editor.isActive("paragraph")}
  >
    P
  </button>
{/if}

<div bind:this={element} />

<style>
  button.active {
    background: black;
    color: white;
  }
</style>
