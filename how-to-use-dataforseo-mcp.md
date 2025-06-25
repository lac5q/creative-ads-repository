# 🎯 How to Use DataForSEO MCP in Cursor

## ✅ **Your Setup is CORRECT!**

You're not doing anything wrong. The DataForSEO MCP server is working perfectly when it says "waiting for requests" - that's exactly what it should do.

## 🔧 **How MCP Actually Works**

1. **MCP Server** = The DataForSEO service (running in background)
2. **MCP Client** = Cursor/Claude Desktop (connects to the server)
3. **You** = Send prompts to the client, which uses the server

## 🚀 **How to Use DataForSEO MCP in Cursor**

### Step 1: Restart Cursor
Since you updated the MCP configuration, restart Cursor completely:
1. Close Cursor
2. Reopen Cursor
3. Open this project

### Step 2: Test MCP Connection
In Cursor, try this prompt:

```
Using DataForSEO MCP, analyze the domain metrics for turnedyellow.com
```

### Step 3: If That Doesn't Work, Try These Prompts:

```
List available MCP tools
```

```
What MCP servers are available?
```

```
Use the dataforseo tool to get domain information for turnedyellow.com
```

## 🎯 **Ready-to-Use DataForSEO Prompts**

Once MCP is working, use these prompts:

### 1. Domain Analysis
```
Using DataForSEO MCP, analyze the domain authority and SEO metrics for turnedyellow.com
```

### 2. Keyword Research
```
Using DataForSEO MCP, find all keywords that turnedyellow.com currently ranks for
```

### 3. SERP Analysis
```
Using DataForSEO MCP, analyze SERP results for "custom simpsons portrait" and show where turnedyellow.com ranks
```

### 4. Competitor Analysis
```
Using DataForSEO MCP, identify the top 5 competitors for turnedyellow.com based on keyword overlap
```

### 5. Backlink Analysis
```
Using DataForSEO MCP, analyze the backlink profile for turnedyellow.com including referring domains and anchor text
```

## 🔍 **Troubleshooting**

### If MCP Doesn't Work in Cursor:

1. **Check Cursor Settings**
   - Go to Cursor Settings
   - Look for MCP or Model Context Protocol settings
   - Ensure it's enabled

2. **Check the Configuration**
   - Your `.cursor/mcp.json` is correct
   - Credentials are properly set

3. **Alternative: Use MCP Inspector**
   - Open: http://127.0.0.1:6274 (from your terminal output)
   - Add DataForSEO server manually
   - Test individual API calls

## 🎯 **What Should Happen**

When you use a DataForSEO prompt in Cursor:
1. Cursor connects to the DataForSEO MCP server
2. The server makes API calls to DataForSEO
3. Results are returned to you in Cursor
4. You get real SEO data for analysis

## 💡 **Pro Tips**

1. **Start Simple**: Begin with domain analysis
2. **Be Specific**: Mention "DataForSEO MCP" in your prompts
3. **Check Balance**: You have $1.00 - each API call costs a few cents
4. **Monitor Usage**: Check your DataForSEO dashboard for API usage

## 🚨 **Common Mistakes**

❌ **Don't do this**: Run `npx @skobyn/mcp-dataforseo` directly
✅ **Do this**: Use prompts in Cursor that reference DataForSEO MCP

❌ **Don't expect**: The MCP server to give you data directly
✅ **Do expect**: Cursor to use the MCP server when you ask

## 🎉 **Your Next Step**

**Try this exact prompt in Cursor right now:**

```
Using DataForSEO MCP, get basic domain information for turnedyellow.com including domain rank and organic traffic estimates
```

If it works, you'll see real DataForSEO API data!
If it doesn't work, we'll troubleshoot the Cursor MCP connection. 