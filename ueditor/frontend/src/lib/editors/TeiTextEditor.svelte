<script lang="ts">
  import { Toolbar } from "bits-ui";
  import { onMount, getContext } from "svelte";
  import { Editor, Node, Mark } from "@tiptap/core";
  import { Document } from "@tiptap/extension-document";
  import { Text } from "@tiptap/extension-text";
  import type { CreateQueryResult } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";

  export let section: TEITextSection | null = null;
  export let config: any | null;

  const uEditorConfig = getContext(
    "uEditorConfig",
  ) as CreateQueryResult<UEditorSettings>;
  let editorElement: HTMLElement | null = null;
  let editor: Editor | null = null;

  onMount(() => {
    if (editorElement !== null && $uEditorConfig.isSuccess) {
      const extensions: (Node | Mark)[] = [Document, Text];
      for (let blockConfig of $uEditorConfig.data.tei.blocks) {
        console.log(blockConfig);
        extensions.push(
          Node.create({
            name: blockConfig.name,
            group: "block",
            content: "inline*",
            attributes: {},
            renderHTML({ node, HTMLAttributes }) {
              HTMLAttributes["data-tei-block-" + node.type.name] = "";
              return [blockConfig.tag || "div", HTMLAttributes, 0];
            },
          }),
        );
      }
      for (let markConfig of $uEditorConfig.data.tei.marks) {
        extensions.push(
          Mark.create({
            name: markConfig.name,
            renderHTML({ mark, HTMLAttributes }) {
              HTMLAttributes["data-tei-mark-" + mark.type.name] = "";
              return [markConfig.tag || "span", HTMLAttributes, 0];
            },
          }),
        );
      }
      editor = new Editor({
        element: editorElement,
        extensions: extensions,
        content: section?.content,
        onTransaction: () => {
          editor = editor;
        },
      });
    }
  });

  function reloadContent() {
    if (section !== null && editor !== null) {
      editor.commands.setContent(section.content);
    }
  }
  $: if (section) {
    reloadContent();
  }

  function runAction(editor: Editor | null, action: any) {
    if (editor) {
      if (action.type === "set-block") {
        editor.commands.setNode(action.block);
      }
    }
  }
</script>

<div class="flex flex-row w-full h-full overflow-hidden">
  <div class="flex-1" bind:this={editorElement}></div>
  <div class="w-3/12 border-l border-gray-300 overflow-auto">
    {#if config && editor}
      {#each config.sidebar as sidebarBlock}
        {#if !sidebarBlock.condition || editor.isActive(sidebarBlock.condition.block)}
          <h2>{sidebarBlock.title}</h2>
          <Toolbar.Root>
            {#each sidebarBlock.items as item}
              {#if item.type == "set-block"}
                <Toolbar.Button
                  on:click={() => {
                    runAction(editor, item);
                  }}
                >
                  {#if item.icon}
                    <Icon path={item.icon} />
                    <span class="sr-only">{item.title}</span>
                  {:else}
                    {item.title}
                  {/if}
                </Toolbar.Button>
              {/if}
            {/each}
          </Toolbar.Root>
        {/if}
      {/each}
    {/if}
  </div>
</div>
