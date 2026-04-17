import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "./client";
import {
  DropdownOptions,
  ExplainedQuoteResponse,
  QuoteInput,
  SavedQuote,
  SavedQuoteCreate,
  SavedQuoteList,
} from "./types";

export function useDropdowns() {
  return useQuery({
    queryKey: ["catalog", "dropdowns"],
    queryFn: async () => (await api.get<DropdownOptions>("/catalog/dropdowns")).data,
    staleTime: 5 * 60_000,
  });
}

export function useSingleQuote() {
  return useMutation<ExplainedQuoteResponse, unknown, QuoteInput>({
    mutationFn: async (input) =>
      (await api.post<ExplainedQuoteResponse>("/quote/single", input)).data,
  });
}

export function useSavedQuotes(
  params: { project?: string; industry?: string; search?: string } = {},
) {
  return useQuery<SavedQuoteList>({
    queryKey: ["savedQuotes", params],
    queryFn: async () =>
      (await api.get<SavedQuoteList>("/quotes", { params })).data,
  });
}

export function useSavedQuote(id: string | undefined) {
  return useQuery<SavedQuote>({
    queryKey: ["savedQuote", id],
    enabled: !!id,
    queryFn: async () => (await api.get<SavedQuote>(`/quotes/${id}`)).data,
  });
}

export function useSaveScenario() {
  const qc = useQueryClient();
  return useMutation<SavedQuote, unknown, SavedQuoteCreate>({
    mutationFn: async (body) =>
      (await api.post<SavedQuote>("/quotes", body)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["savedQuotes"] }),
  });
}

export function useDeleteScenario() {
  const qc = useQueryClient();
  return useMutation<void, unknown, string>({
    mutationFn: async (id) => {
      await api.delete(`/quotes/${id}`);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["savedQuotes"] }),
  });
}

export function useDuplicateScenario() {
  const qc = useQueryClient();
  return useMutation<SavedQuote, unknown, string>({
    mutationFn: async (id) =>
      (await api.post<SavedQuote>(`/quotes/${id}/duplicate`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["savedQuotes"] }),
  });
}
