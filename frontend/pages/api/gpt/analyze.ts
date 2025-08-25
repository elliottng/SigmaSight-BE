import type { NextApiRequest, NextApiResponse } from 'next';

const DEMO_RESPONSES = [
  "Based on your portfolio analysis, I can see you have a well-diversified mix of assets. Your risk-adjusted returns look strong, but I'd recommend considering some defensive positions given current market volatility.",
  "Looking at your factor exposures, you have significant exposure to growth factors. This could be beneficial in a bull market, but consider adding some value exposure to balance your risk profile.",
  "Your portfolio shows good diversification across sectors. The technology allocation seems appropriate given current trends, but watch for concentration risk if tech continues to outperform.",
  "I notice your portfolio has low correlation with traditional risk factors. This suggests good diversification, but make sure you're not missing out on systematic risk premiums.",
  "Your Greek exposures indicate you're positioned for moderate market moves. Consider adding some volatility protection if you expect increased market turbulence."
];

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  console.log('API called with method:', req.method);
  
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const { message } = req.body;
    console.log('Received message:', message);

    if (!message) {
      return res.status(400).json({ error: 'Message is required' });
    }

    // Try direct OpenAI API call with portfolio context
    try {
      console.log('Fetching portfolio data from backend...');
      
      // Fetch portfolio data from backend
      let portfolioContext = '';
      try {
        // Get a demo portfolio for analysis
        const portfolioId = 'a3209353-9ed5-4885-81e8-d4bbc995f96c'; // Demo Individual
        const portfolioResponse = await fetch(`http://localhost:8000/api/v1/reports/portfolio/${portfolioId}/content/json`);
        
        if (portfolioResponse.ok) {
          const portfolioData = await portfolioResponse.json();
          portfolioContext = `
PORTFOLIO ANALYSIS CONTEXT:
Portfolio Name: ${portfolioData.content?.portfolio_name || 'Individual Portfolio'}
Total Value: $${portfolioData.content?.total_value?.toLocaleString() || 'N/A'}
Long Exposure: $${portfolioData.content?.long_exposure?.toLocaleString() || 'N/A'}
Short Exposure: $${portfolioData.content?.short_exposure?.toLocaleString() || 'N/A'}
Net Exposure: ${portfolioData.content?.net_exposure_percent?.toFixed(2) || 'N/A'}%

TOP POSITIONS:
${portfolioData.content?.top_positions?.slice(0, 5).map((pos: any, idx: number) => 
  `${idx + 1}. ${pos.symbol}: $${pos.market_value?.toLocaleString() || 'N/A'} (${pos.weight_percent?.toFixed(2) || 'N/A'}%)`
).join('\n') || 'No positions available'}

RISK METRICS:
Portfolio Beta: ${portfolioData.content?.portfolio_beta?.toFixed(2) || 'N/A'}
VaR (1-day): ${portfolioData.content?.var_1d_percent?.toFixed(2) || 'N/A'}%
Volatility (Annualized): ${portfolioData.content?.volatility_annualized?.toFixed(2) || 'N/A'}%

USER QUESTION: ${message}
`;
          console.log('Portfolio data fetched successfully');
        } else {
          console.log('Portfolio data not available, using general context');
          portfolioContext = `USER QUESTION ABOUT PORTFOLIO MANAGEMENT: ${message}`;
        }
      } catch (portfolioError) {
        console.log('Error fetching portfolio data:', portfolioError);
        portfolioContext = `USER QUESTION ABOUT PORTFOLIO MANAGEMENT: ${message}`;
      }
      
      console.log('Calling OpenAI API with portfolio context...');
      
      const openaiResponse = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.OPENAI_API_KEY}`
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: [
            {
              role: 'system',
              content: 'You are a sophisticated portfolio risk management assistant for SigmaSight. Provide helpful, actionable insights about portfolio analysis, risk management, factor exposures, and investment strategies. Keep responses concise but informative, and focus on practical advice for portfolio managers.'
            },
            {
              role: 'user',
              content: portfolioContext || message
            }
          ],
          max_tokens: 400,
          temperature: 0.7
        })
      });

      if (openaiResponse.ok) {
        const data = await openaiResponse.json();
        const aiResponse = data.choices?.[0]?.message?.content || "I'm sorry, I couldn't generate a response.";
        
        console.log('Got response from OpenAI API successfully');
        return res.status(200).json({ 
          response: aiResponse + " 🤖"
        });
      } else {
        const errorData = await openaiResponse.json();
        console.log('OpenAI API error:', openaiResponse.status, errorData);
        throw new Error(`OpenAI API error: ${openaiResponse.status}`);
      }
    } catch (openaiError) {
      console.log('OpenAI API failed:', openaiError.message);
    }

    // Fallback to intelligent demo responses
    const randomResponse = DEMO_RESPONSES[Math.floor(Math.random() * DEMO_RESPONSES.length)];
    
    // Add some context based on the user's message
    let contextualResponse = randomResponse;
    if (message.toLowerCase().includes('risk')) {
      contextualResponse = "Based on your query about risk, " + contextualResponse.toLowerCase();
    } else if (message.toLowerCase().includes('portfolio')) {
      contextualResponse = "Regarding your portfolio question: " + contextualResponse;
    } else if (message.toLowerCase().includes('market')) {
      contextualResponse = "Given current market conditions, " + contextualResponse.toLowerCase();
    }

    console.log('Sending demo response:', contextualResponse);
    
    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000));

    return res.status(200).json({ 
      response: contextualResponse + " (This is a demo response - GPT agent backend will be connected soon!)"
    });

  } catch (error) {
    console.error('Analysis error:', error);
    return res.status(500).json({ 
      error: 'Analysis failed',
      details: error instanceof Error ? error.message : 'Unknown error'
    });
  }
}