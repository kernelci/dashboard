import { useQuery, UseQueryResult} from "@tanstack/react-query";

import type { Tree } from "../types/tree/Tree";

const fetchTreeCheckoutData = async(): Promise<Tree[]> => {
    const res = await fetch('/api/tree');
    if (!res.ok) {
        throw new Error('Request to /api/tree response was not ok');
    }
    return res.json();
}

export const useTreeTable = (): UseQueryResult => {
    return useQuery({ queryKey: ['treeData'], queryFn: fetchTreeCheckoutData });
}
