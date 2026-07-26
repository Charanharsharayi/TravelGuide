import { useState, useEffect } from 'react'
import { useProductStore } from '../store/productStore'
import { useUserStore } from '../store/userStore'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { Loader2, ExternalLink, Search, ShoppingBag, Tag, AlertCircle } from 'lucide-react'

const CATEGORIES = [
    { value: '', label: 'All Categories' },
    { value: 'electronics', label: '🔌 Electronics' },
    { value: 'clothing', label: '👕 Clothing' },
    { value: 'home', label: '🏠 Home & Kitchen' },
    { value: 'books', label: '📚 Books' },
    { value: 'sports', label: '⚽ Sports & Outdoors' },
    { value: 'beauty', label: '💄 Beauty & Health' },
    { value: 'toys', label: '🧸 Toys & Games' },
    { value: 'automotive', label: '🚗 Automotive' },
]

const ProductFinder = () => {
    const { searchProducts, results, isSearching, error, clearResults } = useProductStore()
    const { preferences, fetchPreferences } = useUserStore()

    const [query, setQuery] = useState('')
    const [maxPrice, setMaxPrice] = useState(5000)
    const [category, setCategory] = useState('')
    const [numResults, setNumResults] = useState(5)

    useEffect(() => {
        fetchPreferences()
    }, [fetchPreferences])

    const handleSearch = () => {
        if (!query.trim()) return
        searchProducts({
            query: query.trim(),
            max_price: maxPrice,
            currency: preferences?.currency || 'INR',
            category,
            num_results: numResults,
        })
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') handleSearch()
    }

    const currencySymbol = preferences?.currency || 'INR'

    return (
        <div className="container mx-auto py-8 space-y-8">
            <div className="flex items-center gap-3">
                <ShoppingBag className="h-8 w-8 text-primary" />
                <h1 className="text-3xl font-bold">Product Finder</h1>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Search Form */}
                <Card className="lg:col-span-1 h-fit">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Search className="h-5 w-5" />
                            Search Products
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium">What are you looking for?</label>
                            <Input
                                id="product-query"
                                placeholder="e.g. wireless noise-cancelling headphones"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                                onKeyDown={handleKeyDown}
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Max Budget ({currencySymbol})</label>
                            <Input
                                id="product-budget"
                                type="number"
                                value={maxPrice}
                                onChange={(e) => setMaxPrice(Number(e.target.value))}
                                onKeyDown={handleKeyDown}
                                min={0}
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Number of Results: {numResults}</label>
                            <input
                                id="product-num-results"
                                type="range"
                                min={1}
                                max={10}
                                value={numResults}
                                onChange={(e) => setNumResults(Number(e.target.value))}
                                className="w-full accent-primary cursor-pointer"
                            />
                            <div className="flex justify-between text-xs text-muted-foreground">
                                <span>1</span>
                                <span>5</span>
                                <span>10</span>
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium">Category (optional)</label>
                            <select
                                id="product-category"
                                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                                value={category}
                                onChange={(e) => setCategory(e.target.value)}
                            >
                                {CATEGORIES.map((cat) => (
                                    <option key={cat.value} value={cat.value}>
                                        {cat.label}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <Button
                            id="product-search-btn"
                            className="w-full"
                            onClick={handleSearch}
                            disabled={isSearching || !query.trim()}
                        >
                            {isSearching ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Searching the web...
                                </>
                            ) : (
                                <>
                                    <Search className="mr-2 h-4 w-4" />
                                    Find Products
                                </>
                            )}
                        </Button>

                        {results.length > 0 && (
                            <Button
                                variant="outline"
                                className="w-full"
                                onClick={clearResults}
                            >
                                Clear Results
                            </Button>
                        )}
                    </CardContent>
                </Card>

                {/* Results */}
                <div className="lg:col-span-2 space-y-4">
                    {/* Loading */}
                    {isSearching && (
                        <Card className="flex items-center justify-center p-12">
                            <div className="text-center space-y-4">
                                <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                                <p className="text-muted-foreground">
                                    Searching across the web for the best deals...
                                </p>
                                <p className="text-xs text-muted-foreground">
                                    This may take 15–30 seconds
                                </p>
                            </div>
                        </Card>
                    )}

                    {/* Error */}
                    {error && !isSearching && (
                        <Card className="border-destructive/50">
                            <CardContent className="flex items-center gap-3 py-6">
                                <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0" />
                                <p className="text-sm text-destructive">{error}</p>
                            </CardContent>
                        </Card>
                    )}

                    {/* Results Grid */}
                    {results.length > 0 && !isSearching && (
                        <div className="space-y-4">
                            <p className="text-sm text-muted-foreground">
                                Found {results.length} product{results.length !== 1 ? 's' : ''} matching "{useProductStore.getState().lastQuery}"
                            </p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {results.map((product, idx) => (
                                    <Card
                                        key={idx}
                                        className="group hover:shadow-lg transition-all duration-200 hover:border-primary/30 flex flex-col"
                                    >
                                        <CardHeader className="pb-2">
                                            <div className="flex items-start justify-between gap-2">
                                                <CardTitle className="text-base leading-snug line-clamp-2">
                                                    {product.title}
                                                </CardTitle>
                                            </div>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className="inline-flex items-center gap-1 text-xs bg-secondary text-secondary-foreground px-2 py-0.5 rounded-full">
                                                    <Tag className="h-3 w-3" />
                                                    {product.source}
                                                </span>
                                            </div>
                                        </CardHeader>
                                        <CardContent className="flex-1 flex flex-col justify-between pt-0">
                                            <p className="text-sm text-muted-foreground line-clamp-3 mb-4">
                                                {product.snippet}
                                            </p>
                                            <div className="flex items-center justify-between mt-auto">
                                                <span className="text-xl font-bold text-primary">
                                                    {product.price}
                                                </span>
                                                <a
                                                    href={product.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="inline-flex items-center gap-1.5 text-sm font-medium bg-primary text-primary-foreground px-3 py-1.5 rounded-md hover:bg-primary/90 transition-colors"
                                                >
                                                    View Product
                                                    <ExternalLink className="h-3.5 w-3.5" />
                                                </a>
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Empty state (initial) */}
                    {!isSearching && results.length === 0 && !error && (
                        <Card className="flex items-center justify-center p-12">
                            <div className="text-center space-y-3">
                                <ShoppingBag className="h-12 w-12 mx-auto text-muted-foreground/40" />
                                <p className="text-muted-foreground">
                                    Describe a product and set your budget to find the best deals across the web.
                                </p>
                            </div>
                        </Card>
                    )}
                </div>
            </div>
        </div>
    )
}

export default ProductFinder
