import { SignedIn, UserButton, SignedOut, RedirectToSignIn } from "@clerk/clerk-react"
import { LayoutDashboard, Map, Settings, Menu, ShoppingBag } from "lucide-react"
import { Link, Outlet } from "react-router-dom"
import { Button } from "../ui/button"

const Layout = () => {
    return (
        <div className="min-h-screen bg-background flex flex-col md:flex-row">
            {/* Sidebar */}
            <aside className="w-full md:w-64 bg-card border-r p-4 hidden md:flex flex-col">
                <div className="flex items-center gap-2 mb-8 px-2">
                    <span className="text-xl font-bold">LifeLogistics</span>
                </div>

                <nav className="flex-1 space-y-2">
                    <Link to="/">
                        <Button variant="ghost" className="w-full justify-start">
                            <LayoutDashboard className="mr-2 h-4 w-4" />
                            Dashboard
                        </Button>
                    </Link>
                    <Link to="/planner">
                        <Button variant="ghost" className="w-full justify-start">
                            <Map className="mr-2 h-4 w-4" />
                            Planner
                        </Button>
                    </Link>
                    <Link to="/products">
                        <Button variant="ghost" className="w-full justify-start">
                            <ShoppingBag className="mr-2 h-4 w-4" />
                            Product Finder
                        </Button>
                    </Link>
                    <Link to="/settings">
                        <Button variant="ghost" className="w-full justify-start">
                            <Settings className="mr-2 h-4 w-4" />
                            Settings
                        </Button>
                    </Link>
                </nav>

                <div className="mt-auto pt-4 border-t">
                    <SignedIn>
                        <div className="flex items-center gap-2 px-2">
                            <UserButton />
                            <span className="text-sm font-medium">My Account</span>
                        </div>
                    </SignedIn>
                </div>
            </aside>

            {/* Mobile Header */}
            <header className="md:hidden border-b p-4 flex items-center justify-between bg-card">
                <span className="text-lg font-bold">LifeLogistics</span>
                <SignedIn>
                    <UserButton />
                </SignedIn>
            </header>

            {/* Main Content */}
            <main className="flex-1 p-4 md:p-8 overflow-y-auto">
                <SignedOut>
                    <RedirectToSignIn />
                </SignedOut>
                <SignedIn>
                    <Outlet />
                </SignedIn>
            </main>
        </div>
    )
}

export default Layout
