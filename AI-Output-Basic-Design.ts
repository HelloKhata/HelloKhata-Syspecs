import { NextRequest } from "next/server";

// List of GET API endpoints with x-business-id header
const ERP_APIS: Record<string, string> = {
  sales: "http://127.0.0.1:3000/api/sales",
  expense: "http://127.0.0.1:3000/api/expenses",
  quotation: "http://127.0.0.1:3000/api/quotations",
  payments: "http://127.0.0.1:3000/api/payments",
  parties: "http://127.0.0.1:3000/api/parties",
  accounts: "http://127.0.0.1:3000/api/accounts",
  deadStock: "http://127.0.0.1:3000/api/inventory/dead-stock",
};

// Business ID for headers
// const BUSINESS_ID = "cmm1ro2us0005fbdsyrt6lrji";

// --- 1 Detect Category / Entity ---
function detectCategory(prompt: string) {
  const lower = prompt.toLowerCase();
  if (lower.includes("sale") || lower.includes("বিক্রি")) return "sales";
  if (lower.includes("expense") || lower.includes("খরচ")) return "expense";
  if (lower.includes("inventory") || lower.includes("স্টক")) return "deadStock";
  if (lower.includes("quotation") || lower.includes("কোটেশন"))
    return "quotation";
  if (lower.includes("payment") || lower.includes("পেমেন্ট")) return "payments";
  if (lower.includes("party") || lower.includes("পার্থি")) return "parties";
  if (lower.includes("account") || lower.includes("অ্যাকাউন্ট"))
    return "accounts";
  return "general";
}

// --- 2 Detect Action ---
function detectAction(prompt: string) {
  const lower = prompt.toLowerCase();
  // if (
  //   lower.includes("add") ||
  //   lower.includes("create") ||
  //   lower.includes("new") ||
  //   lower.includes("insert") ||
  //   lower.includes("নতুন")
  // )
  //   return "create";

  if (
    lower.includes("show") ||
    lower.includes("list") ||
    lower.includes("view") ||
    lower.includes("get") ||
    lower.includes("display") ||
    lower.includes("দেখান") ||
    lower.includes("বিস্তারিত")
  )
    return "read";

  // if (
  //   lower.includes("update") ||
  //   lower.includes("edit") ||
  //   lower.includes("change")
  // )
  //   return "update";

  // if (lower.includes("delete") || lower.includes("remove")) return "delete";

  return "read"; // default
}

// --- 3 Fetch ERP Data ---
async function fetchERPData(category: string, businessId?: string) {
  const apiUrl = ERP_APIS[category];
  if (!apiUrl) return null;
  console.log(
    `Fetching ERP data for category: ${category}, businessId: ${businessId}`,
  );
  const res = await fetch(apiUrl, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      "x-business-id": businessId || "", // <-- dynamic
    },
  });

  if (!res.ok) return null;
  return await res.json();
}

// --- 4 Build AI Prompt ---
function buildAIPrompt(category: string, data: any, userPrompt: string) {
  const dataPreview = data
    ? JSON.stringify(data, null, 2)
    : "No data available.";

  console.log("Data preview for AI prompt:", dataPreview);
  return `
You are an ERP AI assistant.

Here is the real ${category} data from the system:
${dataPreview}

User question:
${userPrompt}

Answer clearly, summarize if needed, and make it easy to understand.
`;
}

// --- 5 Chat API call ---type Extract<T, U> = T extends U ? T : never;
async function chatWithLlama(messages: { role: string; content: string }[]) {
  const res = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "llama3.1:8b",
      messages,
      stream: false,
    }),
  });

  if (!res.ok) throw new Error("Chat API failed");
  const data = await res.json();
  return data.message?.content || "No response from AI.";
}

// --- 6 Main API Handler ---
export async function POST(req: NextRequest) {
  try {
    const { prompt, history, businessId } = await req.json();

    const category = detectCategory(prompt);
    const action = detectAction(prompt);

    let enhancedPrompt = prompt;
    let erpData = null;

    if (action === "read" && category !== "general") {
      erpData = await fetchERPData(category, businessId);
      enhancedPrompt = buildAIPrompt(category, erpData, prompt);
    }

    const conversation: { role: string; content: string }[] = [
      { role: "system", content: "You are an ERP AI assistant." },
      ...(history || []),
      { role: "user", content: enhancedPrompt },
    ];

    const aiReply = await chatWithLlama(conversation);

    return new Response(aiReply, {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  } catch (err: any) {
    console.error("❌ AI API Error:", err);
    return new Response("AI request failed", { status: 500 });
  }
}
