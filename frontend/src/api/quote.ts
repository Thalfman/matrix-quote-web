import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "./client";
import { DropdownOptions, QuoteInput, QuotePrediction } from "./types";

export function useDropdowns() {
  return useQuery({
    queryKey: ["catalog", "dropdowns"],
    queryFn: async () => (await api.get<DropdownOptions>("/catalog/dropdowns")).data,
    staleTime: 5 * 60_000,
  });
}

export function useSingleQuote() {
  return useMutation({
    mutationFn: async (payload: QuoteInput) => {
      const { data } = await api.post<QuotePrediction>("/quote/single", payload);
      return data;
    },
  });
}
