import { create } from 'zustand';
import api from '../api';

interface DayPlan {
    day: number;
    date?: string;
    hotel?: string;
    activities: string[];
    estimated_cost: number;
}

interface TransportOption {
    mode: string;
    route: string;
    estimated_price: string;
    duration: string;
}

interface TripPlan {
    destination: string;
    total_cost: number;
    itinerary: DayPlan[];
    packing_list: string[];
    weather_info?: string;
    transport_options?: TransportOption[];
}

interface SavedPlan {
    id: string;
    user_id: string;
    title: string;
    type: string;
    content: TripPlan;
    created_at: string;
}

interface PlanRating {
    plan_id: string;
    hotel_rating: number;
    activities_rating: number;
    budget_rating: number;
    overall_rating: number;
    comment: string;
}

interface PlanState {
    currentPlan: TripPlan | null;
    currentPlanId: string | null;
    savedPlans: SavedPlan[];
    isGenerating: boolean;
    isLoadingHistory: boolean;
    hasRated: boolean;
    isSubmittingRating: boolean;
    generatePlan: (request: any) => Promise<void>;
    fetchPlans: () => Promise<void>;
    submitRating: (rating: Omit<PlanRating, 'plan_id'>) => Promise<void>;
}

export const usePlanStore = create<PlanState>((set, get) => ({
    currentPlan: null,
    currentPlanId: null,
    savedPlans: [],
    isGenerating: false,
    isLoadingHistory: false,
    hasRated: false,
    isSubmittingRating: false,
    generatePlan: async (request) => {
        set({ isGenerating: true, currentPlan: null, currentPlanId: null, hasRated: false });
        try {
            const response = await api.post('/plan/trip', request);
            set({
                currentPlan: response.data.plan,
                currentPlanId: response.data.plan_id || null,
            });
        } catch (error) {
            console.error('Failed to generate plan', error);
        } finally {
            set({ isGenerating: false });
        }
    },
    fetchPlans: async () => {
        set({ isLoadingHistory: true });
        try {
            const response = await api.get('/plan/history');
            set({ savedPlans: response.data });
        } catch (error) {
            console.error('Failed to fetch plan history', error);
        } finally {
            set({ isLoadingHistory: false });
        }
    },
    submitRating: async (rating) => {
        const planId = get().currentPlanId;
        if (!planId) {
            console.error('No plan ID to rate');
            return;
        }
        set({ isSubmittingRating: true });
        try {
            await api.post('/plan/rate', {
                plan_id: planId,
                ...rating,
            });
            set({ hasRated: true });
        } catch (error) {
            console.error('Failed to submit rating', error);
        } finally {
            set({ isSubmittingRating: false });
        }
    },
}));
