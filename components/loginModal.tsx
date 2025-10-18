"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface LoginModalProps {
  isOpen: boolean
  onClose: () => void
  onLoginSuccess: (token: string) => void
}

export function LoginModal({ isOpen, onClose, onLoginSuccess }: LoginModalProps) {
  const [email, setEmail] = useState("user@example.com")
  const [password, setPassword] = useState("password123")
  const [error, setError] = useState("")

  const handleLogin = async () => {
    setError("")
    const apiUrl = process.env.NEXT_PUBLIC_API_URL

    try {
      const response = await fetch(`${apiUrl}/token`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({
          username: email,
          password: password,
        }),
      })

      if (!response.ok) {
        throw new Error("Login failed. Please check your credentials.")
      }

      const data = await response.json()
      onLoginSuccess(data.access_token)
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] bg-slate-800 border-slate-700 text-white">
        <DialogHeader>
          <DialogTitle>Sign In</DialogTitle>
          <DialogDescription>Enter your credentials to access your research dashboard.</DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="email" className="text-right">Email</Label>
            <Input id="email" value={email} onChange={(e) => setEmail(e.target.value)} className="col-span-3 bg-slate-700 border-slate-600" />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="password" className="text-right">Password</Label>
            <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} className="col-span-3 bg-slate-700 border-slate-600" />
          </div>
          {error && <p className="col-span-4 text-center text-red-400 text-sm">{error}</p>}
        </div>
        <Button onClick={handleLogin} className="w-full bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white">
          Sign In
        </Button>
      </DialogContent>
    </Dialog>
  )
}