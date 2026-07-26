import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import TripPlanner from './pages/TripPlanner'
import ProductFinder from './pages/ProductFinder'
import Settings from './pages/Settings'

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    {/* Protected Routes */}
                    <Route index element={
                        <SignedIn>
                            <Dashboard />
                        </SignedIn>
                    } />
                    <Route path="planner" element={
                        <SignedIn>
                            <TripPlanner />
                        </SignedIn>
                    } />
                    <Route path="products" element={
                        <SignedIn>
                            <ProductFinder />
                        </SignedIn>
                    } />
                    <Route path="settings" element={
                        <SignedIn>
                            <Settings />
                        </SignedIn>
                    } />

                    {/* Public or Redirect */}
                    <Route path="*" element={
                        <SignedOut>
                            <RedirectToSignIn />
                        </SignedOut>
                    } />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
