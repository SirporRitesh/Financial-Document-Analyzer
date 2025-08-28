import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import Agent
from tools import ReadFinancialDocumentTool, AnalyzeInvestmentTool, RiskAssessmentTool
from langchain_google_genai import ChatGoogleGenerativeAI
from google import genai
from google.genai import types
from litellm import completion

load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,
    google_api_key=os.environ['GEMINI_API_KEY']
)

# Initialize tool instances
financial_document_tool = ReadFinancialDocumentTool()
investment_tool = AnalyzeInvestmentTool()
risk_tool = RiskAssessmentTool()

# Financial Analyst Agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Analyze financial documents and provide evidence-based investment insights",
    verbose=True,
    backstory="Experienced financial analyst with expertise in document analysis, "
              "market research, and investment strategy.",
    tools=[financial_document_tool],
    llm=llm
)

# Document Verifier Agent
verifier = Agent(
    role="Financial Document Verifier",
    goal="Verify document authenticity and completeness per regulatory standards",
    verbose=True,
    backstory="Certified financial document specialist with expertise in compliance "
              "and verification procedures.",
    tools=[financial_document_tool],
    llm=llm
)

# Investment Advisor Agent
investment_advisor = Agent(
    role="Investment Advisor",
    goal="Provide compliant, evidence-based investment recommendations",
    verbose=True,
    backstory="Certified financial advisor with expertise in portfolio management "
              "and risk assessment.",
    tools=[financial_document_tool, investment_tool],
    llm=llm
)

# Risk Assessor Agent
risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal="Conduct thorough risk analysis based on financial data",
    verbose=True,
    backstory="Expert in financial risk assessment with focus on quantitative "
              "analysis and regulatory compliance.",
    tools=[financial_document_tool, risk_tool],
    llm=llm
)

