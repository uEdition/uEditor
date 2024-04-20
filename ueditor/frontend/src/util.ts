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
