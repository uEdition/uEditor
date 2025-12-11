<script lang="ts">
  import { Toolbar, Separator, type Selected } from "bits-ui";
  import { mdiPencil } from "@mdi/js";
  import { onMount } from "svelte";
  import { Editor, Node, Mark } from "@tiptap/core";
  import { Document } from "@tiptap/extension-document";
  import { Text } from "@tiptap/extension-text";

  import Icon from "../Icon.svelte";
  import { textForFirstNodeOfTipTapDocument } from "../../util";
  import { appState } from "../../state.svelte";

  type TeiTextEditorProps = {
    sectionName: string;
    sectionConfig: UEditorTEITextSection;
    sectionContent: TEITextSection;
    editorState: TEIEditorState;
    jumpToTextlistDocument: (sectionName: string, documentId: string) => void;
  };

  let {
    sectionName,
    sectionConfig,
    sectionContent,
    editorState,
    jumpToTextlistDocument,
  }: TeiTextEditorProps = $props();

  let editorElement: HTMLElement | null = $state(null);
  let editor: { editor: Editor | null } = $state({ editor: null });
  let updateDebounce = -1;

  onMount(() => {
    if (editorElement !== null) {
      const extensions: (Node | Mark)[] = [Document, Text];
      for (let blockConfig of appState.tei.blocks) {
        extensions.push(
          Node.create({
            name: blockConfig.name,
            group: "block",
            content: blockConfig.content ? blockConfig.content : "inline*",
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
      for (let markConfig of appState.tei.marks) {
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
      editor.editor = new Editor({
        element: editorElement,
        extensions: extensions,
        content: sectionContent.content,
        onTransaction: (params) => {
          editor = { editor: params.editor };
          if (params.transaction.docChanged) {
            window.clearTimeout(updateDebounce);
            updateDebounce = window.setTimeout(() => {
              sectionContent.content = params.editor.getJSON();
              editorState.notifyModified();
            }, 100);
          }
        },
      });
    }
  });

  function runAction(
    editor: Editor | null,
    action: UEditorTEIActions,
    evOrSelected: Event | Selected<any> | undefined,
  ) {
    if (editor) {
      if (action.type === "set-block") {
        editor.chain().focus().setNode(action.block).run();
      } else if (action.type === "toggle-wrap-block") {
        editor.chain().focus().toggleWrap(action.block).run();
      } else if (action.type === "set-block-attribute") {
        editor
          .chain()
          .focus()
          .updateAttributes(action.block, { [action.name]: action.value })
          .run();
      } else if (action.type === "toggle-mark") {
        editor.chain().focus().toggleMark(action.mark).run();
      } else if (
        action.type === "select-block-attribute" ||
        action.type === "input-block-attribute"
      ) {
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
            [action.name]: ((evOrSelected as Event).target as HTMLSelectElement)
              .value,
          })
          .run();
      } else if (
        action.type === "input-mark-attribute" ||
        action.type === "select-mark-attribute"
      ) {
        editor
          .chain()
          .focus()
          .extendMarkRange(action.mark)
          .updateAttributes(action.mark, {
            [action.name]: ((evOrSelected as Event).target as HTMLInputElement)
              .value,
          })
          .run();
      }
    }
  }

  function crossReferenceItems(
    item: UEditorTEISelectCrossReferenceMarkAttribute,
  ) {
    if (editorState.sections[item.section].type.type === "textlist") {
      return (
        editorState.sections[item.section] as TEITextlistSection
      ).content.map((text) => {
        return {
          value: text.attrs["id"],
          label: textForFirstNodeOfTipTapDocument(text.content),
        };
      });
    }
    return [];
  }

  function crossReferenceItemLabel(
    item: UEditorTEISelectCrossReferenceMarkAttribute,
  ) {
    if (editorState.sections[item.section].type.type === "textlist") {
      for (const text of (
        editorState.sections[item.section] as TEITextlistSection
      ).content) {
        if (
          text.attrs["id"] == editor.editor?.getAttributes(item.mark)[item.name]
        ) {
          return textForFirstNodeOfTipTapDocument(text.content);
        }
      }
    }
    return "";
  }
</script>

<div class="flex flex-row w-full h-full overflow-hidden">
  <div class="flex-1 overflow-auto px-3 py-2" bind:this={editorElement}></div>
  <div class="w-3/12 px-3 py-2 border-l border-gray-300 overflow-auto">
    {#if editorState.sections[sectionName] && sectionConfig.sidebar && editor.editor}
      {#each sectionConfig.sidebar as sidebarBlock}
        {#if !sidebarBlock.condition || editor.editor.isActive(sidebarBlock.condition.node)}
          <sectionConfig class="mb-4">
            <h2 class="font-bold mb-2">{sidebarBlock.title}</h2>
            {#if sidebarBlock.type === "toolbar"}
              <Toolbar.Root class="flex-wrap">
                {#each sidebarBlock.items as item}
                  {#if item.type === "set-block" || item.type === "toggle-wrap-block" || item.type === "set-block-attribute" || item.type === "toggle-mark"}
                    <Toolbar.Button
                      aria-pressed={((item.type === "set-block" ||
                        item.type === "toggle-wrap-block") &&
                        editor.editor.isActive(item.block)) ||
                        (item.type === "set-block-attribute" &&
                          editor.editor.isActive(item.block, {
                            [item.name]: item.value,
                          })) ||
                        (item.type === "toggle-mark" &&
                          editor.editor.isActive(item.mark))}
                      onclick={(ev) => {
                        runAction(editor.editor, item, ev);
                      }}
                      title={item.title}
                    >
                      {#if item.icon}
                        <Icon path={item.icon} />
                        <span class="sr-only">{item.title}</span>
                      {:else}
                        {item.title}
                      {/if}
                    </Toolbar.Button>
                  {:else if item.type === "separator"}
                    <Separator.Root class="mx-2 border-r border-gray-300" />
                  {/if}
                {/each}
              </Toolbar.Root>
            {:else if sidebarBlock.type === "form"}
              <div class="flex flex-row flex-wrap">
                {#each sidebarBlock.items as item}
                  {#if item.type === "select-block-attribute"}
                    {#key editor}
                      <label>
                        <span class="sr-only">{item.title}</span>
                        <select
                          value={editor.editor.getAttributes(item.block)[
                            item.name
                          ]}
                          onchange={(ev) => {
                            runAction(editor.editor, item, ev);
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
                  {:else if item.type === "input-block-attribute"}
                    <label>
                      <span data-form-field-label>{item.title}</span>
                      <input
                        type="text"
                        value={editor.editor.getAttributes(item.block)[
                          item.name
                        ]}
                        data-form-field-text
                        onchange={(ev) => {
                          runAction(editor.editor, item, ev);
                        }}
                      />
                    </label>
                  {:else if item.type === "select-cross-reference-attribute"}
                    <div class="flex flex-row flex-wrap">
                      <select
                        value={editor.editor.getAttributes(item.mark)[
                          item.name
                        ]}
                        onchange={(ev) => {
                          runAction(editor.editor, item, ev);
                        }}
                        data-combobox-input=""
                        class="block max-w-48"
                      >
                        {#each crossReferenceItems(item) as entry}
                          <option value={entry.value}>{entry.label}</option>
                        {/each}
                      </select>
                      <Toolbar.Root class="flex-wrap">
                        <Toolbar.Button
                          onclick={() => {
                            jumpToTextlistDocument(
                              item.section,
                              editor.editor?.getAttributes(item.mark)[
                                item.name
                              ],
                            );
                          }}
                          title="Edit the selected entry"
                        >
                          <Icon
                            path={mdiPencil}
                            label="Edit the selected entry"
                          />
                        </Toolbar.Button>
                      </Toolbar.Root>
                    </div>
                  {:else if item.type === "input-mark-attribute"}
                    <label>
                      <span data-form-field-label>{item.title}</span>
                      <input
                        type="text"
                        value={editor.editor.getAttributes(item.mark)[
                          item.name
                        ]}
                        data-form-field-text
                        onchange={(ev) => {
                          runAction(editor.editor, item, ev);
                        }}
                      />
                    </label>
                  {:else if item.type === "select-mark-attribute"}
                    {#key editor.editor}
                      <label>
                        <span class="sr-only">{item.title}</span>
                        <select
                          value={editor.editor.getAttributes(item.mark)[
                            item.name
                          ]}
                          onchange={(ev) => {
                            runAction(editor.editor, item, ev);
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
                  {/if}
                {/each}
              </div>
            {/if}
          </sectionConfig>
        {/if}
      {/each}
    {/if}
  </div>
</div>
