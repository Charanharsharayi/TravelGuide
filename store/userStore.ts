import { create } from 'zustand';
import api from '../api';

interface UserPreferences {
    travel_style: 'frugal' | 'balanced' | 'luxury';
    currency: string;
}

interface UserState {
    preferences: UserPreferences | null;
    isLoading: boolean;
    fetchPreferences: () => Promise<void>;
    updatePreferences: (prefs: UserPreferences) => Promise<void>;
}

export const useUserStore = create<UserState>((set) => ({
    preferences: null,
    isLoading: false,
    fetchPreferences: async () => {
        set({ isLoading: true });
        try {
            const response = await api.get('/user/settings');
            set({ preferences: response.data });
        } catch (error) {
            console.error('Failed to fetch preferences', error);
        } finally {
            set({ isLoading: false });
        }
    },
    updatePreferences: async (prefs) => {
        set({ isLoading: true });
        try {
            const response = await api.post('/user/settings', prefs);
            set({ preferences: prefs }); // Optimistic update or use response
        } catch (error) {
            console.error('Failed to update preferences', error);
        } finally {
            set({ isLoading: false });
        }
    },
}));
