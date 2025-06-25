#!/usr/bin/env node

/**
 * Direct DataForSEO API Analysis for turnedyellow.com
 * Comprehensive SEM analysis using DataForSEO REST API
 */

require('dotenv').config();
const https = require('https');

// DataForSEO API Configuration
const API_USERNAME = process.env.DATAFORSEO_USERNAME || 'luis@epiloguecapital.com';
const API_PASSWORD = process.env.DATAFORSEO_PASSWORD || '2e0edaebcc9b3756';
const API_BASE_URL = 'api.dataforseo.com';

// Analysis target
const TARGET_DOMAIN = 'turnedyellow.com';

console.log('🎯 DataForSEO Direct API Analysis for turnedyellow.com');
console.log('=====================================================\n');

// Helper function to make API requests
function makeAPIRequest(endpoint, postData = null) {
  return new Promise((resolve, reject) => {
    const auth = Buffer.from(`${API_USERNAME}:${API_PASSWORD}`).toString('base64');
    
    const options = {
      hostname: API_BASE_URL,
      path: endpoint,
      method: postData ? 'POST' : 'GET',
      headers: {
        'Authorization': `Basic ${auth}`,
        'Content-Type': 'application/json'
      }
    };

    if (postData) {
      options.headers['Content-Length'] = Buffer.byteLength(postData);
    }

    const req = https.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          resolve(jsonData);
        } catch (error) {
          reject(new Error(`Failed to parse JSON: ${error.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(error);
    });

    if (postData) {
      req.write(postData);
    }
    
    req.end();
  });
}

// Analysis functions
async function getDomainAnalytics() {
  console.log('📊 1. Domain Analytics Overview');
  console.log('--------------------------------');
  
  try {
    const postData = JSON.stringify([{
      "target": TARGET_DOMAIN,
      "location_name": "United States",
      "language_name": "English"
    }]);

    const result = await makeAPIRequest('/v3/domain_analytics/overview/live', postData);
    
    if (result.status_code === 20000 && result.tasks?.[0]?.result?.[0]) {
      const data = result.tasks[0].result[0];
      console.log(`✅ Domain: ${data.target}`);
      console.log(`📈 Organic Traffic: ${data.organic_etv || 'N/A'}`);
      console.log(`🔗 Organic Keywords: ${data.organic_count || 'N/A'}`);
      console.log(`💰 Paid Traffic: ${data.paid_etv || 'N/A'}`);
      console.log(`🎯 Paid Keywords: ${data.paid_count || 'N/A'}`);
      console.log(`📊 Domain Rank: ${data.rank || 'N/A'}`);
    } else {
      console.log('❌ No domain analytics data available');
    }
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }
  console.log('');
}

async function getOrganicKeywords() {
  console.log('🔑 2. Organic Keywords Analysis');
  console.log('--------------------------------');
  
  try {
    const postData = JSON.stringify([{
      "target": TARGET_DOMAIN,
      "location_name": "United States",
      "language_name": "English",
      "limit": 20,
      "order_by": ["search_volume,desc"]
    }]);

    const result = await makeAPIRequest('/v3/domain_analytics/keywords/live', postData);
    
    if (result.status_code === 20000 && result.tasks?.[0]?.result?.[0]?.items) {
      const keywords = result.tasks[0].result[0].items;
      console.log(`✅ Found ${keywords.length} top organic keywords:`);
      
      keywords.slice(0, 10).forEach((kw, index) => {
        console.log(`${index + 1}. "${kw.keyword}" - Position: ${kw.rank_group} - Volume: ${kw.search_volume || 'N/A'}`);
      });
    } else {
      console.log('❌ No organic keywords data available');
    }
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }
  console.log('');
}

async function getCompetitors() {
  console.log('🏆 3. Competitor Analysis');
  console.log('--------------------------');
  
  try {
    const postData = JSON.stringify([{
      "target": TARGET_DOMAIN,
      "location_name": "United States",
      "language_name": "English",
      "limit": 10
    }]);

    const result = await makeAPIRequest('/v3/domain_analytics/competitors/live', postData);
    
    if (result.status_code === 20000 && result.tasks?.[0]?.result?.[0]?.items) {
      const competitors = result.tasks[0].result[0].items;
      console.log(`✅ Found ${competitors.length} main competitors:`);
      
      competitors.forEach((comp, index) => {
        console.log(`${index + 1}. ${comp.domain} - Similarity: ${(comp.avg_position * 100).toFixed(1)}%`);
      });
    } else {
      console.log('❌ No competitor data available');
    }
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }
  console.log('');
}

async function getBacklinks() {
  console.log('🔗 4. Backlink Profile Analysis');
  console.log('--------------------------------');
  
  try {
    const postData = JSON.stringify([{
      "target": TARGET_DOMAIN,
      "limit": 20,
      "order_by": ["rank,desc"]
    }]);

    const result = await makeAPIRequest('/v3/backlinks/summary/live', postData);
    
    if (result.status_code === 20000 && result.tasks?.[0]?.result?.[0]) {
      const data = result.tasks[0].result[0];
      console.log(`✅ Backlink Summary:`);
      console.log(`🔗 Total Backlinks: ${data.backlinks || 'N/A'}`);
      console.log(`🌐 Referring Domains: ${data.referring_domains || 'N/A'}`);
      console.log(`📊 Domain Rank: ${data.rank || 'N/A'}`);
      console.log(`🎯 Referring IPs: ${data.referring_ips || 'N/A'}`);
    } else {
      console.log('❌ No backlink data available');
    }
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }
  console.log('');
}

async function getSERPAnalysis() {
  console.log('📈 5. SERP Analysis for Key Terms');
  console.log('----------------------------------');
  
  const keywords = [
    'turn me yellow',
    'custom simpsons portrait',
    'simpsons style drawing',
    'custom cartoon portrait'
  ];

  for (const keyword of keywords) {
    try {
      console.log(`\n🔍 Analyzing: "${keyword}"`);
      
      const postData = JSON.stringify([{
        "keyword": keyword,
        "location_name": "United States",
        "language_name": "English",
        "device": "desktop",
        "os": "windows"
      }]);

      const result = await makeAPIRequest('/v3/serp/google/organic/live/advanced', postData);
      
      if (result.status_code === 20000 && result.tasks?.[0]?.result?.[0]?.items) {
        const items = result.tasks[0].result[0].items;
        const turnedYellowResult = items.find(item => 
          item.domain && item.domain.includes('turnedyellow.com')
        );
        
        if (turnedYellowResult) {
          console.log(`✅ turnedyellow.com found at position ${turnedYellowResult.rank_group}`);
          console.log(`   URL: ${turnedYellowResult.url}`);
          console.log(`   Title: ${turnedYellowResult.title?.substring(0, 60)}...`);
        } else {
          console.log(`❌ turnedyellow.com not found in top 100 results`);
        }
        
        // Show top 3 competitors
        console.log(`   Top 3 results:`);
        items.slice(0, 3).forEach((item, index) => {
          if (item.type === 'organic') {
            console.log(`   ${index + 1}. ${item.domain} - ${item.title?.substring(0, 40)}...`);
          }
        });
      }
    } catch (error) {
      console.log(`❌ Error analyzing "${keyword}": ${error.message}`);
    }
  }
  console.log('');
}

async function getKeywordSuggestions() {
  console.log('💡 6. Keyword Opportunities');
  console.log('----------------------------');
  
  try {
    const postData = JSON.stringify([{
      "keyword": "custom simpsons portrait",
      "location_name": "United States",
      "language_name": "English",
      "limit": 20
    }]);

    const result = await makeAPIRequest('/v3/keywords_data/google_ads/suggestions/live', postData);
    
    if (result.status_code === 20000 && result.tasks?.[0]?.result?.[0]?.items) {
      const suggestions = result.tasks[0].result[0].items;
      console.log(`✅ Found ${suggestions.length} keyword opportunities:`);
      
      suggestions.slice(0, 10).forEach((kw, index) => {
        console.log(`${index + 1}. "${kw.keyword}" - Volume: ${kw.search_volume || 'N/A'} - CPC: $${kw.cpc || 'N/A'}`);
      });
    } else {
      console.log('❌ No keyword suggestions available');
    }
  } catch (error) {
    console.log(`❌ Error: ${error.message}`);
  }
  console.log('');
}

// Main analysis function
async function runCompleteAnalysis() {
  console.log(`🚀 Starting comprehensive SEM analysis for ${TARGET_DOMAIN}...\n`);
  
  // Check credentials
  if (!API_USERNAME || !API_PASSWORD) {
    console.log('❌ Error: DataForSEO credentials not found!');
    console.log('Make sure your .env file contains:');
    console.log('DATAFORSEO_USERNAME=luis@epiloguecapital.com');
    console.log('DATAFORSEO_PASSWORD=2e0edaebcc9b3756');
    return;
  }

  console.log(`📋 Using credentials: ${API_USERNAME}`);
  console.log(`🎯 Target domain: ${TARGET_DOMAIN}\n`);

  try {
    // Run all analyses
    await getDomainAnalytics();
    await getOrganicKeywords();
    await getCompetitors();
    await getBacklinks();
    await getSERPAnalysis();
    await getKeywordSuggestions();

    console.log('🎉 Analysis Complete!');
    console.log('=====================');
    console.log('');
    console.log('📊 Summary Report Generated');
    console.log('💡 Check your DataForSEO dashboard for API usage');
    console.log('🔄 Run this script anytime for updated data');
    
  } catch (error) {
    console.log(`❌ Analysis failed: ${error.message}`);
  }
}

// Export for use as module or run directly
if (require.main === module) {
  runCompleteAnalysis();
}

module.exports = {
  runCompleteAnalysis,
  getDomainAnalytics,
  getOrganicKeywords,
  getCompetitors,
  getBacklinks,
  getSERPAnalysis,
  getKeywordSuggestions
}; 