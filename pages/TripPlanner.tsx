import { useState, useEffect } from 'react'
import { usePlanStore } from '../store/planStore'
import { useUserStore } from '../store/userStore'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Loader2, Star, MapPin, Calendar, CloudSun, Train } from 'lucide-react'

// Star rating component
const StarRating = ({ label, value, onChange }: { label: string; value: number; onChange: (v: number) => void }) => (
    <div className="flex items-center justify-between">
        <span className="text-sm font-medium w-40">{label}</span>
        <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((star) => (
                <button
                    key={star}
                    type="button"
                    onClick={() => onChange(star)}
                    className="focus:outline-none transition-colors"
                >
                    <Star
                        className={`h-5 w-5 ${star <= value
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-muted-foreground/30'
                            }`}
                    />
                </button>
            ))}
        </div>
    </div>
)

const TripPlanner = () => {
    const { generatePlan, isGenerating, currentPlan, currentPlanId, hasRated, isSubmittingRating, submitRating } = usePlanStore()
    const { preferences, fetchPreferences } = useUserStore()

    const [query, setQuery] = useState('')
    const [budget, setBudget] = useState(1000)
    const [origin, setOrigin] = useState('')
    const [destination, setDestination] = useState('')
    const [tripDate, setTripDate] = useState('')
    const [useCurrentLocation, setUseCurrentLocation] = useState(true)

    // Rating state
    const [hotelRating, setHotelRating] = useState(0)
    const [activitiesRating, setActivitiesRating] = useState(0)
    const [budgetRating, setBudgetRating] = useState(0)
    const [overallRating, setOverallRating] = useState(0)
    const [comment, setComment] = useState('')

    useEffect(() => {
        fetchPreferences()
    }, [fetchPreferences])

    // Reset ratings when a new plan is generated
    useEffect(() => {
        if (currentPlan) {
            setHotelRating(0)
            setActivitiesRating(0)
            setBudgetRating(0)
            setOverallRating(0)
            setComment('')
        }
    }, [currentPlan])

    const handlePlan = () => {
        if (!query && !destination) return

        generatePlan({
            query: query || `Trip to ${destination}`,
            budget_limit: budget,
            preferences: preferences || { travel_style: 'balanced', currency: 'INR' },
            origin: useCurrentLocation ? 'Current Location' : origin,
            destination: destination,
            trip_date: tripDate,
        })
    }

    const handleSubmitRating = () => {
        if (hotelRating === 0 || activitiesRating === 0 || budgetRating === 0 || overallRating === 0) return
        submitRating({
            hotel_rating: hotelRating,
            activities_rating: activitiesRating,
            budget_rating: budgetRating,
            overall_rating: overallRating,
            comment,
        })
    }

    const canSubmitRating = hotelRating > 0 && activitiesRating > 0 && budgetRating > 0 && overallRating > 0

    const formatDate = (dateStr: string) => {
        try {
            return new Date(dateStr).toLocaleDateString('en-US', {
                weekday: 'short',
                year: 'numeric',
                month: 'short',
                day: 'numeric',
            })
        } catch {
            return dateStr
        }
    }

    const getTransportIcon = (mode: string) => {
        const m = mode.toLowerCase()
        if (m.includes('flight') || m.includes('air') || m.includes('plane')) return '✈️'
        if (m.includes('train') || m.includes('rail')) return '🚆'
        if (m.includes('bus') || m.includes('coach')) return '🚌'
        if (m.includes('car') || m.includes('drive') || m.includes('taxi')) return '🚗'
        return '🚆'
    }

    return (
        <div className="container mx-auto py-8 space-y-8">
            <h1 className="text-3xl font-bold">Trip Planner</h1>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Input Form */}
                <Card className="lg:col-span-1 h-fit">
                    <CardHeader>
                        <CardTitle>Plan Your Trip</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        {/* Origin */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium flex items-center gap-1">
                                <MapPin className="h-3.5 w-3.5" /> From
                            </label>
                            <div className="flex items-center gap-2 mb-1">
                                <input
                                    type="checkbox"
                                    id="currentLocation"
                                    checked={useCurrentLocation}
                                    onChange={(e) => setUseCurrentLocation(e.target.checked)}
                                    className="rounded"
                                />
                                <label htmlFor="currentLocation" className="text-xs text-muted-foreground cursor-pointer">
                                    📍 Use Current Location
                                </label>
                            </div>
                            {!useCurrentLocation && (
                                <Input
                                    placeholder="e.g. Delhi, Mumbai"
                                    value={origin}
                                    onChange={(e) => setOrigin(e.target.value)}
                                />
                            )}
                        </div>

                        {/* Destination */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium flex items-center gap-1">
                                <MapPin className="h-3.5 w-3.5" /> To (Destination)
                            </label>
                            <Input
                                placeholder="e.g. Jaipur, Goa, Kyoto"
                                value={destination}
                                onChange={(e) => setDestination(e.target.value)}
                            />
                        </div>

                        {/* Trip Date */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium flex items-center gap-1">
                                <Calendar className="h-3.5 w-3.5" /> Trip Date
                            </label>
                            <Input
                                type="date"
                                value={tripDate}
                                onChange={(e) => setTripDate(e.target.value)}
                            />
                        </div>

                        {/* Trip Details */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium">Trip Details</label>
                            <Input
                                placeholder="e.g. 5 days, cherry blossom, adventure"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Budget Limit ({preferences?.currency || 'INR'})</label>
                            <Input
                                type="number"
                                value={budget}
                                onChange={(e) => setBudget(Number(e.target.value))}
                            />
                        </div>

                        <Button
                            className="w-full"
                            onClick={handlePlan}
                            disabled={isGenerating || (!query && !destination)}
                        >
                            {isGenerating ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Planning...
                                </>
                            ) : (
                                'Generate Plan'
                            )}
                        </Button>
                    </CardContent>
                </Card>

                {/* Results Display */}
                <div className="lg:col-span-2 space-y-4">
                    {isGenerating && (
                        <Card className="flex items-center justify-center p-12">
                            <div className="text-center space-y-4">
                                <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                                <p className="text-muted-foreground">Checking weather, finding transport & consulting travel agents...</p>
                            </div>
                        </Card>
                    )}

                    {currentPlan && !isGenerating && (
                        <div className="space-y-6">
                            <Card>
                                <CardHeader>
                                    <CardTitle>Trip to {currentPlan.destination}</CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="text-2xl font-bold mb-4">
                                        Total Cost: {currentPlan.total_cost} {preferences?.currency || 'INR'}
                                    </div>

                                    {/* Weather Info Banner */}
                                    {currentPlan.weather_info && (
                                        <div className="flex items-center gap-2 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-3 mb-4">
                                            <CloudSun className="h-5 w-5 text-blue-500 flex-shrink-0" />
                                            <div>
                                                <span className="text-sm font-medium text-blue-700 dark:text-blue-300">Weather: </span>
                                                <span className="text-sm text-blue-600 dark:text-blue-400">{currentPlan.weather_info}</span>
                                            </div>
                                        </div>
                                    )}

                                    {/* Transport Options */}
                                    {currentPlan.transport_options && currentPlan.transport_options.length > 0 && (
                                        <div className="mb-6">
                                            <h3 className="font-semibold mb-2 flex items-center gap-1">
                                                <Train className="h-4 w-4" /> Transport Options
                                            </h3>
                                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                                {currentPlan.transport_options.map((opt: any, idx: number) => (
                                                    <div key={idx} className="border rounded-lg p-3 bg-muted/30">
                                                        <div className="flex items-center gap-2 mb-1">
                                                            <span className="text-lg">{getTransportIcon(opt.mode)}</span>
                                                            <span className="font-medium text-sm capitalize">{opt.mode}</span>
                                                        </div>
                                                        <div className="text-xs text-muted-foreground">{opt.route}</div>
                                                        <div className="flex justify-between mt-2">
                                                            <span className="text-sm font-semibold text-primary">{opt.estimated_price}</span>
                                                            {opt.duration && (
                                                                <span className="text-xs text-muted-foreground">{opt.duration}</span>
                                                            )}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                    <h3 className="font-semibold mb-2">Itinerary</h3>
                                    <div className="space-y-4">
                                        {currentPlan.itinerary.map((day: any) => (
                                            <div key={day.day} className="border-l-2 border-primary pl-4 py-2">
                                                <h4 className="font-medium text-lg">
                                                    Day {day.day}
                                                    {day.date && (
                                                        <span className="text-sm font-normal text-muted-foreground ml-2">
                                                            — {formatDate(day.date)}
                                                        </span>
                                                    )}
                                                </h4>
                                                {day.hotel && (
                                                    <div className="mt-1 text-sm font-medium text-primary">
                                                        🏨 {day.hotel}
                                                    </div>
                                                )}
                                                <ul className="list-disc list-inside text-sm text-muted-foreground mt-1">
                                                    {day.activities.map((act: string, idx: number) => (
                                                        <li key={idx}>{act}</li>
                                                    ))}
                                                </ul>
                                                <div className="mt-2 text-sm font-medium">
                                                    Est. Cost: {day.estimated_cost} {preferences?.currency || 'INR'}
                                                </div>
                                            </div>
                                        ))}
                                    </div>

                                    <div className="mt-6">
                                        <h3 className="font-semibold mb-2">Packing List</h3>
                                        <div className="flex flex-wrap gap-2">
                                            {currentPlan.packing_list.map((item: string, idx: number) => (
                                                <span key={idx} className="bg-secondary text-secondary-foreground px-2 py-1 rounded-md text-xs">
                                                    {item}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </CardContent>
                            </Card>

                            {/* Rating Card */}
                            {currentPlanId && (
                                <Card>
                                    <CardHeader>
                                        <CardTitle className="text-lg">
                                            {hasRated ? '✅ Thanks for your feedback!' : '⭐ Rate This Plan'}
                                        </CardTitle>
                                    </CardHeader>
                                    {!hasRated && (
                                        <CardContent className="space-y-4">
                                            <p className="text-sm text-muted-foreground">
                                                Your ratings help us generate better plans next time.
                                            </p>
                                            <div className="space-y-3">
                                                <StarRating label="🏨 Hotels" value={hotelRating} onChange={setHotelRating} />
                                                <StarRating label="🎯 Activities" value={activitiesRating} onChange={setActivitiesRating} />
                                                <StarRating label="💰 Budget Accuracy" value={budgetRating} onChange={setBudgetRating} />
                                                <StarRating label="⭐ Overall" value={overallRating} onChange={setOverallRating} />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-sm font-medium">Comments (optional)</label>
                                                <textarea
                                                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none"
                                                    rows={2}
                                                    placeholder="e.g. I prefer boutique hotels, more cultural activities..."
                                                    value={comment}
                                                    onChange={(e) => setComment(e.target.value)}
                                                />
                                            </div>
                                            <Button
                                                className="w-full"
                                                onClick={handleSubmitRating}
                                                disabled={!canSubmitRating || isSubmittingRating}
                                            >
                                                {isSubmittingRating ? (
                                                    <>
                                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                        Submitting...
                                                    </>
                                                ) : (
                                                    'Submit Rating'
                                                )}
                                            </Button>
                                        </CardContent>
                                    )}
                                </Card>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default TripPlanner
