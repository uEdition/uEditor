<script lang="ts">
  import { Combobox, Toolbar, type Selected } from "bits-ui";
  import { mdiChevronDown, mdiChevronUp } from "@mdi/js";
  import { onMount, getContext } from "svelte";
  import { Editor, Node, Mark } from "@tiptap/core";
  import { Document } from "@tiptap/extension-document";
  import { Text } from "@tiptap/extension-text";
  import type { CreateQueryResult } from "@tanstack/svelte-query";

  import Icon from "../Icon.svelte";
  import { textForFirstNodeOfTipTapDocument } from "../../util";

  export let section: TEITextSection | null = null;
  export let config: any | null;
  export let sections: TEIDocument;

  const uEditorConfig = getContext(
    "uEditorConfig",
  ) as CreateQueryResult<UEditorSettings>;
  let editorElement: HTMLElement | null = null;
  let editor: Editor | null = null;

  onMount(() => {
    if (editorElement !== null && $uEditorConfig.isSuccess) {
      const extensions: (Node | Mark)[] = [Document, Text];
      for (let blockConfig of $uEditorConfig.data.tei.blocks) {
        extensions.push(
          Node.create({
            name: blockConfig.name,
            group: "block",
            content: "inline*",
            addAttributes() {
              return Object.fromEntries(
                blockConfig.attributes.map((attr) => {
                  return [
                    attr.name,
                    {
                      default: attr.default,
                      renderHTML(attributes) {
                        return {
                          ["data-tei-attribute-" + attr.name]:
                            attributes[attr.name],
                        };
                      },
                    },
                  ];
                }),
              );
            },
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
            addAttributes() {
              return Object.fromEntries(
                markConfig.attributes.map((attr) => {
                  return [
                    attr.name,
                    {
                      default: attr.default,
                      renderHTML(attributes) {
                        return {
                          ["data-tei-attribute-" + attr.name]:
                            attributes[attr.name],
                        };
                      },
                    },
                  ];
                }),
              );
            },
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

  function runAction(
    editor: Editor | null,
    action: UEditorTEIActions,
    evOrSelected: Event | Selected<any>,
  ) {
    if (editor) {
      if (action.type === "set-block") {
        editor.chain().focus().setNode(action.block).run();
      } else if (action.type == "toggle-mark") {
        editor.chain().focus().toggleMark(action.mark).run();
      } else if (action.type === "select-block-attribute") {
        editor
          .chain()
          .focus()
          .updateAttributes(action.block, {
            [action.name]: ((evOrSelected as Event).target as HTMLSelectElement)
              .value,
          })
          .run();
      } else if (action.type === "select-cross-reference-attribute") {
        editor
          .chain()
          .focus()
          .extendMarkRange(action.mark)
          .updateAttributes(action.mark, {
            [action.name]: (evOrSelected as Selected<string>).value,
          })
          .run();
      }
    }
  }
</script>

<div class="flex flex-row w-full h-full overflow-hidden">
  <div class="flex-1" bind:this={editorElement}></div>
  <div class="w-3/12 px-3 py-2 border-l border-gray-300 overflow-auto">
    {#if config && editor}
      {#each config.sidebar as sidebarBlock}
        {#if !sidebarBlock.condition || editor.isActive(sidebarBlock.condition.node)}
          <section class="mb-4">
            <h2 class="font-bold mb-2">{sidebarBlock.title}</h2>
            {#if sidebarBlock.type === "toolbar"}
              <Toolbar.Root>
                {#each sidebarBlock.items as item}
                  {#if item.type === "set-block" || item.type === "toggle-mark"}
                    <Toolbar.Button
                      aria-pressed={(item.type === "set-block" &&
                        editor.isActive(item.block)) ||
                        (item.type === "toggle-mark" &&
                          editor.isActive(item.mark))}
                      on:click={(ev) => {
                        runAction(editor, item, ev);
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
            {:else if sidebarBlock.type === "form"}
              <div class="flex flex-row">
                {#each sidebarBlock.items as item}
                  {#if item.type === "select-block-attribute"}
                    {#key editor}
                      <label>
                        <span class="sr-only">{item.title}</span>
                        <select
                          value={editor.getAttributes(item.block)[item.name]}
                          on:change={(ev) => {
                            runAction(editor, item, ev);
                          }}
                          data-combobox-input=""
                          class="bg-white"
                        >
                          {#each item.values as value, idx}
                            <option value={value.value}>{value.title}</option>
                          {/each}
                        </select>
                      </label>
                    {/key}
                  {:else if item.type === "select-cross-reference-attribute"}
                    <Combobox.Root
                      selected={{
                        value: editor.getAttributes(item.mark)[item.name],
                        label: textForFirstNodeOfTipTapDocument(
                          sections[item.section].content.filter((text) => {
                            return (
                              text.attrs["id"] ===
                              editor?.getAttributes(item.mark)[item.name]
                            );
                          })[0].content,
                        ),
                      }}
                      items={sections[item.section].content.map((text) => {
                        return {
                          value: text.attrs["id"],
                          label: textForFirstNodeOfTipTapDocument(text.content),
                        };
                      })}
                      onSelectedChange={(value) => {
                        runAction(editor, item, value);
                      }}
                    >
                      <div class="relative">
                        <Combobox.Input
                          placeholder="Select the text to edit"
                          aria-label="Select the text to edit"
                          class="relative pr-6 z-10 bg-transparent"
                        />
                        <div class="absolute top-1/2 right-0 -translate-y-1/2">
                          <Icon
                            path={mdiChevronDown}
                            class="w-6 h-6 combobox-expand"
                          />
                          <Icon
                            path={mdiChevronUp}
                            class="w-6 h-6 combobox-collapse"
                          />
                        </div>
                      </div>
                      <Combobox.Content>
                        {#each sections[item.section].content as text}
                          <Combobox.Item
                            value={text.attrs["id"]}
                            label={textForFirstNodeOfTipTapDocument(
                              text.content,
                            )}
                            >{textForFirstNodeOfTipTapDocument(
                              text.content,
                            )}</Combobox.Item
                          >
                        {/each}
                      </Combobox.Content>
                    </Combobox.Root>
                  {/if}
                {/each}
              </div>
            {/if}
          </section>
        {/if}
      {/each}
    {/if}
  </div>
</div>
