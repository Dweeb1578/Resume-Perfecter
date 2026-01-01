const { GoogleGenerativeAI } = require("@google/generative-ai");
require("dotenv").config({ path: "web/.env" });

const apiKey = process.env.GEMINI_API_KEY;
console.log("API Key present:", !!apiKey, "Length:", apiKey ? apiKey.length : 0);

async function testConfig() {
    if (!apiKey) {
        console.error("ERROR: No API Key found.");
        return;
    }

    try {
        const genAI = new GoogleGenerativeAI(apiKey);
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

        console.log("Testing Gemini 1.5 Flash...");
        const result = await model.generateContent("Hello, are you working?");
        console.log("Response:", result.response.text());
        console.log("SUCCESS: Gemini is reachable!");
    } catch (error) {
        console.error("FAILURE: Gemini Error:", error.message);
        if (error.response) console.error(JSON.stringify(error.response, null, 2));
    }
}

testConfig();
