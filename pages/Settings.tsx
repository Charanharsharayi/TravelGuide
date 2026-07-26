import { useEffect, useState } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { useUserStore } from '../store/userStore'

const Settings = () => {
    const { preferences, fetchPreferences, updatePreferences, isLoading } = useUserStore()
    const [travelStyle, setTravelStyle] = useState('balanced')
    const [currency, setCurrency] = useState('INR')

    useEffect(() => {
        fetchPreferences()
    }, [fetchPreferences])

    useEffect(() => {
        if (preferences) {
            setTravelStyle(preferences.travel_style)
            setCurrency(preferences.currency)
        }
    }, [preferences])

    const handleSave = () => {
        updatePreferences({
            travel_style: travelStyle as 'frugal' | 'balanced' | 'luxury',
            currency
        })
    }

    return (
        <div className="container mx-auto max-w-2xl py-8">
            <h1 className="text-3xl font-bold mb-8">Settings</h1>

            <Card>
                <CardHeader>
                    <CardTitle>Travel Preferences</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <label className="text-sm font-medium">Travel Style</label>
                        <select
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            value={travelStyle}
                            onChange={(e) => setTravelStyle(e.target.value)}
                        >
                            <option value="frugal">Frugal</option>
                            <option value="balanced">Balanced</option>
                            <option value="luxury">Luxury</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium">Currency</label>
                        <select
                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                            value={currency}
                            onChange={(e) => setCurrency(e.target.value)}
                        >
                            <option value="INR">INR (₹)</option>
                            <option value="USD">USD ($)</option>
                            <option value="EUR">EUR (€)</option>
                        </select>
                    </div>

                    <Button onClick={handleSave} disabled={isLoading} className="mt-4">
                        {isLoading ? 'Saving...' : 'Save Preferences'}
                    </Button>
                </CardContent>
            </Card>
        </div>
    )
}

export default Settings
