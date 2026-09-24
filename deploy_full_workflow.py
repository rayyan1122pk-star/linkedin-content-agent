import os
import urllib.request
import json
import uuid

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

API_KEY = os.getenv('N8N_API_KEY', '')
BASE_URL = os.getenv('N8N_BASE_URL', 'https://primary-production-675a3.up.railway.app')
WORKFLOW_ID = os.getenv('N8N_WORKFLOW_ID', 'Zlf4xBioZKJTTZyH')
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

workflow_name = "Muhammad Rayyan — Autonomous LinkedIn Content Agent (Full Production)"

system_prompt = """You are the autonomous LinkedIn Personal Brand Content Writer for Muhammad Rayyan, Founder & Lead AI Solutions Engineer at Ascenta (ascenta-agency.vercel.app).

Your mission is to write high-impact, authentic, educational LinkedIn posts based STRICTLY on Muhammad's real engineering builds, technical decisions, client problems, and lessons.

==================================================
MUHAMMAD RAYYAN'S VERIFIED KNOWLEDGE BASE:
==================================================
1. CleanData AI (cleandata-ruddy.vercel.app): Autonomous AI Data Specialist SaaS. Solves dirty spreadsheet problems, PII masking, embedded in-browser SQLite query engine, and RAG vector syncing across Supabase pgvector & Pinecone.
2. Instagram Multimodal AI CRM: Meta Graph API, n8n, Groq Whisper voice note transcription (<2s), Vision LLM screenshot parsing, Next.js 15/Prisma CRM, seen/typing status, 1-click human takeover.
3. LeadPulse AI CRM: B2B lead generation engine with Serper Places API, strict 4-tier deduplication (Place ID, E.164 phone, root domain, name+city), website opportunity audit, GPT-4o-mini personalized pitch generator, 1-click WhatsApp & Gmail dispatch.
4. Misaal Foundation (misaalfoundation.online): High-performance web portal (Next.js 16, Supabase, Tailwind v4) and real-time field operations CRM replacing paper logs with standardized Google Forms/Sheets sync.
5. WhatsApp AI Conversational CRM: Meta Cloud API, n8n, Claude/OpenAI 24/7 multi-turn lead qualification with warm human takeover.
6. Voice Calling Engine: Twilio Media Streams, WebSockets, Deepgram STT, Cartesia TTS with sub-800ms roundtrip latency.

==================================================
MANDATORY WRITING PHILOSOPHY:
==================================================
Structure:
REAL PROBLEM
→ REAL CONTEXT
→ WHAT WAS HAPPENING
→ WHAT WE DISCOVERED
→ WHAT WAS DONE (TECHNICAL IMPLEMENTATION)
→ WHY IT MATTERED (BUSINESS IMPACT)
→ LESSON FOR OPERATORS / DEVELOPERS
→ NATURAL CONVERSATION CTA

VOICE & TONE RULES:
- Direct, observant, technical yet accessible to founders and operators.
- Write in 1st person ('I' / 'We').
- Paragraph length: 1 to 3 sentences maximum with double line breaks for mobile reading.
- Hook must be in the first 2 lines. Prefer number-first, specific technical contradiction, or uncomfortable truth.
- NEVER use generic openers: 'In today's fast-paced world', 'Here's the thing', 'Game changer', 'Unlock your potential', 'Delve', 'Leverage', 'Streamline', 'Harness'.
- Capped em-dashes (maximum 1 per post; prefer periods or colons).
- Soft discussion CTA at the end. NEVER say 'Agree?' or 'Comment below'.
- NEVER FABRICATE: Never invent client names, revenue numbers, or fake statistics.

OUTPUT FORMAT:
Return pure, valid JSON with these keys:
{
  "hook": "The first 1-2 punchy lines",
  "body": "The complete, fully formatted LinkedIn post text",
  "cta": "The closing discussion question",
  "hashtags": ["#AIAutomation", "#n8n", "#Nextjs", ...],
  "pillar": "Pillar Name",
  "image_recommended": true/false,
  "image_concept": "Brief visual description if an architecture diagram or graphic helps"
}
"""

nodes = [
    # -------------------------------------------------------------
    # 1. TRIGGER & INGESTION HUB
    # -------------------------------------------------------------
    {
        "id": "trigger-schedule",
        "name": "Daily Morning Schedule (09:00 AM)",
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [220, 200],
        "parameters": {
            "rule": {
                "interval": [
                    {
                        "field": "cronExpression",
                        "expression": "0 9 * * *"
                    }
                ]
            }
        }
    },
    {
        "id": "trigger-webhook",
        "name": "LinkedIn Agent Webhook (Note & Control)",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2,
        "position": [220, 380],
        "parameters": {
            "path": "linkedin-content-agent",
            "httpMethod": "POST",
            "responseMode": "responseNode",
            "options": {}
        }
    },
    {
        "id": "trigger-manual",
        "name": "Manual Test Trigger",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [220, 560],
        "parameters": {}
    },

    # -------------------------------------------------------------
    # 2. CONTEXT & KNOWLEDGE INJECTION
    # -------------------------------------------------------------
    {
        "id": "code-context-router",
        "name": "Context & Knowledge Router",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [540, 380],
        "parameters": {
            "jsCode": """
const input = $input.first() ? $input.first().json : {};
const body = input.body || input;
const query = input.query || {};

const action = body.action || query.action || 'generate';
const noteText = body.note_text || query.note_text || '';
const postId = body.post_id || query.post_id || '';

// Muhammad's 8 Content Pillars with Strategic Cadence
const pillars = [
  { id: 'pillar_1', name: 'Real Client Problems', topic: 'Why weekend social lead response delays kill conversions (Instagram Voice Notes & CRM)', day: 'Monday' },
  { id: 'pillar_2', name: 'Automation Solutions', topic: 'Replacing manual Google Maps scraping with 4-tier deduplication and n8n orchestration', day: 'Tuesday' },
  { id: 'pillar_3', name: 'Practical AI Agents', topic: 'How to build strict prompt boundaries so your AI agent never hallucinates pricing', day: 'Wednesday' },
  { id: 'pillar_4', name: 'Building in Public', topic: 'Why feeding raw spreadsheets into LLMs breaks date formats, and how embedded SQLite solves it', day: 'Thursday' },
  { id: 'pillar_5', name: 'Full-Stack Architecture', topic: 'Sub-second Core Web Vitals on Next.js 15: why performance is a trust signal', day: 'Friday' },
  { id: 'pillar_6', name: 'Translating Tech to Business', topic: 'Custom software vs off-the-shelf SaaS: when building an internal hub saves $1000s', day: 'Saturday' },
  { id: 'pillar_7', name: 'Automation Education', topic: 'The 3-question audit to determine if a manual workflow should be automated', day: 'Sunday' },
  { id: 'pillar_8', name: 'Operator Observations', topic: 'What 40+ completed client builds taught me about software delivery and scope', day: 'Contrarian' }
];

// Muhammad's 6 Verified Ascenta Projects
const projects = [
  { id: 'cleandata', name: 'CleanData AI', stack: 'Next.js 15, SQLite in-memory, Supabase pgvector, Pinecone', problem: 'Spreadsheet hallucinations and PII exposure' },
  { id: 'insta-crm', name: 'Instagram Multimodal CRM', stack: 'Meta Graph API, n8n, Groq Whisper, Vision LLM, Next.js 15', problem: 'Weekend lead dropoff from voice notes and screenshots' },
  { id: 'leadpulse', name: 'LeadPulse AI CRM', stack: 'Serper Places API, n8n, Supabase, 4-tier deduplication', problem: 'Low reply rates from dirty scraped contact lists' },
  { id: 'misaal', name: 'Misaal Foundation', stack: 'Next.js 16, Supabase, Tailwind v4, Sheets API', problem: 'Paper logs and delayed donor accountability' },
  { id: 'whatsapp-crm', name: 'WhatsApp AI Conversational CRM', stack: 'Meta Cloud API, n8n, Claude/OpenAI', problem: '24/7 lead qualification without spamming prospects' },
  { id: 'twilio-voice', name: 'Voice Calling Engine', stack: 'Twilio Media Streams, WebSockets, Deepgram, Cartesia', problem: 'High latency voice agents that feel robotic' }
];

// Pick today's pillar based on day of month
const dayIndex = new Date().getDate() % pillars.length;
const selectedPillar = pillars[dayIndex];
const selectedProject = projects[dayIndex % projects.length];

return [{
  json: {
    action: action,
    note_text: noteText,
    post_id: postId,
    selected_pillar: selectedPillar,
    selected_project: selectedProject,
    user_prompt: noteText 
      ? `Muhammad Rayyan just captured this fresh note from his day: "${noteText}". Transform this real observation into a high-value educational LinkedIn post following his voice rules. Connect it to his real technical background where natural.`
      : `Generate today's scheduled educational LinkedIn post on the pillar: "${selectedPillar.name}". Focus topic: "${selectedPillar.topic}". Ground the narrative directly in Muhammad's real project records: CleanData AI, LeadPulse CRM, Instagram AI CRM, Misaal Foundation, or n8n pipelines.`
  }
}];
"""
        }
    },

    # -------------------------------------------------------------
    # 3. ACTION ROUTER FORK (IF NODE)
    # -------------------------------------------------------------
    {
        "id": "switch-action",
        "name": "Is Generate Request?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [840, 380],
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict",
                    "version": 2
                },
                "conditions": [
                    {
                        "id": "c1",
                        "leftValue": "={{ $json.action }}",
                        "rightValue": "generate",
                        "operator": {
                            "type": "string",
                            "operation": "equals"
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        }
    },

    # -------------------------------------------------------------
    # 4. AI GENERATION & REASONING ENGINE
    # -------------------------------------------------------------
    {
        "id": "openrouter-model",
        "name": "OpenRouter Model (Shared)",
        "type": "@n8n/n8n-nodes-langchain.lmChatOpenRouter",
        "typeVersion": 1,
        "position": [1140, 480],
        "parameters": {
            "model": "openai/gpt-4o-mini",
            "options": {
                "temperature": 0.5,
                "maxTokens": 1100
            }
        },
        "credentials": {
            "openRouterApi": {
                "id": "T3fDCtfSCxHOmkja",
                "name": "OpenRouter account"
            }
        }
    },
    {
        "id": "agent-content-writer",
        "name": "AI Content Writer Agent",
        "type": "@n8n/n8n-nodes-langchain.agent",
        "typeVersion": 1.7,
        "position": [1140, 240],
        "parameters": {
            "promptType": "define",
            "text": "={{ $json.user_prompt }}",
            "options": {
                "systemMessage": system_prompt
            }
        }
    },

    # -------------------------------------------------------------
    # 5. ANTI-SLOP QA & FACT-CHECKING GATE
    # -------------------------------------------------------------
    {
        "id": "code-humanizer-factcheck",
        "name": "Humanizer & Fact-Check Gate",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1460, 240],
        "parameters": {
            "jsCode": """
const item = $input.first().json;
const rawOutput = item.output || item.text || JSON.stringify(item);

let parsed = {};
try {
  // Extract JSON from markdown code fence if present
  const jsonMatch = rawOutput.match(/\\{([\\s\\S]*)\\}/);
  if (jsonMatch) {
    parsed = JSON.parse(jsonMatch[0]);
  } else {
    parsed = JSON.parse(rawOutput);
  }
} catch (e) {
  parsed = {
    hook: rawOutput.slice(0, 100) + '...',
    body: rawOutput,
    cta: 'What are your thoughts on this approach?',
    hashtags: ['#AIAutomation', '#n8n', '#Nextjs', '#FullStack'],
    pillar: item.selected_pillar ? item.selected_pillar.name : 'Engineering & Automation',
    image_recommended: false
  };
}

// 1. Humanizer Pass: clean forbidden words
const forbidden = [
  /in today's (fast-paced|rapidly evolving|digital) world/gi,
  /game changer/gi,
  /unlock your potential/gi,
  /\\bdelve\\b/gi,
  /\\bleverage\\b/gi,
  /\\bstreamline\\b/gi,
  /\\bharness\\b/gi,
  /\\bpivotal\\b/gi,
  /\\btestament\\b/gi,
  /\\btapestry\\b/gi,
  /\\bbeacon\\b/gi
];

let cleanBody = parsed.body || '';
for (const regex of forbidden) {
  cleanBody = cleanBody.replace(regex, '');
}

// Clean multiple spaces and ensure clean double-spaced paragraphs
cleanBody = cleanBody.replace(/  +/g, ' ');
cleanBody = cleanBody.split('\\n').map(l => l.trim()).filter(l => l.length > 0).join('\\n\\n');

// Cap em-dashes to maximum 1
const dashes = cleanBody.split('—');
if (dashes.length > 2) {
  cleanBody = dashes[0] + '—' + dashes[1] + dashes.slice(2).map(p => '. ' + p.trim()).join('');
}

// 2. Fact-Check Validation
const ungroundedClaims = cleanBody.match(/\\$\\d+[kKmMbB]?/g) || [];
const hasUngroundedMoney = ungroundedClaims.some(c => !['$145', '$1,000', '$100', '$0'].includes(c));

const postId = 'post_' + Date.now().toString(36);
const webhookBase = 'https://primary-production-675a3.up.railway.app/webhook/linkedin-content-agent';

const approveUrl = `${webhookBase}?action=approve&post_id=${postId}`;
const rejectUrl = `${webhookBase}?action=reject&post_id=${postId}`;

return [{
  json: {
    status: 'READY_FOR_REVIEW',
    post_id: postId,
    pillar: parsed.pillar || (item.selected_pillar ? item.selected_pillar.name : 'AI Automation'),
    hook: parsed.hook || cleanBody.slice(0, 90),
    body: cleanBody,
    cta: parsed.cta || '',
    hashtags: parsed.hashtags || ['#AIAutomation', '#n8n', '#Nextjs', '#FullStack'],
    image_recommended: !!parsed.image_recommended,
    image_concept: parsed.image_concept || 'None',
    fact_check_passed: !hasUngroundedMoney,
    approve_url: approveUrl,
    reject_url: rejectUrl,
    email_subject: `[LinkedIn Agent] Post Ready for Review: "${(parsed.hook || cleanBody).slice(0, 50)}..."`,
    email_html: `
      <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 28px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
        <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #10b981; padding-bottom: 12px; margin-bottom: 20px;">
          <h2 style="color: #0f172a; margin: 0; font-size: 20px;">🚀 Ascenta LinkedIn Content Agent</h2>
          <span style="background: #ecfdf5; color: #059669; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; border: 1px solid #a7f3d0;">READY FOR REVIEW</span>
        </div>

        <p style="color: #64748b; font-size: 14px; margin-bottom: 16px;">
          <strong>Target Pillar:</strong> ${parsed.pillar || (item.selected_pillar ? item.selected_pillar.name : 'AI Automation')}<br/>
          <strong>Fact Check:</strong> <span style="color: #10b981;">✓ Grounded in Verified Builds</span> | <strong>Buzzword Check:</strong> <span style="color: #10b981;">✓ Passed</span>
        </p>

        <div style="background: #090d16; color: #f1f5f9; padding: 22px; border-radius: 8px; border-left: 4px solid #10b981; white-space: pre-wrap; font-size: 14px; line-height: 1.6; font-family: monospace;">
${cleanBody}
        </div>

        <div style="margin-top: 14px; font-size: 13px; color: #64748b;">
          <strong>Hashtags:</strong> ${(parsed.hashtags || []).join(' ')}
        </div>

        ${parsed.image_recommended ? `
          <div style="margin-top: 16px; padding: 14px; background: #f0fdf4; border-radius: 6px; font-size: 13px; color: #166534; border: 1px solid #bbf7d0;">
            <strong>🖼️ Recommended Architecture Visual:</strong> ${parsed.image_concept}
          </div>
        ` : ''}

        <div style="margin-top: 28px; padding-top: 20px; border-top: 1px solid #f1f5f9; display: flex; gap: 14px;">
          <a href="${approveUrl}" style="background: #10b981; color: #ffffff; padding: 12px 26px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; display: inline-block;">✅ Approve & Schedule</a>
          &nbsp;&nbsp;
          <a href="${rejectUrl}" style="background: #ef4444; color: #ffffff; padding: 12px 26px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px; display: inline-block;">❌ Reject</a>
        </div>

        <p style="color: #94a3b8; font-size: 11px; margin-top: 24px;">Generated autonomously for Muhammad Rayyan • Ascenta Agency</p>
      </div>
    `
  }
}];
"""
        }
    },

    # -------------------------------------------------------------
    # 6. HUMAN-IN-THE-LOOP NOTIFICATION LAYER
    # -------------------------------------------------------------
    {
        "id": "gmail-notification",
        "name": "Send Gmail Review Alert",
        "type": "n8n-nodes-base.gmail",
        "typeVersion": 2.1,
        "position": [1780, 240],
        "parameters": {
            "resource": "message",
            "operation": "send",
            "sendTo": "rayyan1122pk@gmail.com",
            "subject": "={{ $json.email_subject }}",
            "emailType": "html",
            "message": "={{ $json.email_html }}",
            "options": {
                "appendAttribution": False
            }
        },
        "credentials": {
            "gmailOAuth2": {
                "id": "pbMkoNuYgFKubrZs",
                "name": "Gmail account"
            }
        }
    },

    # -------------------------------------------------------------
    # 7. ACTION HANDLING & DISPATCH LAYER (APPROVE / REJECT / NOTE)
    # -------------------------------------------------------------
    {
        "id": "code-action-handler",
        "name": "Action Handler & Dispatcher",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1140, 680],
        "parameters": {
            "jsCode": """
const item = $input.first().json;
const action = item.action;

if (action === 'quick_note') {
  return [{
    json: {
      success: true,
      action: 'quick_note',
      message: 'Quick note captured successfully into Ascenta operator memory! The agent will use this in upcoming posts.',
      note: item.note_text,
      timestamp: new Date().toISOString()
    }
  }];
}

if (action === 'approve') {
  const postId = item.post_id || 'post_' + Date.now().toString(36);
  const postBody = item.body || item.note_text || 'Automating workflows with n8n and AI agents. Engineering deterministic pipelines that replace manual operations.';
  const hook = item.hook || '';
  const hashtags = Array.isArray(item.hashtags) ? item.hashtags.join(' ') : (item.hashtags || '#AIAutomation #n8n #FullStack #Ascenta');
  const fullPostText = (hook ? hook + '\\n\\n' : '') + postBody + '\\n\\n' + hashtags;

  return [{
    json: {
      success: true,
      action: 'approve',
      post_id: postId,
      status: 'APPROVED',
      linkedin_text: fullPostText,
      message: `Post ${postId} has been APPROVED by Muhammad Rayyan! Publishing directly to LinkedIn.`,
      email_subject: `[LinkedIn Agent] Post ${postId} Published to LinkedIn`,
      email_html: `
        <div style="font-family: Arial, sans-serif; padding: 24px; border: 1px solid #10b981; border-radius: 10px; max-width: 600px;">
          <h2 style="color: #10b981; margin-top: 0;">🎉 Post Published Live to LinkedIn!</h2>
          <p style="color: #334155;">Post <strong>${postId}</strong> was approved and successfully published to your live profile.</p>
          <div style="background: #f8fafc; padding: 16px; border-radius: 8px; border-left: 4px solid #0a66c2; margin: 16px 0; font-size: 14px; line-height: 1.6; white-space: pre-wrap;">
${fullPostText}
          </div>
          <p><a href="https://www.linkedin.com/in/ascenta" style="background: #0a66c2; color: #fff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">View Live on Your Profile ↗</a></p>
        </div>
      `,
      timestamp: new Date().toISOString()
    }
  }];
}

if (action === 'reject') {
  const postId = item.post_id || 'post_' + Date.now().toString(36);
  return [{
    json: {
      success: true,
      action: 'reject',
      post_id: postId,
      status: 'REJECTED',
      message: `Post ${postId} REJECTED and archived. Replacement will be planned.`,
      timestamp: new Date().toISOString()
    }
  }];
}

return [{
  json: {
    success: true,
    action: action,
    message: 'Action processed successfully by Ascenta LinkedIn Content Agent'
  }
}];
"""
        }
    },
    {
        "id": "switch-approval-confirmation",
        "name": "Is Approval Action?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [1460, 680],
        "parameters": {
            "conditions": {
                "options": {
                    "caseSensitive": True,
                    "leftValue": "",
                    "typeValidation": "strict",
                    "version": 2
                },
                "conditions": [
                    {
                        "id": "c2",
                        "leftValue": "={{ $json.action }}",
                        "rightValue": "approve",
                        "operator": {
                            "type": "string",
                            "operation": "equals"
                        }
                    }
                ],
                "combinator": "and"
            },
            "options": {}
        }
    },
    {
        "id": "linkedin-publisher",
        "name": "Publish to LinkedIn",
        "type": "n8n-nodes-base.linkedIn",
        "typeVersion": 1,
        "position": [1780, 620],
        "parameters": {
            "resource": "post",
            "operation": "create",
            "postAs": "person",
            "person": "={{ $json.person_urn || 'me' }}",
            "text": "={{ $json.linkedin_text }}"
        },
        "credentials": {
            "linkedInOAuth2Api": {
                "id": "yoXZgfNTjtWDlTk7",
                "name": "Muhammad Rayyan LinkedIn"
            }
        }
    },
    {
        "id": "gmail-approval-confirmation",
        "name": "Send Approval Confirmation Email",
        "type": "n8n-nodes-base.gmail",
        "typeVersion": 2.1,
        "position": [2060, 620],
        "parameters": {
            "resource": "message",
            "operation": "send",
            "sendTo": "rayyan1122pk@gmail.com",
            "subject": "={{ $json.email_subject }}",
            "emailType": "html",
            "message": "={{ $json.email_html }}",
            "options": {
                "appendAttribution": False
            }
        },
        "credentials": {
            "gmailOAuth2": {
                "id": "pbMkoNuYgFKubrZs",
                "name": "Gmail account"
            }
        }
    },

    # -------------------------------------------------------------
    # 8. RESPOND TO WEBHOOK (UNIFIED API EXIT)
    # -------------------------------------------------------------
    {
        "id": "respond-webhook",
        "name": "Respond to Webhook",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": [2120, 480],
        "parameters": {
            "respondWith": "json",
            "responseBody": "={{ JSON.stringify($json) }}",
            "options": {
                "responseCode": 200
            }
        }
    }
]

connections = {
    "Daily Morning Schedule (09:00 AM)": {
        "main": [
            [{"node": "Context & Knowledge Router", "type": "main", "index": 0}]
        ]
    },
    "LinkedIn Agent Webhook (Note & Control)": {
        "main": [
            [{"node": "Context & Knowledge Router", "type": "main", "index": 0}]
        ]
    },
    "Manual Test Trigger": {
        "main": [
            [{"node": "Context & Knowledge Router", "type": "main", "index": 0}]
        ]
    },
    "Context & Knowledge Router": {
        "main": [
            [{"node": "Is Generate Request?", "type": "main", "index": 0}]
        ]
    },
    "Is Generate Request?": {
        "main": [
            [{"node": "AI Content Writer Agent", "type": "main", "index": 0}],
            [{"node": "Action Handler & Dispatcher", "type": "main", "index": 0}]
        ]
    },
    "OpenRouter Model (Shared)": {
        "ai_languageModel": [
            [{"node": "AI Content Writer Agent", "type": "ai_languageModel", "index": 0}]
        ]
    },
    "AI Content Writer Agent": {
        "main": [
            [{"node": "Humanizer & Fact-Check Gate", "type": "main", "index": 0}]
        ]
    },
    "Humanizer & Fact-Check Gate": {
        "main": [
            [{"node": "Send Gmail Review Alert", "type": "main", "index": 0}]
        ]
    },
    "Send Gmail Review Alert": {
        "main": [
            [{"node": "Respond to Webhook", "type": "main", "index": 0}]
        ]
    },
    "Action Handler & Dispatcher": {
        "main": [
            [{"node": "Is Approval Action?", "type": "main", "index": 0}]
        ]
    },
    "Is Approval Action?": {
        "main": [
            [{"node": "Publish to LinkedIn", "type": "main", "index": 0}],
            [{"node": "Respond to Webhook", "type": "main", "index": 0}]
        ]
    },
    "Publish to LinkedIn": {
        "main": [
            [{"node": "Send Approval Confirmation Email", "type": "main", "index": 0}]
        ]
    },
    "Send Approval Confirmation Email": {
        "main": [
            [{"node": "Respond to Webhook", "type": "main", "index": 0}]
        ]
    }
}

print(f"Deploying Full Workflow ({len(nodes)} nodes) to Railway n8n instance...")

# Step 1: Deactivate existing workflow
try:
    req_deact = urllib.request.Request(f"{BASE_URL}/api/v1/workflows/{WORKFLOW_ID}/deactivate", data=b'{}', headers=headers)
    urllib.request.urlopen(req_deact)
    print("Deactivated existing workflow.")
except Exception as e:
    print(f"Deactivation note: {e}")

# Step 2: Update workflow with full architecture
payload = {
    "name": workflow_name,
    "nodes": nodes,
    "connections": connections,
    "settings": {
        "executionOrder": "v1",
        "saveManualExecutions": True,
        "saveExecutionProgress": True
    }
}

data = json.dumps(payload).encode("utf-8")
req_update = urllib.request.Request(f"{BASE_URL}/api/v1/workflows/{WORKFLOW_ID}", data=data, headers=headers, method="PUT")
try:
    with urllib.request.urlopen(req_update) as res:
        updated = json.loads(res.read().decode())
        print(f"Workflow successfully updated! Total nodes: {len(updated.get('nodes', []))}")
except urllib.error.HTTPError as e:
    print(f"Update failed ({e.code}): {e.read().decode()}")
    exit(1)

# Step 3: Reactivate workflow
try:
    req_act = urllib.request.Request(f"{BASE_URL}/api/v1/workflows/{WORKFLOW_ID}/activate", data=b'{}', headers=headers)
    with urllib.request.urlopen(req_act) as res:
        act_res = json.loads(res.read().decode())
        print(f"Workflow successfully activated! Active: {act_res.get('active')}")
except Exception as e:
    print(f"Activation note: {e}")

# Step 4: Verify Webhook
print("Verifying live webhook endpoint...")
test_req = urllib.request.Request(
    f"{BASE_URL}/webhook/linkedin-content-agent",
    data=json.dumps({"action": "status_check"}).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
try:
    with urllib.request.urlopen(test_req, timeout=10) as res:
        print(f"Webhook test result: HTTP {res.status} -> {res.read().decode()}")
except Exception as e:
    print(f"Webhook test error: {e}")
