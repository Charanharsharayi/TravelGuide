import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { ClerkProvider, useAuth } from '@clerk/clerk-react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { setupAxiosInterceptors } from './api'

// Import your publishable key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
    throw new Error("Missing Publishable Key")
}

const queryClient = new QueryClient()

// Wrapper to provide auth token to Axios
const AuthWrapper = ({ children }: { children: React.ReactNode }) => {
    const { getToken } = useAuth()

    React.useEffect(() => {
        setupAxiosInterceptors(getToken)
    }, [getToken])

    return <>{children}</>
}

ReactDOM.createRoot(document.getElementById('root')!).render(
    <React.StrictMode>
        <ClerkProvider publishableKey={PUBLISHABLE_KEY}>
            <QueryClientProvider client={queryClient}>
                <AuthWrapper>
                    <App />
                </AuthWrapper>
            </QueryClientProvider>
        </ClerkProvider>
    </React.StrictMode>,
)
