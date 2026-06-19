import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import pdfParse from 'pdf-parse';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    if (!process.env.OPENAI_API_KEY) {
      // Return mock data if no API key is provided
      console.warn("No OPENAI_API_KEY found, returning mock analysis data.");
      await new Promise(resolve => setTimeout(resolve, 2000));
      return NextResponse.json({ id: '1' });
    }

    const arrayBuffer = await file.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    let extractedText = "";

    // 1. Extract text from the file (PDF handling)
    if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
      const pdfData = await pdfParse(buffer);
      extractedText = pdfData.text;
    } else {
      // For images, ideally we'd use vision models or tesseract, but for MVP we send image to Vision API if possible.
      // Since openai SDK allows image URLs, it's easier to handle text for now or mock it.
      return NextResponse.json({ error: 'Currently only PDF format is supported for automated extraction' }, { status: 400 });
    }

    // 2. Stage 1: Extraction via LLM (Replacing base44 ExtractDataFromUploadedFile)
    const extractionPrompt = `Extract the following information from the lab report text below. If a value is not found, leave it as null or "Unknown".

    Lab Report Text:
    ${extractedText.substring(0, 15000)}
    `;

    const extractionCompletion = await openai.chat.completions.create({
      model: "gpt-4o-mini", // Fast and efficient for data extraction
      messages: [
        { role: "system", content: "You are an expert data extractor parsing Certificates of Analysis (COAs) for hemp and CBD products." },
        { role: "user", content: extractionPrompt }
      ],
      response_format: {
        type: "json_schema",
        json_schema: {
          name: "lab_data_extraction",
          schema: {
            type: "object",
            properties: {
              product_name: { type: "string" },
              batch_number: { type: "string" },
              test_date: { type: "string" },
              lab_name: { type: "string" },
              product_type: { type: "string", description: "Type of product: topical, edible, flower, tincture, vape, etc." },
              thc_content: { type: "number", description: "Delta-9 THC percentage only (NOT THCA)" },
              thca_content: { type: "number", description: "THCA percentage" },
              delta_8_content: { type: "number", description: "Delta-8 THC percentage if present" },
              cbd_content: { type: "number" },
              pesticides_status: { type: "string", description: "Status of pesticides test: 'ND' (not detected), 'Pass', 'Fail', or list detected pesticides" },
              heavy_metals_status: { type: "string", description: "Status of heavy metals test: 'ND' (not detected), 'Pass', 'Fail', or list detected metals" },
              microbials_status: { type: "string", description: "Status of microbials test: 'ND' (not detected), 'Pass', 'Fail', or details" },
              residual_solvents_status: { type: "string", description: "Status of residual solvents test: 'ND' (not detected), 'Pass', 'Fail', or list detected solvents" },
              test_results_status: { type: "string", description: "Overall status from lab report (e.g., 'passed', 'tested', 'failed')" },
            },
            required: ["product_name", "test_date", "thc_content", "test_results_status"],
            additionalProperties: false,
          }
        }
      }
    });

    const extractedDataStr = extractionCompletion.choices[0].message.content;
    if (!extractedDataStr) throw new Error("Failed to extract data from OpenAI");

    const extractedData = JSON.parse(extractedDataStr);

    // Helper logic from base44
    const isTopical = extractedData.product_type?.toLowerCase().includes('topical') ||
                      extractedData.product_type?.toLowerCase().includes('cream') ||
                      extractedData.product_type?.toLowerCase().includes('lotion') ||
                      extractedData.product_type?.toLowerCase().includes('balm') ||
                      extractedData.product_type?.toLowerCase().includes('salve');

    // 3. Stage 2: Compliance Analysis via LLM (Replacing base44 InvokeLLM)
    const llmPrompt = `Analyze this hemp/CBD lab test data and provide a comprehensive assessment:

${JSON.stringify(extractedData, null, 2)}

Product Type: ${extractedData.product_type || 'Unknown'}
${isTopical ? 'NOTE: This is a TOPICAL product - residual solvents are acceptable and should NOT negatively impact the score.' : ''}

Test Status Notes:
- Pesticides: ${extractedData.pesticides_status || 'Unknown'} (ND = Not Detected)
- Heavy Metals: ${extractedData.heavy_metals_status || 'Unknown'} (ND = Not Detected)
- Microbials: ${extractedData.microbials_status || 'Unknown'} (ND = Not Detected)
- Residual Solvents: ${extractedData.residual_solvents_status || 'Unknown'} (ND = Not Detected)

CRITICAL TERMINOLOGY RULE: NEVER use the words "psychoactive" or "non-psychoactive" anywhere in your response. These terms are forbidden. Instead, when discussing THC effects, use terms like "active cannabinoid" or simply describe compliance levels.

IMPORTANT SCORING RULES:
1. If the lab report status shows "passed" or "tested", the score MUST BE 8 OR ABOVE (8, 9, or 10)
2. ONLY evaluate Delta-9 THC for federal compliance (must be <0.3% for federal compliance)
3. THCA and Delta-8 THC percentages should be recorded but NOT used for compliance scoring - they're informational only
4. If THC is <0.1%, consider it excellent for strictest state standards
5. ${isTopical ? 'FOR TOPICAL PRODUCTS: Residual solvents are acceptable and should NOT reduce the score' : 'Residual solvents should only negatively impact score if detected in non-topical products'}
6. "ND" means "Not Detected" which is EXCELLENT - this should positively impact the score

Scoring guidelines (Scale of 1-100, where 90-100 is excellent, 80-89 is good/passed, 60-79 is marginal, 1-59 is failing):
- 90-100: Lab report shows "passed" or "tested" AND Delta-9 THC <0.1% AND no contaminants detected (or residual solvents only if topical)
- 80-89: Lab report shows "passed" or "tested" AND Delta-9 THC <0.3% (federal compliance)
- 60-79: Meets federal guidelines (THC <0.3%) but lab report doesn't explicitly show "passed"
- 1-59: Does not meet federal standards (THC >0.3%) OR has safety concerns OR failed tests

IMPORTANT: Format the plain_english_summary as BULLET POINTS (use • or -) for easy scanning. Keep it concise and clear.
REMEMBER: NEVER use "psychoactive" or "non-psychoactive" - these words are strictly forbidden.

Provide a plain English summary in bullet point format covering:
• What the Delta-9 THC level means for legality and compliance
• What THCA and Delta-8 percentages indicate (if present)
• Whether this product meets federal and state requirements
• Any safety concerns from contaminants${isTopical ? '\n• Note that residual solvents are acceptable for topical products' : ''}
• Overall safety assessment

END THE SUMMARY WITH THIS EXACT FOOTNOTE ON A NEW LINE:
*Make sure that the COA matches the product name and labeling.`;

    const analysisCompletion = await openai.chat.completions.create({
      model: "gpt-4o",
      messages: [
        { role: "system", content: "You are a stringent compliance officer reviewing hemp product lab reports." },
        { role: "user", content: llmPrompt }
      ],
      response_format: {
        type: "json_schema",
        json_schema: {
          name: "compliance_analysis",
          schema: {
            type: "object",
            properties: {
              overall_score: { type: "number", description: "Score out of 100" },
              plain_english_summary: { type: "string", description: "Summary in bullet point format using bullet or dash characters. NEVER use psychoactive or non-psychoactive. Must end with the footnote about COA matching" },
              status: { type: "string", enum: ["Pass", "Fail"], description: "Overall pass or fail status" }
            },
            required: ["overall_score", "plain_english_summary", "status"],
            additionalProperties: false,
          }
        }
      }
    });

    const analysisDataStr = analysisCompletion.choices[0].message.content;
    if (!analysisDataStr) throw new Error("Failed to analyze data via OpenAI");

    const analysisResult = JSON.parse(analysisDataStr);

    // Combine extracted and analyzed data into our expected frontend format
    const finalResult = {
      productName: extractedData.product_name || "Unknown Product",
      labName: extractedData.lab_name || "Unknown Lab",
      date: extractedData.test_date || new Date().toLocaleDateString(),
      score: analysisResult.overall_score || 50,
      status: analysisResult.status || "Fail",
      summary: analysisResult.plain_english_summary || "",
      metrics: [
        { name: 'Potency (THC < 0.3%)', status: extractedData.thc_content < 0.3 ? 'Pass' : 'Fail', value: `${extractedData.thc_content || 0}%` },
        { name: 'Pesticides', status: extractedData.pesticides_status?.toLowerCase().includes('nd') ? 'Pass' : 'Warning', value: extractedData.pesticides_status || 'Unknown' },
        { name: 'Heavy Metals', status: extractedData.heavy_metals_status?.toLowerCase().includes('nd') ? 'Pass' : 'Warning', value: extractedData.heavy_metals_status || 'Unknown' },
        { name: 'Microbials', status: extractedData.microbials_status?.toLowerCase().includes('nd') ? 'Pass' : 'Warning', value: extractedData.microbials_status || 'Unknown' },
        { name: 'Residual Solvents', status: isTopical || extractedData.residual_solvents_status?.toLowerCase().includes('nd') ? 'Pass' : 'Warning', value: extractedData.residual_solvents_status || 'Unknown' },
      ]
    };

    return NextResponse.json({
      status: "success",
      data: finalResult
    });

  } catch (error: unknown) {
    console.error('Error processing upload:', error);
    const errorMessage = error instanceof Error ? error.message : 'Failed to process file';
    return NextResponse.json(
      { error: errorMessage },
      { status: 500 }
    );
  }
}
