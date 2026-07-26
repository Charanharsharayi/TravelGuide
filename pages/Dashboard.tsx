import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Map, Plus, Loader2 } from 'lucide-react'
import { usePlanStore } from '../store/planStore'

const Dashboard = () => {
    const { savedPlans, isLoadingHistory, fetchPlans } = usePlanStore()

    useEffect(() => {
        fetchPlans()
    }, [fetchPlans])

    return (
        <div className="container mx-auto py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">Dashboard</h1>
                <Link to="/planner">
                    <Button>
                        <Plus className="mr-2 h-4 w-4" />
                        New Trip Plan
                    </Button>
                </Link>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <Card className="hover:bg-accent/5 transition-colors cursor-pointer border-dashed border-2 flex items-center justify-center p-8 h-64">
                    <Link to="/planner" className="flex flex-col items-center text-muted-foreground hover:text-primary">
                        <Map className="h-12 w-12 mb-2" />
                        <span className="font-medium">Plan a new trip</span>
                    </Link>
                </Card>

                {isLoadingHistory && (
                    <Card className="flex items-center justify-center h-64">
                        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                    </Card>
                )}

                {!isLoadingHistory && savedPlans.length === 0 && (
                    <Card>
                        <CardHeader>
                            <CardTitle>Recent Plans</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-muted-foreground text-sm">No recent plans found. Create your first trip!</p>
                        </CardContent>
                    </Card>
                )}

                {savedPlans.map((plan) => (
                    <Card key={plan.id} className="hover:bg-accent/5 transition-colors h-64 flex flex-col">
                        <CardHeader className="pb-2">
                            <CardTitle className="text-lg truncate">{plan.title}</CardTitle>
                            <p className="text-xs text-muted-foreground">
                                {new Date(plan.created_at).toLocaleDateString('en-IN', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric'
                                })}
                            </p>
                        </CardHeader>
                        <CardContent className="flex-1 flex flex-col justify-between">
                            <div>
                                <p className="text-sm text-muted-foreground truncate">
                                    {plan.content?.destination || 'Trip'}
                                </p>
                                <p className="text-sm mt-1">
                                    {plan.content?.itinerary?.length || 0} day(s)
                                </p>
                            </div>
                            <div className="mt-auto pt-4">
                                <span className="text-xl font-bold">
                                    {plan.content?.total_cost?.toLocaleString() || '—'}
                                </span>
                                <span className="text-sm text-muted-foreground ml-1">estimated</span>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
}

export default Dashboard
