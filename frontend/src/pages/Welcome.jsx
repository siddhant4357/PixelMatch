import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Camera, Zap, Upload, ArrowRight, Shield, Brain, Sparkles, Search, Users, Star } from 'lucide-react'
import { SignedIn, SignedOut } from '@clerk/clerk-react'

const Welcome = () => {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 80)
    return () => clearTimeout(t)
  }, [])

  const steps = [
    {
      icon: <Upload className="w-7 h-7 text-purple-600" />,
      num: '01',
      title: 'Host uploads photos',
      desc: 'Create a private room and bulk-upload your event gallery in seconds.',
      color: 'from-purple-100 to-pink-100',
      border: 'border-purple-200/60',
    },
    {
      icon: <Camera className="w-7 h-7 text-pink-600" />,
      num: '02',
      title: 'Guests snap a selfie',
      desc: "Join with a room code, take one quick selfie — that's all it takes.",
      color: 'from-pink-100 to-orange-100',
      border: 'border-pink-200/60',
    },
    {
      icon: <Zap className="w-7 h-7 text-purple-600" />,
      num: '03',
      title: 'AI finds your photos',
      desc: 'Our Super-Ensemble AI scans every photo and delivers yours instantly.',
      color: 'from-purple-100 to-indigo-100',
      border: 'border-indigo-200/60',
    },
  ]

  const features = [
    {
      icon: <Brain className="w-6 h-6 text-purple-600" />,
      title: 'Super-Ensemble AI',
      desc: 'ArcFace + FaceNet512 dual-model architecture — 99.99% accuracy even in group shots.',
    },
    {
      icon: <Zap className="w-6 h-6 text-pink-600" />,
      title: 'Sub-second search',
      desc: 'FAISS vector database finds your face across thousands of photos in milliseconds.',
    },
    {
      icon: <Sparkles className="w-6 h-6 text-purple-600" />,
      title: 'Ask AI anything',
      desc: '"Show my photos from the dance floor" — natural language search powered by Llama 3.3.',
    },
    {
      icon: <Shield className="w-6 h-6 text-pink-600" />,
      title: 'Privacy-first',
      desc: 'Selfie data lives in-memory only. You only see photos you appear in. Auto-deleted after 7 days.',
    },
    {
      icon: <Search className="w-6 h-6 text-purple-600" />,
      title: 'Multi-face detection',
      desc: 'RetinaFace detects and indexes every person in every group shot automatically.',
    },
    {
      icon: <Users className="w-6 h-6 text-pink-600" />,
      title: 'Unlimited guests',
      desc: 'One event room, hundreds of guests — each person gets their own private gallery.',
    },
  ]

  return (
    <div
      className={`min-h-screen transition-opacity duration-700 ${visible ? 'opacity-100' : 'opacity-0'}`}
    >
      {/* ─── HERO ─── */}
      <section className="relative px-5 pt-16 pb-24 sm:pt-24 sm:pb-32 overflow-hidden">
        {/* decorative orbs — same palette as other pages */}
        <div className="pointer-events-none absolute top-0 right-0 w-[50vw] h-[50vw] max-w-xl max-h-xl bg-gradient-to-bl from-purple-300/30 to-pink-300/30 rounded-full blur-3xl" />
        <div className="pointer-events-none absolute bottom-0 left-0 w-[40vw] h-[40vw] max-w-lg max-h-lg bg-gradient-to-tr from-pink-200/25 to-orange-200/25 rounded-full blur-3xl" />

        <div className="relative z-10 mx-auto max-w-4xl text-center">
          {/* eyebrow badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/70 backdrop-blur-md border border-purple-200/60 shadow-md mb-8">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-purple-500 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-purple-600" />
            </span>
            <span className="text-sm font-semibold text-purple-700 tracking-wide">PixelMatch · AI Photo Search</span>
          </div>

          <h1 className="text-4xl sm:text-6xl md:text-7xl font-extrabold tracking-tight text-slate-900 leading-[1.1] mb-6">
            Find your moments.{' '}
            <span className="bg-gradient-to-r from-purple-600 via-pink-500 to-orange-400 bg-clip-text text-transparent">
              Instantly.
            </span>
          </h1>

          <p className="text-lg sm:text-xl text-slate-600 max-w-2xl mx-auto leading-relaxed mb-10">
            No more begging for photos after an event. Join a room, snap a selfie, and let our
            Super-Ensemble AI instantly find every single photo of you.
          </p>

          {/* CTA buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <SignedOut>
              <Link
                to="/sign-up"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold text-lg shadow-xl shadow-purple-500/30 hover:opacity-90 hover:-translate-y-0.5 transition-all duration-200"
              >
                Get Started Free <ArrowRight className="w-5 h-5" />
              </Link>
              <Link
                to="/sign-in"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/80 backdrop-blur-md text-slate-700 rounded-2xl font-bold text-lg border border-slate-200 shadow-md hover:bg-white hover:-translate-y-0.5 transition-all duration-200"
              >
                Sign In
              </Link>
            </SignedOut>
            <SignedIn>
              <Link
                to="/dashboard"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold text-lg shadow-xl shadow-purple-500/30 hover:opacity-90 hover:-translate-y-0.5 transition-all duration-200"
              >
                Go to Dashboard <ArrowRight className="w-5 h-5" />
              </Link>
            </SignedIn>
          </div>

          {/* social proof strip */}
          <div className="mt-12 flex flex-wrap items-center justify-center gap-x-8 gap-y-3 text-sm text-slate-500 font-medium">
            {['99.99% face-match accuracy', 'Privacy-first by design', 'Free to get started'].map((t) => (
              <span key={t} className="flex items-center gap-1.5">
                <Star className="w-4 h-4 text-amber-400 fill-amber-400" />
                {t}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* ─── HOW IT WORKS ─── */}
      <section className="px-5 py-20 sm:py-28">
        <div className="mx-auto max-w-5xl">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/70 backdrop-blur-md border border-purple-200/60 shadow-md mb-5">
              <Sparkles className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-semibold text-purple-700">How it works</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-3">
              Three steps to your photos
            </h2>
            <p className="text-slate-600 max-w-xl mx-auto">
              From upload to delivery in under a minute — no apps to install, no accounts to share.
            </p>
          </div>

          <div className="grid sm:grid-cols-3 gap-6">
            {steps.map((s) => (
              <div
                key={s.num}
                className={`relative bg-white/80 backdrop-blur-md rounded-[2rem] p-8 border ${s.border} shadow-lg shadow-purple-900/5 hover:-translate-y-1 transition-transform duration-300 overflow-hidden`}
              >
                {/* large step number watermark */}
                <div className="absolute -top-3 -right-3 text-[7rem] font-black text-slate-100 select-none leading-none">
                  {s.num}
                </div>
                <div className={`relative inline-flex p-4 rounded-2xl bg-gradient-to-br ${s.color} mb-5 shadow-inner`}>
                  {s.icon}
                </div>
                <h3 className="relative text-xl font-bold text-slate-900 mb-2">{s.title}</h3>
                <p className="relative text-slate-600 leading-relaxed">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── FEATURES GRID ─── */}
      <section className="px-5 py-20 sm:py-28">
        <div className="mx-auto max-w-5xl">
          <div className="text-center mb-14">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/70 backdrop-blur-md border border-purple-200/60 shadow-md mb-5">
              <Brain className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-semibold text-purple-700">Why PixelMatch</span>
            </div>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-3">
              Powered by advanced AI
            </h2>
            <p className="text-slate-600 max-w-xl mx-auto">
              Built with the same technology used by identity-verification platforms — now accessible to anyone.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {features.map((f) => (
              <div
                key={f.title}
                className="group bg-white/70 backdrop-blur-md rounded-2xl p-6 border border-white/80 shadow-md shadow-purple-900/5 hover:bg-white hover:-translate-y-1 hover:shadow-xl hover:shadow-purple-500/10 transition-all duration-300"
              >
                <div className="inline-flex items-center justify-center w-11 h-11 rounded-xl bg-gradient-to-br from-purple-100 to-pink-100 mb-4 shadow-inner group-hover:scale-110 transition-transform duration-300">
                  {f.icon}
                </div>
                <h3 className="font-bold text-slate-900 mb-1.5">{f.title}</h3>
                <p className="text-sm text-slate-600 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ─── FINAL CTA BANNER ─── */}
      <section className="px-5 pb-24">
        <div className="mx-auto max-w-3xl">
          <div className="relative bg-white/80 backdrop-blur-xl rounded-[2.5rem] p-10 sm:p-14 border border-white shadow-2xl shadow-purple-900/10 text-center overflow-hidden">
            {/* decorative blobs inside the card */}
            <div className="pointer-events-none absolute -top-20 -right-20 w-56 h-56 bg-gradient-to-bl from-purple-300/40 to-pink-300/40 rounded-full blur-3xl" />
            <div className="pointer-events-none absolute -bottom-20 -left-20 w-56 h-56 bg-gradient-to-tr from-pink-200/30 to-orange-200/30 rounded-full blur-3xl" />

            <div className="relative z-10">
              <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br from-purple-100 to-pink-100 mb-6 shadow-inner">
                <Camera className="w-10 h-10 text-purple-600" />
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight mb-4">
                Ready to find your photos?
              </h2>
              <p className="text-slate-600 max-w-md mx-auto mb-8 leading-relaxed">
                Create a free account and set up your first event room in under two minutes.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <SignedOut>
                  <Link
                    to="/sign-up"
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold shadow-xl shadow-purple-500/30 hover:opacity-90 hover:-translate-y-0.5 transition-all duration-200"
                  >
                    Create Free Account <ArrowRight className="w-5 h-5" />
                  </Link>
                  <Link
                    to="/sign-in"
                    className="w-full sm:w-auto inline-flex items-center justify-center px-8 py-4 bg-white text-slate-700 rounded-2xl font-bold border border-slate-200 shadow-md hover:bg-slate-50 hover:-translate-y-0.5 transition-all duration-200"
                  >
                    I already have an account
                  </Link>
                </SignedOut>
                <SignedIn>
                  <Link
                    to="/dashboard"
                    className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold shadow-xl shadow-purple-500/30 hover:opacity-90 hover:-translate-y-0.5 transition-all duration-200"
                  >
                    Open Dashboard <ArrowRight className="w-5 h-5" />
                  </Link>
                </SignedIn>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default Welcome
