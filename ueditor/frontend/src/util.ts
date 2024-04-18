import { type QueryOptions } from "@tanstack/svelte-query";

export async function apiQueryHandler<ResponseModel>({ queryKey }: QueryOptions) {
    if (queryKey) {
        let response = await window.fetch("/api/" + queryKey.join("/"));
        if (response.ok) {
            return (await response.json()) as ResponseModel;
        }
    }
    throw new Error("Could not fetch data");
}
