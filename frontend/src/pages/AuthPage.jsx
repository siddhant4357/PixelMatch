import React from 'react'
import { SignIn, SignUp } from '@clerk/clerk-react'

const AuthPage = ({ type }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0] py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Decorative */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-gradient-to-br from-purple-300/30 to-pink-300/30 blur-3xl" />
      <div className="w-full max-w-md space-y-8 relative z-10">
        <div className="text-center mb-8">
          <h2 className="mt-6 text-3xl font-extrabold text-slate-900">
            {type === 'sign-in' ? 'Welcome Back' : 'Create an Account'}
          </h2>
          <p className="mt-2 text-sm text-slate-600">
            {type === 'sign-in' ? 'Sign in to access your events' : 'Join to find your photos instantly'}
          </p>
        </div>
        
        <div className="flex justify-center shadow-xl rounded-2xl bg-white p-2">
          {type === 'sign-in' ? (
            <SignIn 
              routing="path" 
              path="/sign-in" 
              signUpUrl="/sign-up" 
              forceRedirectUrl="/dashboard"
            />
          ) : (
            <SignUp 
              routing="path" 
              path="/sign-up" 
              signInUrl="/sign-in" 
              forceRedirectUrl="/dashboard"
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default AuthPage
