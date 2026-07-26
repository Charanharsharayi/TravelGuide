import { create } from 'zustand';
import api from '../api';

interface ProductResult {
    title: string;
    price: string;
    url: string;
    source: string;
    snippet: string;
}

interface ProductSearchState {
    results: ProductResult[];
    isSearching: boolean;
    error: string | null;
    lastQuery: string;
    searchProducts: (request: {
        query: string;
        max_price: number;
        currency: string;
        category: string;
        num_results: number;
    }) => Promise<void>;
    clearResults: () => void;
}

export const useProductStore = create<ProductSearchState>((set) => ({
    results: [],
    isSearching: false,
    error: null,
    lastQuery: '',
    searchProducts: async (request) => {
        set({ isSearching: true, error: null, results: [], lastQuery: request.query });
        try {
            const response = await api.post('/product/search', request);
            set({
                results: response.data.results || [],
                error: response.data.results?.length === 0
                    ? 'No products found matching your criteria. Try adjusting your search or budget.'
                    : null,
            });
        } catch (error: any) {
            console.error('Product search failed', error);
            set({
                error: error?.response?.data?.detail || 'Search failed. Please try again.',
            });
        } finally {
            set({ isSearching: false });
        }
    },
    clearResults: () => set({ results: [], error: null, lastQuery: '' }),
}));
