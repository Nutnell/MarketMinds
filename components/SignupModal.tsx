"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { useToast } from "@/components/ui/use-toast" // Corrected path based on your structure

interface SignupModalProps {
  isOpen: boolean
  onClose: () => void
  onSignupSuccess: () => void
}

export function SignupModal({
  isOpen,
  onClose,
  onSignupSuccess,
}: SignupModalProps) {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const { toast } = useToast()

  const handleSignup = async () => {
    setError("")
    const apiUrl = process.env.NEXT_PUBLIC_API_URL

    try {
      const response = await fetch(`${apiUrl}/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || "Signup failed. Please try again.")
      }

      // On success, show a notification and trigger the success function
      toast({
        title: "✅ Account Created!",
        description: "You can now sign in with your new credentials.",
      })
      onSignupSuccess()
    } catch (err: any) {
      setError(err.message)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] bg-slate-800 border-slate-700 text-white">
        <DialogHeader>
          <DialogTitle>Create Your Account</DialogTitle>
          <DialogDescription>
            Get started with your AI Investment Co-Pilot.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="email-signup" className="text-right">
              Email
            </Label>
            <Input
              id="email-signup"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="col-span-3 bg-slate-700 border-slate-600"
              placeholder="you@example.com"
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="password-signup" className="text-right">
              Password
            </Label>
            <Input
              id="password-signup"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="col-span-3 bg-slate-700 border-slate-600"
            />
          </div>
          {error && (
            <p className="col-span-4 text-center text-red-400 text-sm">
              {error}
            </p>
          )}
        </div>
        <Button
          onClick={handleSignup}
          className="w-full bg-gradient-to-r from-emerald-500 to-blue-500 hover:from-emerald-600 hover:to-blue-600 text-white"
        >
          Create Account
        </Button>
      </DialogContent>
    </Dialog>
  )
}