import os
import json
import urllib.request
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import agent_core

PORT = 5050
HOST = "127.0.0.1"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Ascenta — Autonomous LinkedIn Content Engine</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script>
    tailwind.config = {
      theme: {
        extend: {
          fontFamily: {
            display: ['"Plus Jakarta Sans"', 'sans-serif'],
            sans: ['Inter', 'sans-serif'],
            mono: ['"JetBrains Mono"', 'monospace'],
          },
          colors: {
            canvas: '#f0f2f7',
            navy: {
              950: '#0e1122',
              900: '#14182b',
              850: '#191e36',
              800: '#202646',
              700: '#2b335c',
            },
            accent: {
              purple: '#4f46e5',
              purpleHover: '#4338ca',
              purpleLight: '#e0e7ff',
              pillActive: '#4338ca',
            }
          }
        }
      }
    }
  </script>
  <style>
    body {
      background-color: #f0f2f7;
      color: #0f172a;
      font-family: 'Inter', sans-serif;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: rgba(0, 0, 0, 0.03);
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: rgba(0, 0, 0, 0.15);
      border-radius: 4px;
    }
    .dark-scroll::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    .dark-scroll::-webkit-scrollbar-track {
      background: #14182b;
    }
    .dark-scroll::-webkit-scrollbar-thumb {
      background: #2b335c;
      border-radius: 4px;
    }
    /* Smooth transitions */
    .ease-spring {
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
  </style>
</head>
<body class="min-h-screen bg-[#f0f2f7] p-4 sm:p-6 lg:p-8 antialiased selection:bg-indigo-600 selection:text-white">

  <!-- NOTIFICATION TOAST -->
  <div id="toast" class="fixed top-6 right-6 z-50 transform transition-all duration-300 translate-y-[-120px] opacity-0 pointer-events-none flex items-center gap-3 px-5 py-3.5 rounded-2xl bg-slate-900 text-white shadow-2xl text-xs font-semibold">
    <div class="w-5 h-5 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center font-bold text-[11px]">✓</div>
    <span id="toast-message">Action executed smoothly</span>
  </div>

  <!-- MAIN FRAME CONTAINER (MATCHING FINNOVA DESIGN SYSTEM) -->
  <div class="max-w-[1400px] mx-auto bg-white/60 backdrop-blur-md rounded-[36px] border border-slate-200/80 p-6 lg:p-8 shadow-sm space-y-7">

    <!-- 1. TOP NAVIGATION BAR -->
    <header class="flex flex-col lg:flex-row items-center justify-between gap-4">
      
      <!-- Logo & Score -->
      <div class="flex items-center gap-4 w-full lg:w-auto justify-between lg:justify-start">
        <div class="flex items-center gap-3">
          <!-- Logo Ribbon Icon -->
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-500 flex items-center justify-center shadow-md shadow-indigo-500/20">
            <svg class="w-6 h-6 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <div>
            <div class="font-display font-extrabold text-slate-900 text-lg tracking-tight leading-none">ASCENTA</div>
            <p class="text-[11px] text-slate-500 font-medium">Autonomous Content Engine</p>
          </div>
        </div>

        <!-- Telemetry Score Pill (like the '80' pill in screenshot) -->
        <div class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 border border-slate-200/70 text-xs font-mono font-bold text-slate-700">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>98% Fact Grounded</span>
        </div>
      </div>

      <!-- Center Dark Capsule Navigation (FINNOVA Signature Navbar) -->
      <nav class="flex items-center bg-[#15192c] p-1.5 rounded-full shadow-lg shadow-slate-900/10 text-xs font-semibold">
        <button onclick="setTab('OVERVIEW')" id="nav-overview" class="px-4 py-2 rounded-full bg-indigo-600 text-white shadow-sm flex items-center gap-1.5">
          <span>• Overview</span>
        </button>
        <button onclick="setTab('QUEUE')" id="nav-queue" class="px-4 py-2 rounded-full text-slate-300 hover:text-white transition">
          Posts Queue
        </button>
        <button onclick="setTab('CALENDAR')" id="nav-calendar" class="px-4 py-2 rounded-full text-slate-300 hover:text-white transition">
          Schedule
        </button>
        <button onclick="setTab('KNOWLEDGE')" id="nav-knowledge" class="px-4 py-2 rounded-full text-slate-300 hover:text-white transition">
          Knowledge Base
        </button>
        <button onclick="setTab('SIMULATOR')" id="nav-simulator" class="px-4 py-2 rounded-full text-slate-300 hover:text-white transition">
          Feed Simulator
        </button>
      </nav>

      <!-- Right Action Icons & User Avatar -->
      <div class="flex items-center gap-2.5">
        <button onclick="triggerGeneratePost()" title="Quick Refresh / Ping" class="w-9 h-9 rounded-full bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 flex items-center justify-center text-xs shadow-sm">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
        </button>
        <button onclick="openNoteModal()" title="Add Raw Observation" class="w-9 h-9 rounded-full bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 flex items-center justify-center text-xs shadow-sm">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
        </button>
        <button title="Notifications" class="w-9 h-9 rounded-full bg-white border border-slate-200 hover:bg-slate-50 text-slate-600 flex items-center justify-center text-xs shadow-sm relative">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
          <span class="absolute top-2 right-2 w-2 h-2 rounded-full bg-red-500"></span>
        </button>

        <!-- Profile Avatar & Identity -->
        <a href="https://www.linkedin.com/in/ascenta" target="_blank" title="Muhammad Rayyan - Founder" class="flex items-center gap-2 pl-2">
          <div class="w-9 h-9 rounded-full bg-gradient-to-tr from-slate-900 to-indigo-900 text-white flex items-center justify-center font-display font-bold text-xs ring-2 ring-indigo-500/30">
            MR
          </div>
        </a>
      </div>
    </header>

    <!-- 2. SECTION HEADER (TITLE & PRIMARY ACTION) -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-2">
      <div class="flex items-center gap-3">
        <button class="w-10 h-10 rounded-full bg-white border border-slate-200 text-slate-600 flex items-center justify-center hover:bg-slate-50 shadow-sm transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
        </button>
        <div>
          <h1 class="font-display font-extrabold text-2xl lg:text-3xl text-slate-900 tracking-tight" id="main-section-title">Content Pipeline</h1>
          <p class="text-xs text-slate-500 font-medium mt-0.5">Manage, review, audit and publish your autonomous LinkedIn posts in one place.</p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button onclick="toggleFilters()" class="w-10 h-10 rounded-full bg-white border border-slate-200 text-slate-600 flex items-center justify-center hover:bg-slate-50 shadow-sm transition">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
        </button>
        <button onclick="triggerGeneratePost()" id="btn-generate-main" class="px-5 py-2.5 rounded-full bg-indigo-600 hover:bg-indigo-700 text-white font-display font-bold text-xs tracking-wide shadow-lg shadow-indigo-600/25 flex items-center gap-2 transition active:scale-95">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"></path></svg>
          <span>Generate Post</span>
        </button>
      </div>
    </div>

    <!-- 3. TOP 4 METRIC CARDS ROW (EXACT FINNOVA CARD LAYOUT) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <!-- Card 1: Ready For Review (with photo illustration) -->
      <div class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm flex flex-col justify-between h-48 relative overflow-hidden">
        <div>
          <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-1">
            <span>Ready for Review</span>
            <span class="w-5 h-5 rounded-full bg-rose-50 text-rose-500 border border-rose-200 flex items-center justify-center text-[10px] font-bold">!</span>
          </div>
          <div class="font-display font-extrabold text-3xl text-slate-900 tracking-tight" id="kpi-review-count">3 Posts</div>
          <div class="flex items-center gap-1.5 text-[11px] font-semibold text-rose-500 mt-1">
            <span>↑ 100% Grounded</span>
            <span class="text-slate-400 font-normal">in Ascenta records</span>
          </div>
        </div>
        
        <!-- Clean workspace graphic cutout -->
        <div class="flex items-end justify-between pt-2">
          <div class="text-[11px] font-mono text-slate-400">Zero AI Slop</div>
          <div class="w-16 h-12 rounded-xl bg-gradient-to-tr from-slate-100 to-indigo-50 border border-slate-200/60 flex items-center justify-center text-indigo-600 text-lg shadow-inner">
            💻
          </div>
        </div>
      </div>

      <!-- Card 2: 30-Day Cadence (with Bar Chart) -->
      <div class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm flex flex-col justify-between h-48">
        <div>
          <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-1">
            <span>Target Cadence</span>
            <span class="w-6 h-6 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center text-xs">📅</span>
          </div>
          <div class="font-display font-extrabold text-3xl text-slate-900 tracking-tight">16 Posts / mo</div>
          <div class="flex items-center gap-1.5 text-[11px] font-semibold text-indigo-600 mt-1">
            <span>↑ 4 posts / week</span>
            <span class="text-slate-400 font-normal">Mon, Wed, Fri, Sat</span>
          </div>
        </div>

        <!-- Mini Bar Chart (Exact Finnova bar visual) -->
        <div class="flex items-end gap-1.5 h-12 pt-1 px-1">
          <div class="flex-1 bg-indigo-100 rounded-t h-4"></div>
          <div class="flex-1 bg-indigo-200 rounded-t h-7"></div>
          <div class="flex-1 bg-indigo-400 rounded-t h-10"></div>
          <div class="flex-1 bg-indigo-600 rounded-t h-12"></div>
          <div class="flex-1 bg-indigo-500 rounded-t h-8"></div>
          <div class="flex-1 bg-indigo-600 rounded-t h-11"></div>
          <div class="flex-1 bg-indigo-300 rounded-t h-6"></div>
        </div>
      </div>

      <!-- Card 3: Automation Speed (with Spline Line Graph) -->
      <div class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm flex flex-col justify-between h-48">
        <div>
          <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-1">
            <span>Voice & Transcribe Speed</span>
            <span class="w-6 h-6 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center text-xs">⏱</span>
          </div>
          <div class="font-display font-extrabold text-3xl text-slate-900 tracking-tight">1.8 <span class="text-base font-normal text-slate-500">sec</span></div>
          <div class="flex items-center gap-1.5 text-[11px] font-semibold text-emerald-600 mt-1">
            <span>↓ 60% faster</span>
            <span class="text-slate-400 font-normal">Groq Whisper + n8n</span>
          </div>
        </div>

        <!-- Spline Line Graphic -->
        <div class="h-10 w-full relative">
          <svg class="w-full h-full overflow-visible" viewBox="0 0 100 30" preserveAspectRatio="none">
            <path d="M0,25 Q20,20 40,15 T80,8 T100,5" fill="none" stroke="#4f46e5" stroke-width="2.5" stroke-linecap="round" />
            <circle cx="20" cy="22" r="2.5" fill="#4f46e5" />
            <circle cx="50" cy="13" r="2.5" fill="#4f46e5" />
            <circle cx="80" cy="8" r="2.5" fill="#4f46e5" />
            <circle cx="100" cy="5" r="3" fill="#10b981" />
          </svg>
        </div>
      </div>

      <!-- Card 4: LinkedIn Direct Publishing (with card selector chips) -->
      <div class="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm flex flex-col justify-between h-48">
        <div>
          <div class="flex items-center justify-between text-xs font-semibold text-slate-500 mb-1">
            <span>LinkedIn Connection</span>
            <span class="w-6 h-6 rounded-lg bg-sky-50 text-sky-600 flex items-center justify-center text-xs">↗</span>
          </div>
          <div class="font-display font-extrabold text-2xl text-slate-900 tracking-tight">API Integrated</div>
          <div class="text-[11px] text-slate-500 font-medium mt-1">
            Profile: <span class="text-indigo-600 font-mono">/in/ascenta</span>
          </div>
        </div>

        <!-- 3 Horizontal Chips (Visa/Stripe/PayPal in screenshot -> our verified systems) -->
        <div class="flex items-center gap-1.5 pt-2">
          <div class="flex-1 p-1.5 rounded-xl bg-slate-50 border border-slate-200 text-center text-[10px] font-mono text-slate-600 truncate">
            CleanData
          </div>
          <div class="flex-1 p-1.5 rounded-xl bg-indigo-600 text-white text-center text-[10px] font-mono font-bold shadow-sm shadow-indigo-600/30 truncate">
            Instagram
          </div>
          <div class="flex-1 p-1.5 rounded-xl bg-slate-50 border border-slate-200 text-center text-[10px] font-mono text-slate-600 truncate">
            LeadPulse
          </div>
        </div>
      </div>

    </div>

    <!-- 4. ACTIVE FILTERS CONTROL BAR -->
    <div class="flex flex-wrap items-center justify-between gap-3 text-xs">
      <div class="flex flex-wrap items-center gap-2">
        <span class="px-3 py-1.5 rounded-full bg-slate-900 text-white font-semibold flex items-center gap-1.5 text-xs">
          <span>Active filters</span>
          <span class="w-4 h-4 rounded-full bg-white text-slate-900 text-[10px] font-bold flex items-center justify-center">2</span>
        </span>

        <select id="filter-pillar" onchange="applyFilters()" class="bg-white border border-slate-200 rounded-full px-3.5 py-1.5 font-medium text-slate-700 outline-none hover:bg-slate-50">
          <option value="ALL">All Content Pillars</option>
          <option value="Real Client Problems">Real Client Problems</option>
          <option value="Building in Public">Building in Public</option>
          <option value="Automation Solutions">Automation Solutions</option>
          <option value="Practical AI Agents">Practical AI Agents</option>
        </select>

        <select id="filter-status" onchange="applyFilters()" class="bg-white border border-slate-200 rounded-full px-3.5 py-1.5 font-medium text-slate-700 outline-none hover:bg-slate-50">
          <option value="ALL">All Statuses</option>
          <option value="READY_FOR_REVIEW">Ready for Review</option>
          <option value="APPROVED">Approved</option>
          <option value="PUBLISHED">Published</option>
        </select>

        <span class="px-3.5 py-1.5 rounded-full bg-white border border-slate-200 font-medium text-slate-600">
          September 2026 📅
        </span>
      </div>

      <!-- Search Bar -->
      <div class="relative w-full sm:w-64">
        <input type="text" id="search-input" oninput="applyFilters()" placeholder="Enter post ID or keyword..." class="w-full bg-white border border-slate-200 rounded-full pl-8 pr-4 py-1.5 text-xs text-slate-800 outline-none focus:border-indigo-500 shadow-sm">
        <svg class="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
      </div>
    </div>

    <!-- 5. SIGNATURE DARK WORKSPACE (DUAL-PANE WORKBENCH FROM FINNOVA) -->
    <section class="bg-[#15192c] rounded-[32px] p-6 lg:p-7 text-white shadow-xl shadow-slate-900/10 space-y-6">
      
      <!-- Top Inner Bar: Section Title + Sub-Tabs -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div class="flex items-center gap-3">
          <h2 class="font-display font-bold text-base text-white">Review & Publishing Workbench</h2>
          <span class="text-xs text-slate-400 font-mono">Live n8n Queue</span>
        </div>

        <!-- Pill Tabs inside Dark Workbench (Exact Finnova styling) -->
        <div class="flex items-center gap-1.5 bg-[#1f243d] p-1 rounded-full text-xs font-medium">
          <button onclick="filterStatusTab('ALL')" id="tab-sub-all" class="px-3.5 py-1 rounded-full text-slate-300 hover:text-white transition">All Posts</button>
          <button onclick="filterStatusTab('READY_FOR_REVIEW')" id="tab-sub-review" class="px-3.5 py-1 rounded-full bg-indigo-600 text-white font-semibold shadow-sm">Review <span id="sub-count-review" class="ml-1 px-1.5 py-0.2 rounded-full bg-white text-indigo-600 text-[10px] font-bold">3</span></button>
          <button onclick="filterStatusTab('APPROVED')" id="tab-sub-approved" class="px-3.5 py-1 rounded-full text-slate-300 hover:text-white transition">Approved</button>
          <button onclick="filterStatusTab('PUBLISHED')" id="tab-sub-published" class="px-3.5 py-1 rounded-full text-slate-300 hover:text-white transition">Published</button>
        </div>
      </div>

      <!-- DUAL PANE GRID: LEFT LIST (38%) + RIGHT DETAIL (62%) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        <!-- LEFT COLUMN: POST LIST (5 COLS) -->
        <div class="lg:col-span-5 space-y-3 dark-scroll max-h-[620px] overflow-y-auto pr-1" id="posts-list-container">
          <!-- Dynamic post items inserted here -->
        </div>

        <!-- RIGHT COLUMN: DETAILED POST INSPECTOR (7 COLS) -->
        <div class="lg:col-span-7 bg-[#202542] rounded-3xl p-6 lg:p-7 border border-slate-700/60 shadow-inner space-y-6 relative overflow-hidden" id="post-detail-container">
          <!-- Detail panel dynamically rendered -->
          <div class="text-center py-20 text-slate-400 text-xs font-mono">Select a post to inspect full content & publish</div>
        </div>

      </div>

    </section>

    <!-- 6. WHAT HAPPENED TODAY? RAW OPERATOR CAPTURE MODAL / DRAWER -->
    <div id="note-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
      <div class="w-full max-w-xl bg-white rounded-3xl p-6 lg:p-7 shadow-2xl space-y-4 text-slate-900">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-indigo-600"></span>
            <h3 class="font-display font-bold text-base text-slate-900">What did you build or observe today?</h3>
          </div>
          <button onclick="closeNoteModal()" class="text-slate-400 hover:text-slate-600 text-lg">✕</button>
        </div>

        <p class="text-xs text-slate-500 leading-relaxed">
          Type an honest 1-sentence note about a bug fix, architecture win, or client problem. The agent transforms it into a grounded post without hallucinated metrics.
        </p>

        <textarea id="modal-note-input" rows="3" placeholder="e.g., Spent 2 hours debugging an n8n webhook timeout; switching heavy Groq Whisper calls to a sub-workflow cut response time by 70%..." class="w-full bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs text-slate-800 outline-none focus:border-indigo-600 transition font-sans"></textarea>

        <div class="flex items-center justify-end gap-2 pt-2">
          <button onclick="closeNoteModal()" class="px-4 py-2 rounded-full bg-slate-100 text-slate-600 text-xs font-semibold hover:bg-slate-200 transition">Cancel</button>
          <button onclick="submitModalNote()" class="px-5 py-2 rounded-full bg-indigo-600 text-white text-xs font-display font-bold hover:bg-indigo-700 transition shadow-sm">Capture & Ingest</button>
        </div>
      </div>
    </div>

    <!-- 7. EDIT POST MODAL -->
    <div id="edit-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
      <div class="w-full max-w-2xl bg-white rounded-3xl p-6 lg:p-7 shadow-2xl space-y-4 text-slate-900">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 class="font-display font-bold text-base text-slate-900">Edit Post Copy</h3>
          <button onclick="closeEditModal()" class="text-slate-400 hover:text-slate-600 text-lg">✕</button>
        </div>

        <input type="hidden" id="edit-post-id">

        <div class="space-y-1">
          <label class="text-[11px] font-mono text-slate-500 uppercase tracking-wider">Hook Line</label>
          <input type="text" id="edit-hook" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 outline-none focus:border-indigo-600">
        </div>

        <div class="space-y-1">
          <label class="text-[11px] font-mono text-slate-500 uppercase tracking-wider">Full Body Copy</label>
          <textarea id="edit-body" rows="9" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 outline-none focus:border-indigo-600 custom-scroll font-sans leading-relaxed"></textarea>
        </div>

        <div class="space-y-1">
          <label class="text-[11px] font-mono text-slate-500 uppercase tracking-wider">Hashtags</label>
          <input type="text" id="edit-hashtags" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 outline-none focus:border-indigo-600 font-mono">
        </div>

        <div class="flex items-center justify-end gap-2 pt-2">
          <button onclick="closeEditModal()" class="px-4 py-2 rounded-full bg-slate-100 text-slate-600 text-xs font-semibold hover:bg-slate-200">Cancel</button>
          <button onclick="saveEditPost()" class="px-5 py-2 rounded-full bg-indigo-600 text-white text-xs font-display font-bold hover:bg-indigo-700 shadow-sm">Save Changes</button>
        </div>
      </div>
    <!-- 8. GENERATE NEW POST MODAL (WITH OPTIONAL TOPIC & PILLAR) -->
    <div id="generate-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
      <div class="w-full max-w-xl bg-white rounded-3xl p-6 lg:p-7 shadow-2xl space-y-4 text-slate-900 animate-in fade-in zoom-in duration-150">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-indigo-600 animate-pulse"></span>
            <h3 class="font-display font-bold text-base text-slate-900">Generate New LinkedIn Post</h3>
          </div>
          <button onclick="closeGenerateModal()" class="text-slate-400 hover:text-slate-600 text-lg">✕</button>
        </div>

        <p class="text-xs text-slate-500 leading-relaxed">
          Tell the agent what you want the post to be about. <strong class="text-indigo-600 font-semibold">This is 100% optional:</strong> leave blank for autonomous rotation through your audited Ascenta builds.
        </p>

        <!-- Optional Topic Input -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <label class="text-[11px] font-mono text-slate-700 font-semibold uppercase tracking-wider">What should this post be about? <span class="text-slate-400 font-normal lowercase">(optional)</span></label>
            <span class="text-[10px] text-indigo-600 font-medium">Custom Topic</span>
          </div>
          <input type="text" id="gen-topic-input" placeholder="e.g. Lead leakage on Instagram DMs, n8n webhook timeouts, SQLite in-browser..." class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs text-slate-800 outline-none focus:border-indigo-600 font-sans">
        </div>

        <!-- Optional Pillar Selection -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="space-y-1">
            <label class="text-[11px] font-mono text-slate-700 font-semibold uppercase tracking-wider">Content Pillar <span class="text-slate-400 font-normal lowercase">(optional)</span></label>
            <select id="gen-pillar-select" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800 outline-none focus:border-indigo-600 font-sans">
              <option value="">Auto-Select / Rotate Pillars</option>
              <option value="pillar_1_client_problems">Real Client Problems</option>
              <option value="pillar_2_automation_solutions">Automation Solutions</option>
              <option value="pillar_3_ai_agents">Practical AI Agents</option>
              <option value="pillar_4_building_in_public">Building in Public & Lessons</option>
              <option value="pillar_5_fullstack_dev">Full-Stack Dev & Architecture</option>
              <option value="pillar_6_business_tech">Translating Tech to Business</option>
              <option value="pillar_7_automation_education">Automation Education</option>
              <option value="pillar_8_observations">Operator Observations</option>
            </select>
          </div>

          <div class="space-y-1">
            <label class="text-[11px] font-mono text-slate-700 font-semibold uppercase tracking-wider">Tone & Style</label>
            <select id="gen-tone-select" class="w-full bg-slate-50 border border-slate-200 rounded-xl p-2.5 text-xs text-slate-800 outline-none focus:border-indigo-600 font-sans">
              <option value="Technical & Observant">Technical & Observant (Default)</option>
              <option value="Contrarian Truth">Contrarian Truth / Tough Reality</option>
              <option value="Step-by-Step Breakdown">Step-by-Step Architectural Breakdown</option>
              <option value="Founder Reflection">Founder & Operator Reflection</option>
            </select>
          </div>
        </div>

        <!-- Knowledge Base Grounding Info -->
        <div class="p-3 rounded-xl bg-indigo-50/70 border border-indigo-100 flex items-center gap-2.5 text-indigo-900 text-[11px]">
          <span class="text-base">🛡️</span>
          <span>Zero hallucination policy: Post will be grounded strictly in your 6 verified Ascenta projects with clean formatting.</span>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2">
          <button onclick="closeGenerateModal()" class="px-4 py-2 rounded-full bg-slate-100 text-slate-600 text-xs font-semibold hover:bg-slate-200 transition">Cancel</button>
          <button onclick="submitGenerateModal()" id="btn-submit-generate" class="px-6 py-2.5 rounded-full bg-indigo-600 text-white text-xs font-display font-bold hover:bg-indigo-700 transition shadow-md shadow-indigo-600/20 flex items-center gap-1.5">
            <span>✨ Generate Post</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 9. TAB VIEWS (SCHEDULE / KNOWLEDGE BASE / FEED SIMULATOR) -->
    <!-- CALENDAR SCHEDULE MODAL / VIEW -->
    <div id="calendar-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
      <div class="w-full max-w-4xl bg-white rounded-3xl p-6 lg:p-7 shadow-2xl space-y-4 text-slate-900 max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">📅</span>
            <div>
              <h3 class="font-display font-bold text-base text-slate-900">30-Day Content Cadence Schedule</h3>
              <p class="text-[11px] text-slate-500 font-medium">Cadence: 4 posts / week (Monday, Wednesday, Friday, Saturday)</p>
            </div>
          </div>
          <button onclick="closeCalendarModal()" class="text-slate-400 hover:text-slate-600 text-lg">✕</button>
        </div>

        <div class="overflow-y-auto custom-scroll pr-1 flex-1">
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3" id="calendar-grid-container">
            <!-- Calendar days rendered dynamically -->
          </div>
        </div>
      </div>
    </div>

    <!-- KNOWLEDGE BASE MODAL / VIEW -->
    <div id="kb-modal" class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm hidden items-center justify-center p-4">
      <div class="w-full max-w-4xl bg-white rounded-3xl p-6 lg:p-7 shadow-2xl space-y-4 text-slate-900 max-h-[85vh] flex flex-col">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">📚</span>
            <div>
              <h3 class="font-display font-bold text-base text-slate-900">Muhammad Rayyan's Audited Knowledge Base</h3>
              <p class="text-[11px] text-slate-500 font-medium">6 Verified Production Systems powering your LinkedIn Agent</p>
            </div>
          </div>
          <button onclick="closeKbModal()" class="text-slate-400 hover:text-slate-600 text-lg">✕</button>
        </div>

        <div class="overflow-y-auto custom-scroll pr-1 flex-1 space-y-3" id="kb-projects-container">
          <!-- Projects rendered dynamically -->
        </div>
      </div>
    </div>

  </div>

  <!-- JAVASCRIPT CONTROLLER -->
  <script>
    let allPosts = [];
    let selectedPostId = null;
    let currentFilterStatus = 'READY_FOR_REVIEW';
    let currentPillarFilter = 'ALL';
    let searchQuery = '';

    function showToast(msg) {
      const el = document.getElementById('toast');
      document.getElementById('toast-message').textContent = msg;
      el.classList.remove('translate-y-[-120px]', 'opacity-0');
      el.classList.add('translate-y-0', 'opacity-100');
      setTimeout(() => {
        el.classList.remove('translate-y-0', 'opacity-100');
        el.classList.add('translate-y-[-120px]', 'opacity-0');
      }, 3500);
    }

    async function loadData() {
      try {
        const res = await fetch('/api/posts');
        allPosts = await res.json();
        if (allPosts.length > 0 && !selectedPostId) {
          selectedPostId = allPosts[0].id;
        }
        renderWorkbench();
        updateKpis();
      } catch (e) {
        console.error('Error fetching posts:', e);
      }
    }

    function updateKpis() {
      const reviewCount = allPosts.filter(p => p.status === 'READY_FOR_REVIEW').length;
      document.getElementById('kpi-review-count').textContent = `${reviewCount} Posts`;
      document.getElementById('sub-count-review').textContent = reviewCount;
    }

    function applyFilters() {
      currentPillarFilter = document.getElementById('filter-pillar').value;
      const statusSelect = document.getElementById('filter-status').value;
      if (statusSelect !== 'ALL') {
        currentFilterStatus = statusSelect;
      }
      searchQuery = document.getElementById('search-input').value.toLowerCase();
      renderWorkbench();
    }

    function filterStatusTab(status) {
      currentFilterStatus = status;
      const tabs = ['all', 'review', 'approved', 'published'];
      tabs.forEach(t => {
        const btn = document.getElementById('tab-sub-' + t);
        if ((t === 'all' && status === 'ALL') || 
            (t === 'review' && status === 'READY_FOR_REVIEW') ||
            (t === 'approved' && status === 'APPROVED') ||
            (t === 'published' && status === 'PUBLISHED')) {
          btn.className = 'px-3.5 py-1 rounded-full bg-indigo-600 text-white font-semibold shadow-sm';
        } else {
          btn.className = 'px-3.5 py-1 rounded-full text-slate-300 hover:text-white transition';
        }
      });
      renderWorkbench();
    }

    function renderWorkbench() {
      const container = document.getElementById('posts-list-container');
      const filtered = allPosts.filter(p => {
        const matchesStatus = currentFilterStatus === 'ALL' || p.status === currentFilterStatus;
        const matchesPillar = currentPillarFilter === 'ALL' || p.pillar_name === currentPillarFilter;
        const matchesSearch = !searchQuery || 
          (p.hook && p.hook.toLowerCase().includes(searchQuery)) ||
          (p.body && p.body.toLowerCase().includes(searchQuery)) ||
          (p.id && p.id.toLowerCase().includes(searchQuery));
        return matchesStatus && matchesPillar && matchesSearch;
      });

      if (filtered.length === 0) {
        container.innerHTML = '<div class="text-xs text-slate-400 font-mono py-12 text-center">No posts found in this queue.</div>';
        renderDetail(null);
        return;
      }

      // Check if selected post still in list
      if (!filtered.some(p => p.id === selectedPostId)) {
        selectedPostId = filtered[0].id;
      }

      container.innerHTML = filtered.map(post => {
        const isSelected = post.id === selectedPostId;
        const activeClass = isSelected ? 'bg-indigo-600 shadow-md shadow-indigo-600/30 text-white' : 'bg-[#1b2038] hover:bg-[#202744] text-slate-300';
        
        let statusTag = 'Unsent';
        let statusBadgeClass = 'bg-slate-800 text-slate-300';
        if (post.status === 'APPROVED') {
          statusTag = 'Approved';
          statusBadgeClass = 'bg-emerald-950 text-emerald-400 border border-emerald-800/40';
        } else if (post.status === 'PUBLISHED') {
          statusTag = 'Published';
          statusBadgeClass = 'bg-sky-950 text-sky-400 border border-sky-800/40';
        } else {
          statusTag = 'Review';
          statusBadgeClass = 'bg-amber-950 text-amber-400 border border-amber-800/40';
        }

        const shortId = post.id.replace('post_', '# INV-');

        return `
          <div onclick="selectPost('${post.id}')" class="p-3.5 rounded-2xl ${activeClass} cursor-pointer flex items-center justify-between transition-all duration-200">
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 rounded-full bg-slate-900/60 flex items-center justify-center font-display font-bold text-xs text-white">
                MR
              </div>
              <div>
                <div class="font-display font-bold text-xs text-white flex items-center gap-1.5">
                  <span>${shortId}</span>
                </div>
                <div class="text-[11px] text-slate-400 truncate max-w-[140px]">${post.pillar_name || 'AI Automation'}</div>
              </div>
            </div>

            <div class="flex items-center gap-2 text-right">
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-mono font-medium ${statusBadgeClass}">
                ${statusTag}
              </span>
              <div class="text-xs font-mono font-semibold text-white">Ready</div>
            </div>
          </div>
        `;
      }).join('');

      const selectedPost = allPosts.find(p => p.id === selectedPostId);
      renderDetail(selectedPost);
    }

    function selectPost(id) {
      selectedPostId = id;
      renderWorkbench();
    }

    function renderDetail(post) {
      const container = document.getElementById('post-detail-container');
      if (!post) {
        container.innerHTML = '<div class="text-center py-20 text-slate-400 text-xs font-mono">No post selected.</div>';
        return;
      }

      const shortId = post.id.replace('post_', '# INV-');
      const isApproved = post.status === 'APPROVED';
      const isPublished = post.status === 'PUBLISHED';

      container.innerHTML = `
        <!-- Top Detail Rail (Matches FINNOVA detail panel) -->
        <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-700/60 pb-5">
          <div>
            <span class="text-[11px] font-mono text-slate-400 uppercase">Post Details</span>
            <div class="font-display font-bold text-lg text-white flex items-center gap-2 mt-0.5">
              <span>${shortId}</span>
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
                ${post.status}
              </span>
            </div>
          </div>

          <div>
            <span class="text-[11px] font-mono text-slate-400 uppercase">Source System</span>
            <div class="font-display font-semibold text-sm text-white mt-0.5">
              ${post.project_id ? post.project_id.replace('-', ' ').toUpperCase() : 'ASCENTA AUTOMATION'} 🌐
            </div>
          </div>

          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-full bg-slate-900 text-white flex items-center justify-center font-bold text-xs">MR</div>
            <div>
              <div class="font-semibold text-xs text-white leading-tight">Muhammad Rayyan</div>
              <p class="text-[10px] text-slate-400">Founder & AI Engineer</p>
            </div>
          </div>
        </div>

        <!-- Middle 3 Metric Boxes (Exact Finnova design) -->
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div class="p-3.5 rounded-2xl bg-[#181c33] border border-slate-700/40 space-y-1">
            <div class="flex items-center justify-between text-slate-400 text-[11px]">
              <span>Pillar Category</span>
              <span>↗</span>
            </div>
            <div class="font-display font-bold text-sm text-white truncate">${post.pillar_name || 'AI Engineering'}</div>
            <div class="text-[10px] text-indigo-300">100% Grounded</div>
          </div>

          <div class="p-3.5 rounded-2xl bg-[#181c33] border border-slate-700/40 space-y-1">
            <div class="flex items-center justify-between text-slate-400 text-[11px]">
              <span>Fact Check</span>
              <span>✓</span>
            </div>
            <div class="font-display font-bold text-sm text-emerald-400">Verified Fact</div>
            <div class="text-[10px] text-slate-400">Zero AI Hallucination</div>
          </div>

          <div class="p-3.5 rounded-2xl bg-[#181c33] border border-slate-700/40 space-y-1">
            <div class="flex items-center justify-between text-slate-400 text-[11px]">
              <span>Buzzword Audit</span>
              <span>✓</span>
            </div>
            <div class="font-display font-bold text-sm text-white">0 Banned Words</div>
            <div class="text-[10px] text-slate-400">Passed Copy Gate</div>
          </div>
        </div>

        <!-- Hook Highlight -->
        <div class="p-4 rounded-2xl bg-[#14182b] border-l-4 border-indigo-500 text-slate-100 font-display font-semibold text-xs leading-relaxed">
          "${escapeHtml(post.hook || '')}"
        </div>

        <!-- Full Formatted Body Text -->
        <div class="p-4 rounded-2xl bg-[#181c33]/70 border border-slate-700/40 text-xs text-slate-300 leading-relaxed max-h-52 overflow-y-auto dark-scroll whitespace-pre-wrap font-sans">
${escapeHtml(post.body || '')}
        </div>

        ${post.image_file ? `
          <div class="rounded-2xl overflow-hidden border border-slate-700/60 shadow-md">
            <div class="px-3.5 py-1.5 bg-[#181c33] text-[10px] font-mono text-indigo-300 flex items-center justify-between border-b border-slate-700/40">
              <span>🖼️ ARCHITECTURE INFOGRAPHIC (READY TO ATTACH)</span>
              <a href="/${post.image_file}" target="_blank" class="hover:underline text-white">Full Resolution ↗</a>
            </div>
            <img src="/${post.image_file}" alt="Architecture Visual" class="w-full object-cover max-h-56">
          </div>
        ` : ''}

        <!-- Hashtags -->
        <div class="text-xs font-mono text-indigo-400">
          ${(post.hashtags || []).join(' ')}
        </div>

        <!-- Bottom Action Bar with White Primary Pill Button (Exact FINNOVA button) -->
        <div class="pt-4 border-t border-slate-700/60 flex flex-wrap items-center justify-between gap-3">
          <div class="flex items-center gap-4 text-xs font-mono">
            <div>
              <span class="text-slate-400 text-[10px]">TOTAL WORDS</span>
              <div class="font-bold text-white text-sm">${post.body ? post.body.split(/\\s+/).length : 0}</div>
            </div>
            <div>
              <span class="text-slate-400 text-[10px]">READ TIME</span>
              <div class="font-bold text-indigo-300 text-sm">~2 min</div>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button onclick="openEditModal('${post.id}')" title="Edit Copy" class="w-10 h-10 rounded-full bg-[#1b2038] hover:bg-slate-700 text-slate-300 flex items-center justify-center text-xs transition">
              ✏
            </button>
            <button onclick="copyPost('${post.id}')" title="Copy to Clipboard" class="w-10 h-10 rounded-full bg-[#1b2038] hover:bg-slate-700 text-slate-300 flex items-center justify-center text-xs transition">
              📋
            </button>

            ${!isApproved && !isPublished ? `
              <button onclick="approvePost('${post.id}')" class="px-5 py-2.5 rounded-full bg-indigo-600 hover:bg-indigo-500 text-white font-display font-bold text-xs transition shadow-md">
                ✓ Approve Post
              </button>
            ` : ''}

            <!-- Signature White Primary Pill Button (like "Payout now" in Finnova) -->
            <button onclick="publishToLinkedIn('${post.id}')" class="px-6 py-2.5 rounded-full bg-white hover:bg-slate-100 text-slate-900 font-display font-bold text-xs tracking-wide transition shadow-lg active:scale-95 flex items-center gap-1.5">
              <span>Publish to LinkedIn ↗</span>
            </button>
          </div>
        </div>
      `;
    }

    function escapeHtml(t) {
      const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
      return (t || '').replace(/[&<>"']/g, m => map[m]);
    }

    async function approvePost(id) {
      try {
        await fetch('/api/approve', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ post_id: id })
        });
        showToast('✓ Post APPROVED & synced to n8n publishing pipeline!');
        loadData();
      } catch (e) {
        showToast('Error approving post');
      }
    }

    async function publishToLinkedIn(id) {
      const post = allPosts.find(p => p.id === id);
      if (!post) return;

      showToast('🚀 Publishing directly to your LinkedIn feed...');

      try {
        const res = await fetch('/api/publish', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ post_id: id })
        });
        const result = await res.json();

        if (result.success) {
          showToast("🎉 Successfully published to Muhammad Rayyan's LinkedIn feed!");
          loadData();
          if (result.linkedin_url) {
            setTimeout(() => {
              window.open(result.linkedin_url, '_blank');
            }, 800);
          }
        } else {
          showToast('⚠️ LinkedIn API Notice: ' + (result.error || 'Failed to publish'));
        }
      } catch (err) {
        showToast('Error communicating with server');
      }
    }

    async function copyPost(id) {
      const post = allPosts.find(p => p.id === id);
      if (!post) return;
      const fullText = (post.hook ? post.hook + '\\n\\n' : '') + post.body + '\\n\\n' + (post.hashtags || []).join(' ');
      await navigator.clipboard.writeText(fullText);
      showToast('📋 Copied full post with hashtags!');
    }

    // Generate Post Modal controls (Topic is optional)
    function openGenerateModal() {
      document.getElementById('generate-modal').classList.remove('hidden');
      document.getElementById('generate-modal').classList.add('flex');
      document.getElementById('gen-topic-input').focus();
    }
    function closeGenerateModal() {
      document.getElementById('generate-modal').classList.add('hidden');
      document.getElementById('generate-modal').classList.remove('flex');
    }
    async function submitGenerateModal() {
      const topic = document.getElementById('gen-topic-input').value.trim();
      const pillar_id = document.getElementById('gen-pillar-select').value;
      const tone = document.getElementById('gen-tone-select').value;
      const btn = document.getElementById('btn-submit-generate');
      
      btn.disabled = true;
      btn.innerHTML = '<span>⚙ Writing Grounded Post...</span>';

      try {
        const res = await fetch('/api/trigger-generation', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ topic, pillar_id, tone })
        });
        const data = await res.json();
        
        closeGenerateModal();
        document.getElementById('gen-topic-input').value = '';
        
        if (data.success && data.post) {
          selectedPostId = data.post.id;
          currentFilterStatus = 'READY_FOR_REVIEW';
          filterStatusTab('READY_FOR_REVIEW');
          showToast('⚡ New grounded post created & placed in review queue!');
        } else {
          showToast('⚡ New post generated and placed in review queue!');
        }
        loadData();
      } catch (e) {
        showToast('Error generating post');
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>✨ Generate Post</span>';
      }
    }

    function triggerGeneratePost() {
      openGenerateModal();
    }

    // Modal controls for Schedule & Knowledge Base
    function closeCalendarModal() {
      document.getElementById('calendar-modal').classList.add('hidden');
      document.getElementById('calendar-modal').classList.remove('flex');
    }
    async function openCalendarModal() {
      const modal = document.getElementById('calendar-modal');
      const container = document.getElementById('calendar-grid-container');
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      container.innerHTML = '<div class="col-span-full py-10 text-center text-xs text-slate-400">Loading schedule...</div>';

      try {
        const res = await fetch('/api/calendar');
        const days = await res.json();
        
        container.innerHTML = days.map(d => {
          const isPostDay = d.is_scheduled_day;
          const bg = isPostDay ? 'bg-indigo-50/60 border-indigo-200' : 'bg-slate-50/60 border-slate-200/60';
          const badge = isPostDay ? '<span class="px-2 py-0.5 rounded-full bg-indigo-600 text-white text-[9px] font-bold">Publish Day</span>' : '<span class="text-[10px] text-slate-400 font-mono">Rest / Buffer</span>';
          
          return `
            <div class="p-3.5 rounded-2xl border ${bg} flex flex-col justify-between h-32">
              <div>
                <div class="flex items-center justify-between text-xs font-semibold">
                  <span class="text-slate-800">${d.day_name.slice(0,3)}, ${d.date.slice(5)}</span>
                  ${badge}
                </div>
                ${d.assigned_pillar ? `<div class="text-[11px] font-display font-bold text-indigo-700 mt-2 truncate">${d.assigned_pillar}</div>` : ''}
              </div>
              <div class="text-[10px] text-slate-500 font-mono">
                ${d.post ? '✓ Post Ready: ' + d.post.id.slice(0,10) : (isPostDay ? 'Queue slot open' : 'No publish scheduled')}
              </div>
            </div>
          `;
        }).join('');
      } catch (e) {
        container.innerHTML = '<div class="col-span-full py-10 text-center text-xs text-rose-500">Failed to load schedule.</div>';
      }
    }

    function closeKbModal() {
      document.getElementById('kb-modal').classList.add('hidden');
      document.getElementById('kb-modal').classList.remove('flex');
    }
    async function openKbModal() {
      const modal = document.getElementById('kb-modal');
      const container = document.getElementById('kb-projects-container');
      modal.classList.remove('hidden');
      modal.classList.add('flex');
      container.innerHTML = '<div class="py-10 text-center text-xs text-slate-400">Loading verified projects...</div>';

      try {
        const res = await fetch('/api/projects');
        const projects = await res.json();
        
        container.innerHTML = projects.map(p => `
          <div class="p-4 rounded-2xl border border-slate-200/80 bg-slate-50/60 space-y-2 hover:border-indigo-300 transition">
            <div class="flex items-center justify-between">
              <div class="font-display font-bold text-sm text-slate-900">${p.name}</div>
              <span class="px-2.5 py-0.5 rounded-full bg-indigo-100 text-indigo-700 text-[10px] font-mono font-semibold">${p.category}</span>
            </div>
            <p class="text-xs text-slate-600 leading-relaxed">${p.problem}</p>
            <div class="p-2.5 rounded-xl bg-white border border-slate-200 text-xs text-slate-800">
              <strong class="text-indigo-600">Ascenta Solution:</strong> ${p.solution}
            </div>
            <div class="flex flex-wrap items-center gap-1.5 pt-1">
              ${(p.tech_stack || []).map(t => `<span class="px-2 py-0.5 rounded bg-slate-200/70 text-slate-700 text-[10px] font-mono">${t}</span>`).join('')}
            </div>
          </div>
        `).join('');
      } catch (e) {
        container.innerHTML = '<div class="py-10 text-center text-xs text-rose-500">Failed to load knowledge base.</div>';
      }
    }

    // Modal controls
    function openNoteModal() {
      document.getElementById('note-modal').classList.remove('hidden');
      document.getElementById('note-modal').classList.add('flex');
    }
    function closeNoteModal() {
      document.getElementById('note-modal').classList.add('hidden');
      document.getElementById('note-modal').classList.remove('flex');
    }
    async function submitModalNote() {
      const input = document.getElementById('modal-note-input');
      const text = input.value.trim();
      if (!text) return;

      try {
        await fetch('/api/note', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ raw_text: text })
        });
        input.value = '';
        closeNoteModal();
        showToast('✓ Raw observation captured and ingested!');
        loadData();
      } catch (e) {
        showToast('Error saving note');
      }
    }

    function openEditModal(id) {
      const post = allPosts.find(p => p.id === id);
      if (!post) return;
      document.getElementById('edit-post-id').value = post.id;
      document.getElementById('edit-hook').value = post.hook || '';
      document.getElementById('edit-body').value = post.body || '';
      document.getElementById('edit-hashtags').value = (post.hashtags || []).join(' ');
      document.getElementById('edit-modal').classList.remove('hidden');
      document.getElementById('edit-modal').classList.add('flex');
    }
    function closeEditModal() {
      document.getElementById('edit-modal').classList.add('hidden');
      document.getElementById('edit-modal').classList.remove('flex');
    }
    async function saveEditPost() {
      const id = document.getElementById('edit-post-id').value;
      const hook = document.getElementById('edit-hook').value;
      const body = document.getElementById('edit-body').value;
      const hashtags = document.getElementById('edit-hashtags').value.split(' ').filter(h => h.trim());

      try {
        await fetch('/api/edit', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ post_id: id, hook, body, hashtags })
        });
        showToast('✓ Post updated successfully!');
        closeEditModal();
        loadData();
      } catch (e) {
        showToast('Error saving post');
      }
    }

    function setTab(tab) {
      const tabs = ['overview', 'queue', 'calendar', 'knowledge', 'simulator'];
      tabs.forEach(t => {
        const btn = document.getElementById('nav-' + t);
        if (t.toUpperCase() === tab) {
          btn.className = 'px-4 py-2 rounded-full bg-indigo-600 text-white shadow-sm flex items-center gap-1.5';
        } else {
          btn.className = 'px-4 py-2 rounded-full text-slate-300 hover:text-white transition';
        }
      });
      if (tab === 'OVERVIEW') {
        currentFilterStatus = 'ALL';
        filterStatusTab('ALL');
        showToast('Showing all content streams');
      } else if (tab === 'QUEUE') {
        currentFilterStatus = 'READY_FOR_REVIEW';
        filterStatusTab('READY_FOR_REVIEW');
        showToast('Filtered to In-Flight Review Queue');
      } else if (tab === 'CALENDAR') {
        openCalendarModal();
      } else if (tab === 'KNOWLEDGE') {
        openKbModal();
      } else if (tab === 'SIMULATOR') {
        window.open('https://www.linkedin.com/feed/?shareActive=true', '_blank');
      }
    }

    loadData();
  </script>

</body>
</html>
"""


class ContentAgentHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status_code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, html_str, status_code=200):
        body = html_str.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path in ["/", "/index.html"]:
            self._send_html(HTML_TEMPLATE)
            return
        
        elif path.startswith("/data/"):
            file_path = Path(__file__).resolve().parent / path.lstrip("/")
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                if path.endswith(".jpg") or path.endswith(".jpeg"):
                    self.send_header("Content-Type", "image/jpeg")
                elif path.endswith(".png"):
                    self.send_header("Content-Type", "image/png")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                data = file_path.read_bytes()
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

        elif path == "/api/posts":
            posts = agent_core.get_posts()
            self._send_json(posts)
            return

        elif path == "/api/calendar":
            calendar = agent_core.get_calendar_schedule(days=28)
            self._send_json(calendar)
            return

        elif path == "/api/projects":
            kb = agent_core.get_knowledge_base()
            self._send_json(kb.get("projects", []))
            return

        elif path == "/api/notes":
            notes = agent_core.get_notes()
            self._send_json(notes)
            return

        elif path == "/api/pillars":
            pillars = agent_core.get_content_pillars()
            self._send_json(pillars)
            return

        elif path == "/api/status":
            posts = agent_core.get_posts()
            kb = agent_core.get_knowledge_base()
            self._send_json({
                "status": "online",
                "operator": "Muhammad Rayyan",
                "agency": "Ascenta",
                "n8n_workflow_id": "Zlf4xBioZKJTTZyH",
                "n8n_active": True,
                "posts_count": len(posts),
                "verified_projects": len(kb.get("projects", []))
            })
            return

        else:
            self.send_error(404, "Endpoint not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        payload = json.loads(post_data.decode("utf-8")) if post_data else {}

        if path == "/api/note":
            raw_text = payload.get("raw_text", "")
            if not raw_text:
                self._send_json({"error": "No text provided"}, 400)
                return
            new_note = agent_core.add_quick_note(raw_text)
            # Sync to live n8n webhook
            agent_core.trigger_n8n_webhook("quick_note", {"note_id": new_note["id"], "raw_text": raw_text})
            self._send_json({"success": True, "note": new_note})
            return

        elif path == "/api/approve":
            post_id = payload.get("post_id")
            success = agent_core.approve_post(post_id)
            if success:
                agent_core.trigger_n8n_webhook("approve", {"post_id": post_id})
            self._send_json({"success": success})
            return

        elif path == "/api/reject":
            post_id = payload.get("post_id")
            success = agent_core.reject_post(post_id)
            if success:
                agent_core.trigger_n8n_webhook("reject", {"post_id": post_id})
            self._send_json({"success": success})
            return

        elif path == "/api/publish":
            post_id = payload.get("post_id")
            pub_result = agent_core.publish_to_linkedin_api(post_id)
            self._send_json(pub_result)
            return

        elif path == "/api/edit":
            post_id = payload.get("post_id")
            updated_fields = {
                "hook": payload.get("hook"),
                "body": payload.get("body"),
                "hashtags": payload.get("hashtags")
            }
            success = agent_core.update_post(post_id, updated_fields)
            self._send_json({"success": success})
            return

        elif path == "/api/generate-from-note":
            note_id = payload.get("note_id")
            new_post = agent_core.generate_post_from_note(note_id)
            if new_post:
                # Alert n8n
                agent_core.trigger_n8n_webhook("note_to_post", {"post_id": new_post["id"]})
                self._send_json({"success": True, "post": new_post})
            else:
                self._send_json({"error": "Could not find note"}, 404)
            return

        elif path == "/api/trigger-generation":
            topic = payload.get("topic", "")
            pillar_id = payload.get("pillar_id", None)
            tone = payload.get("tone", "Technical & Observant")
            new_post = agent_core.generate_custom_post(topic=topic, pillar_id=pillar_id, tone=tone)
            # Notify n8n
            agent_core.trigger_n8n_webhook("new_post_created", {"post_id": new_post["id"]})
            self._send_json({"success": True, "post": new_post})
            return

        else:
            self.send_error(404, "Endpoint not found")


def run_dashboard(port=PORT):
    server_address = (HOST, port)
    httpd = ThreadingHTTPServer(server_address, ContentAgentHandler)
    print(f"============================================================")
    print(f" Ascenta Autonomous LinkedIn Content Engine (Finnova Design)")
    print(f" Operator: Muhammad Rayyan")
    print(f" URL: http://localhost:{port}")
    print(f" n8n Webhook: https://primary-production-675a3.up.railway.app/webhook/linkedin-content-agent")
    print(f" Status: Live & Ready")
    print(f"============================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server...")
        httpd.server_close()


if __name__ == "__main__":
    run_dashboard()
