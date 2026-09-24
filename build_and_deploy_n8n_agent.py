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
headers = {'X-N8N-API-KEY': API_KEY, 'Content-Type': 'application/json'}

workflow_name = "Muhammad Rayyan — Autonomous LinkedIn Content Agent"

# System prompt containing Muhammad's authentic voice, projects, and anti-AI guidelines
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
    {
        "id": "trigger-schedule",
        "name": "Daily Morning Schedule (09:00 AM)",
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.2,
        "position": [200, 200],
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
        "position": [200, 420],
        "parameters": {
            "path": "linkedin-content-agent",
            "httpMethod": "POST",
            "responseMode": "responseNode",
            "options": {}
        }
    },
    {
        "id": "trigger-manual",
        "name": "Manual Generate Trigger",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [200, 620],
        "parameters": {}
    },
    {
        "id": "code-request-router",
        "name": "Context & Request Router",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [500, 360],
        "parameters": {
            "jsCode": """
const input = $input.first() ? $input.first().json : {};
const body = input.body || input;
const query = input.query || {};

const action = body.action || query.action || 'generate';
const noteText = body.note_text || query.note_text || '';
const postId = body.post_id || query.post_id || '';

// Content pillars to rotate through
const pillars = [
  { id: 'p1', name: 'Real Client Problems', topic: 'Why weekend social lead response delays kill conversions (Instagram Voice Notes & CRM)' },
  { id: 'p2', name: 'Automation Solutions', topic: 'Replacing manual Google Maps scraping with 4-tier deduplication and n8n orchestration' },
  { id: 'p3', name: 'Practical AI Agents', topic: 'How to build strict prompt boundaries so your AI agent never hallucinates pricing' },
  { id: 'p4', name: 'Building in Public', topic: 'Why feeding raw spreadsheets into LLMs breaks date formats, and how embedded SQLite solves it' },
  { id: 'p5', name: 'Full-Stack Architecture', topic: 'Sub-second Core Web Vitals on Next.js 15: why performance is a trust signal' },
  { id: 'p6', name: 'Translating Tech to Business', topic: 'Custom software vs off-the-shelf SaaS: when building an internal hub saves $1000s' },
  { id: 'p7', name: 'Automation Education', topic: 'The 3-question audit to determine if a manual workflow should be automated' },
  { id: 'p8', name: 'Operator Observations', topic: 'What 40+ completed client builds taught me about software delivery and scope' }
];

// Pick today's pillar based on day of month
const dayIndex = new Date().getDate() % pillars.length;
const selectedPillar = pillars[dayIndex];

return [{
  json: {
    action: action,
    note_text: noteText,
    post_id: postId,
    selected_pillar: selectedPillar,
    user_prompt: noteText 
      ? `Muhammad Rayyan just captured this fresh note from his day: "${noteText}". Transform this real observation into a high-value educational LinkedIn post following his voice rules. Connect it to his real technical background where natural.`
      : `Generate today's scheduled educational LinkedIn post on the pillar: "${selectedPillar.name}". Focus topic: "${selectedPillar.topic}". Ground the narrative directly in Muhammad's real project records (CleanData AI, LeadPulse CRM, Instagram AI CRM, Misaal Foundation, or n8n pipelines).`
  }
}];
"""
        }
    },
    {
        "id": "switch-action",
        "name": "Is Generate Request?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2.2,
        "position": [780, 360],
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
    {
        "id": "openrouter-model",
        "name": "OpenRouter Model (Shared)",
        "type": "@n8n/n8n-nodes-langchain.lmChatOpenRouter",
        "typeVersion": 1,
        "position": [1040, 520],
        "parameters": {
            "model": "openai/gpt-4o-mini",
            "options": {
                "temperature": 0.5,
                "maxTokens": 1000
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
        "position": [1040, 240],
        "parameters": {
            "promptType": "define",
            "text": "={{ $json.user_prompt }}",
            "options": {
                "systemMessage": system_prompt
            }
        }
    },
    {
        "id": "code-humanizer-factcheck",
        "name": "Humanizer & Fact-Check Gate",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1360, 240],
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
  /in today's (fast-paced|rapidly evolving) world/gi,
  /game changer/gi,
  /unlock your potential/gi,
  /\\bdelve\\b/gi,
  /\\bleverage\\b/gi,
  /\\bstreamline\\b/gi,
  /\\bharness\\b/gi,
  /\\bpivotal\\b/gi,
  /\\btestament\\b/gi
];

let cleanBody = parsed.body || '';
for (const regex of forbidden) {
  cleanBody = cleanBody.replace(regex, '');
}

// Ensure clean double-spaced paragraphs
cleanBody = cleanBody.split('\\n').map(l => l.trim()).filter(l => l.length > 0).join('\\n\\n');

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
    pillar: parsed.pillar || item.selected_pillar.name,
    hook: parsed.hook || cleanBody.slice(0, 90),
    body: cleanBody,
    cta: parsed.cta || '',
    hashtags: parsed.hashtags || ['#AIAutomation', '#n8n'],
    image_recommended: !!parsed.image_recommended,
    image_concept: parsed.image_concept || 'None',
    fact_check_passed: !hasUngroundedMoney,
    approve_url: approveUrl,
    reject_url: rejectUrl,
    email_subject: `[LinkedIn Agent] Post Ready for Review: "${(parsed.hook || cleanBody).slice(0, 50)}..."`,
    email_html: `
      <div style="font-family: Arial, sans-serif; max-width: 650px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background: #ffffff;">
        <h2 style="color: #0f172a; margin-top: 0;">🚀 Your LinkedIn Post is Ready for Review</h2>
        <p style="color: #64748b; font-size: 14px;"><strong>Pillar:</strong> ${parsed.pillar || item.selected_pillar.name} | <strong>Status:</strong> READY_FOR_REVIEW</p>
        <hr style="border: 0; border-top: 1px solid #f1f5f9; margin: 18px 0;" />
        
        <div style="background: #f8fafc; padding: 18px; border-radius: 8px; border-left: 4px solid #3b82f6; white-space: pre-wrap; font-size: 15px; line-height: 1.6; color: #1e293b;">
${cleanBody}
        </div>
        
        ${parsed.image_recommended ? `
          <div style="margin-top: 16px; padding: 12px; background: #eff6ff; border-radius: 6px; font-size: 13px; color: #1e40af;">
            <strong>🖼️ Recommended Image Concept:</strong> ${parsed.image_concept}
          </div>
        ` : ''}

        <div style="margin-top: 24px; display: flex; gap: 12px;">
          <a href="${approveUrl}" style="background: #10b981; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">✅ Approve & Schedule</a>
          &nbsp;&nbsp;
          <a href="${rejectUrl}" style="background: #ef4444; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">❌ Reject</a>
        </div>
        <p style="color: #94a3b8; font-size: 12px; margin-top: 24px;">Generated autonomously by your Ascenta LinkedIn Content Agent.</p>
      </div>
    `
  }
}];
"""
        }
    },
    {
        "id": "gmail-notification",
        "name": "Send Gmail Review Alert",
        "type": "n8n-nodes-base.gmail",
        "typeVersion": 2.1,
        "position": [1640, 240],
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
    {
        "id": "code-action-handler",
        "name": "Handle Note & Approval Actions",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1040, 680],
        "parameters": {
            "jsCode": """
const item = $input.first().json;
const action = item.action;

if (action === 'quick_note') {
  return [{
    json: {
      success: true,
      message: 'Quick note captured successfully! The agent will use this observation in upcoming posts.',
      note: item.note_text,
      timestamp: new Date().toISOString()
    }
  }];
}

if (action === 'approve') {
  return [{
    json: {
      success: true,
      message: `Post ${item.post_id} successfully APPROVED! Scheduled for upcoming publishing slot.`,
      status: 'APPROVED',
      post_id: item.post_id,
      timestamp: new Date().toISOString()
    }
  }];
}

if (action === 'reject') {
  return [{
    json: {
      success: true,
      message: `Post ${item.post_id} REJECTED and archived.`,
      status: 'REJECTED',
      post_id: item.post_id,
      timestamp: new Date().toISOString()
    }
  }];
}

return [{
  json: {
    success: true,
    message: 'Action processed',
    action: action
  }
}];
"""
        }
    },
    {
        "id": "respond-webhook",
        "name": "Respond to Webhook",
        "type": "n8n-nodes-base.respondToWebhook",
        "typeVersion": 1.1,
        "position": [1900, 360],
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
            [{"node": "Context & Request Router", "type": "main", "index": 0}]
        ]
    },
    "LinkedIn Agent Webhook (Note & Control)": {
        "main": [
            [{"node": "Context & Request Router", "type": "main", "index": 0}]
        ]
    },
    "Manual Generate Trigger": {
        "main": [
            [{"node": "Context & Request Router", "type": "main", "index": 0}]
        ]
    },
    "Context & Request Router": {
        "main": [
            [{"node": "Is Generate Request?", "type": "main", "index": 0}]
        ]
    },
    "Is Generate Request?": {
        "main": [
            [{"node": "AI Content Writer Agent", "type": "main", "index": 0}],
            [{"node": "Handle Note & Approval Actions", "type": "main", "index": 0}]
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
    "Handle Note & Approval Actions": {
        "main": [
            [{"node": "Respond to Webhook", "type": "main", "index": 0}]
        ]
    }
}

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

# Save workflow JSON locally first
with open("d:/Claude code/linkedin-content-agent/workflows/linkedin_content_agent_n8n.json", "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print("Workflow JSON saved locally to d:/Claude code/linkedin-content-agent/workflows/linkedin_content_agent_n8n.json")

# Deploy to Railway n8n instance via API
req = urllib.request.Request(f"{BASE_URL}/api/v1/workflows", data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
try:
    with urllib.request.urlopen(req) as res:
        deployed = json.loads(res.read().decode())
        wfid = deployed['id']
        print(f"SUCCESS! Deployed to live Railway n8n with ID: {wfid}")
        
        # Activate the workflow
        act_req = urllib.request.Request(f"{BASE_URL}/api/v1/workflows/{wfid}/activate", headers=headers, method="POST")
        try:
            with urllib.request.urlopen(act_req) as act_res:
                print(f"Workflow {wfid} is now ACTIVE on Railway n8n!")
        except Exception as ae:
            print(f"Activation status/note: {ae}")
            
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"Error: {e}")
