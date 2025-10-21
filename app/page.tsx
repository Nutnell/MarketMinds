"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Sparkles, TrendingUp, Plus, Trash2, Search, LogOut, LoaderCircle } from "lucide-react"
import { LoginModal } from "@/components/loginModal"
import { SignupModal } from "@/components/SignupModal"
import ReactMarkdown from "react-markdown"

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [authToken, setAuthToken] = useState<string | null>(null)
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false)
  const [isSignupModalOpen, setIsSignupModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [showChat, setShowChat] = useState(false)
  const [watchlist, setWatchlist] = useState<string[]>(["AAPL", "TSLA", "BTC"])
  const [newSymbol, setNewSymbol] = useState("")
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([])
  const [inputValue, setInputValue] = useState("")

  useEffect(() => {
    const token = localStorage.getItem("marketminds_token")
    if (token) {
      setAuthToken(token)
      setIsLoggedIn(true)
    }
  }, [])

  const handleLoginSuccess = (token: string) => {
    setAuthToken(token)
    setIsLoggedIn(true)
    localStorage.setItem("marketminds_token", token)
    setIsLoginModalOpen(false)
    setShowChat(true)
  }

  const handleSignupSuccess = () => {
    setIsSignupModalOpen(false)
    setIsLoginModalOpen(true)
  }

  const handleLogout = () => {
    setAuthToken(null)
    setIsLoggedIn(false)
    localStorage.removeItem("marketminds_token")
    setShowChat(false)
  }

  const addToWatchlist = () => {
    if (newSymbol.trim() && !watchlist.includes(newSymbol.toUpperCase())) {
      setWatchlist([...watchlist, newSymbol.toUpperCase()])
      setNewSymbol("")
    }
  }

  const removeFromWatchlist = (symbol: string) => {
    setWatchlist(watchlist.filter((s) => s !== symbol))
  }

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading || !authToken) return

    const userMessage = { role: "user", content: inputValue }
    const currentInput = inputValue
    setMessages((prev) => [...prev, userMessage])
    setInputValue("")
    setIsLoading(true)
    setMessages((prev) => [...prev, { role: "assistant", content: "Analyzing..." }])

    try {
      const requestBody = {
        input: currentInput, // ✅ simplified input
        config: {},
        kwargs: {}
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL
      const response = await fetch(`${apiUrl}/api/v1/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`
        },
        body: JSON.stringify(requestBody)
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`)
      }

      const data = await response.json()
      const content =
        typeof data.output === "object" && data.output !== null && "output" in data.output
          ? data.output.output
          : data.output
      const aiResponse = { role: "assistant", content: content || "Sorry, I couldn't generate a response." }

      setMessages((prev) => [...prev.slice(0, -1), aiResponse])
    } catch (error: any) {
      const errorMessage = {
        role: "assistant",
        content: `Sorry, something went wrong: ${error.message}`
      }
      setMessages((prev) => [...prev.slice(0, -1), errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  // --- LANDING PAGE ---
  if (!showChat) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white">
        <LoginModal
          isOpen={isLoginModalOpen}
          onClose={() => setIsLoginModalOpen(false)}
          onLoginSuccess={handleLoginSuccess}
        />
        <SignupModal
          isOpen={isSignupModalOpen}
          onClose={() => setIsSignupModalOpen(false)}
          onSignupSuccess={handleSignupSuccess}
        />
        <nav className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5" />
              </div>
              <span className="text-xl font-bold">MarketMinds AI</span>
            </div>
            <div className="flex items-center gap-4">
              {isLoggedIn ? (
                <>
                  <Button
                    onClick={() => setShowChat(true)}
                    variant="ghost"
                    className="text-slate-300 hover:text-white"
                  >
                    Dashboard
                  </Button>
                  <Button
                    onClick={handleLogout}
                    className="bg-red-500/20 text-red-400 hover:bg-red-500/30"
                  >
                    Sign Out
                  </Button>
                </>
              ) : (
                <>
                  <Button
                    onClick={() => setIsLoginModalOpen(true)}
                    variant="ghost"
                    className="text-slate-300 hover:text-white"
                  >
                    Sign In
                  </Button>
                  <Button
                    onClick={() => setIsSignupModalOpen(true)}
                    className="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600"
                  >
                    Get Started
                  </Button>
                </>
              )}
            </div>
          </div>
        </nav>
        <div className="max-w-7xl mx-auto px-6 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="space-y-4">
                <div className="inline-block px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full">
                  <span className="text-emerald-400 text-sm font-semibold">AI-Powered Research</span>
                </div>
                <h1 className="text-5xl lg:text-6xl font-bold text-white leading-tight">
                  Your AI Investment Research Co-Pilot
                </h1>
                <p className="text-xl text-slate-300 leading-relaxed">
                  Synthesize market data, financial news, and company reports in seconds. Make informed
                  investment decisions with AI-powered insights across stocks, crypto, and global markets.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4">
                <Button
                  onClick={() => (isLoggedIn ? setShowChat(true) : setIsSignupModalOpen(true))}
                  className="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white px-8 py-6 text-lg"
                >
                  Start Researching
                </Button>
              </div>
              <div className="grid grid-cols-2 gap-4 pt-8">
                <div className="space-y-2">
                  <div className="text-emerald-400 font-semibold">Multi-Agent Analysis</div>
                  <p className="text-sm text-slate-400">
                    Stock, crypto, and news agents collaborate for comprehensive insights
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="text-blue-400 font-semibold">Real-Time Data</div>
                  <p className="text-sm text-slate-400">
                    Access live market data and financial statements instantly
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="text-emerald-400 font-semibold">Watchlist Tracking</div>
                  <p className="text-sm text-slate-400">
                    Monitor your favorite assets and get intelligent alerts
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="text-blue-400 font-semibold">Sentiment Analysis</div>
                  <p className="text-sm text-slate-400">
                    Understand market sentiment from global news sources
                  </p>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 rounded-2xl blur-3xl"></div>
              <Card className="relative bg-slate-800/50 border-slate-700 p-8 backdrop-blur-sm">
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h3 className="text-white font-semibold">Market Overview</h3>
                    <TrendingUp className="w-5 h-5 text-emerald-400" />
                  </div>
                  <div className="space-y-4">
                    {[
                      { symbol: "AAPL", price: "$182.45", change: "+2.3%", color: "emerald" },
                      { symbol: "TSLA", price: "$242.80", change: "+5.1%", color: "blue" },
                      { symbol: "BTC", price: "$43,250", change: "+8.7%", color: "emerald" }
                    ].map((item) => (
                      <div
                        key={item.symbol}
                        className="flex items-center justify-between p-3 bg-slate-700/50 rounded-lg"
                      >
                        <div>
                          <div className="font-semibold text-white">{item.symbol}</div>
                          <div className="text-sm text-slate-400">{item.price}</div>
                        </div>
                        <div className={`text-sm font-semibold text-${item.color}-400`}>
                          {item.change}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // --- CHAT UI ---
  return (
    <div className="h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex text-white">
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onLoginSuccess={handleLoginSuccess}
      />
      <SignupModal
        isOpen={isSignupModalOpen}
        onClose={() => setIsSignupModalOpen(false)}
        onSignupSuccess={handleSignupSuccess}
      />
      <div className="w-80 border-r border-slate-700 bg-slate-900/50 backdrop-blur-sm flex flex-col">
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5" />
              </div>
              <span className="text-lg font-bold">MarketMinds</span>
            </div>
            <Button onClick={handleLogout} variant="ghost" size="sm" className="text-slate-400 hover:text-red-400">
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
          <Button onClick={() => setShowChat(false)} variant="outline" className="w-full border-slate-600 text-slate-300 hover:bg-slate-800">
            ← Back to Home
          </Button>
        </div>
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          <div>
            <h3 className="text-sm font-semibold text-slate-300 mb-3">My Watchlist</h3>
            <div className="space-y-2">
              {watchlist.map((symbol) => (
                <div key={symbol} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg hover:bg-slate-700/50 transition-colors">
                  <span className="font-semibold text-white">{symbol}</span>
                  <button
                    onClick={() => removeFromWatchlist(symbol)}
                    className="text-slate-400 hover:text-red-400 transition-colors"
                    title={`Remove ${symbol} from watchlist`}
                    aria-label={`Remove ${symbol} from watchlist`}
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
          <div className="space-y-3">
            <h3 className="text-sm font-semibold text-slate-300">Add Symbol</h3>
            <div className="flex gap-2">
              <Input placeholder="AAPL, BTC..." value={newSymbol} onChange={(e) => setNewSymbol(e.target.value)} onKeyPress={(e) => e.key === "Enter" && addToWatchlist()} className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500" />
              <Button onClick={addToWatchlist} size="sm" className="bg-emerald-500 hover:bg-emerald-600 text-white">
                <Plus className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>
      <div className="flex-1 flex flex-col">
        <div className="border-b border-slate-700 bg-slate-900/50 backdrop-blur-sm p-6">
          <h2 className="text-2xl font-bold text-white">Investment Research Assistant</h2>
          <p className="text-slate-400 text-sm mt-1">Ask me anything about stocks, crypto, or market trends</p>
        </div>
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-gradient-to-br from-emerald-400 to-blue-500 rounded-full flex items-center justify-center mx-auto">
                  <Search className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold text-white mb-2">Start Your Research</h3>
                  <p className="text-slate-400 max-w-md">Ask about any stock, cryptocurrency, or market trend. Our AI agents will analyze data and provide comprehensive insights.</p>
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div key={idx} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`whitespace-pre-wrap max-w-lg px-4 py-3 rounded-lg ${msg.role === "user" ? "bg-gradient-to-r from-emerald-500 to-blue-500 text-white" : "bg-slate-800 text-slate-100 border border-slate-700"}`}>
                  {msg.content === "Analyzing..." ? (
                    <div className="flex items-center gap-2">
                      <LoaderCircle className="w-4 h-4 animate-spin" />
                      <span>Analyzing...</span>
                    </div>
                  ) : (
                    <div className="prose prose-invert prose-p:text-slate-100 prose-strong:text-white prose-headings:text-white prose-ul:text-slate-300 overflow-x-auto">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
        <div className="border-t border-slate-700 bg-slate-900/50 backdrop-blur-sm p-6">
          <div className="flex gap-3">
            <Input
              disabled={isLoading}
              placeholder="Ask about AAPL, Bitcoin, market trends..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && sendMessage()}
              className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500"
            />
            <Button
              disabled={isLoading}
              onClick={sendMessage}
              className="bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 px-6"
            >
              {isLoading ? <LoaderCircle className="animate-spin" /> : "Send"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
