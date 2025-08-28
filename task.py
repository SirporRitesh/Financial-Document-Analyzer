from crewai import Task
from agents import financial_analyst
from tools import financial_document_tool

# Define the Task object for financial analysis
analyze_financial_task = Task(
    description="""Analyze the provided financial document based on user query: {query}

Document Text:
{document_text}

Requirements:
1. Extract and analyze key financial metrics
2. Identify revenue, profit, and growth trends
3. Evaluate market position and competitive landscape
4. Assess potential risks and compliance issues
5. Provide evidence-based investment recommendations""",

    expected_output="""Structured analysis containing:
1. Executive Summary
   - Document overview
   - Key findings
2. Financial Analysis
   - Revenue and profit analysis
   - Growth metrics
   - Market position
3. Risk Assessment
   - Identified risks
   - Mitigation strategies
4. Investment Recommendations
   - Evidence-based suggestions
   - Key considerations""",

    agent=financial_analyst,
    tools=[financial_document_tool],
    async_execution=False
)