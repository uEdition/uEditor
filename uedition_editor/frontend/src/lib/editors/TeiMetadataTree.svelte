<script lang="ts">
    import { mdiChevronDown, mdiChevronRight } from "@mdi/js";
    import { melt, type TreeView } from "@melt-ui/svelte";
    import { getContext } from "svelte";

    import Icon from "../Icon.svelte";

    export let treeItems: TeiMetadataNode[];
    export let parent = "metadata-tree";

    const {
        elements: { item, group },
        helpers: { isExpanded, isSelected },
    } = getContext<TreeView>("tree");
</script>

{#each treeItems as { type, content }, i}
    {@const itemId = `${parent}-${i}`}
    {@const hasChildren = !!content?.length}

    <li role="none">
        <button
            class="flex items-center gap-1 p-1"
            use:melt={$item({
                id: itemId,
                hasChildren,
            })}
        >
            {#if hasChildren && $isExpanded(itemId)}
                <Icon path={mdiChevronDown} />
            {:else if hasChildren}
                <Icon path={mdiChevronRight} />
            {:else}
                <Icon />
            {/if}

            <span class="select-none">{type}</span>
        </button>

        {#if content}
            <ol use:melt={$group({ id: itemId })}>
                <svelte:self treeItems={content} parent={itemId} />
            </ol>
        {/if}
    </li>
{/each}
