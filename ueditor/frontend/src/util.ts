import { type QueryOptions } from "@tanstack/svelte-query";

/**
 * Fetches data from the API.
 *
 * @param queryOptions The query options to use for customising the query
 * @returns The returned data in the appropriate type
 */
export async function apiQueryHandler<ResponseModel>({ queryKey }: QueryOptions) {
  if (queryKey) {
    let response = await window.fetch("/api/" + queryKey.join("/"));
    if (response.ok) {
      return (await response.json()) as ResponseModel;
    }
  }
  throw new Error("Could not fetch data");
}

/**
 * Fetches raw file data.
 *
 * @param queryOptions The query options to use for customising the query
 * @returns The returned data as an ArrayBuffer
 */
export async function fileQueryHandler({ queryKey }: QueryOptions) {
  if (queryKey) {
    let response = await window.fetch("/api/" + queryKey.join("/"));
    if (response.ok) {
      return await response.arrayBuffer();
    }
  }
  throw new Error("Could not fetch data");
}

/**
 * Returns the text for a single TipTap node.
 *
 * @param node The node to get the text for
 * @returns The text for the node
 */
export function textForTipTapNode(node: TipTapNode): string {
  if (node.type === "text") {
    return (node as TipTapText).text;
  } else {
    let result: string[] = [];
    for (let child of (node as TipTapBlock).content) {
      result.push(textForTipTapNode(child));
    }
    return result.join("");
  }
}

/**
 * Returns the text of the first node of a TipTap document.
 *
 * @param doc  The document to get the text for
 * @returns The text of the first node in the document
 */
export function textForFirstNodeOfTipTapDocument(doc: TipTapDocument): string {
  if (doc.content.length > 0) {
    return textForTipTapNode(doc.content[0]);
  } else {
    return "<Empty Document>";
  }
}
