## Importing libraries and files
import os
import re
from typing import Dict, Any, List
from dotenv import load_dotenv
from pypdf import PdfReader
from crewai.tools import BaseTool  
load_dotenv()

## custom pdf reader tool
class ReadFinancialDocumentTool(BaseTool):
    name: str = "read_financial_document"
    description: str = "Reads and extracts text from a financial PDF document"
    
    def _run(self, path: str = "data/sample.pdf") -> Dict[str, Any]:
        """Process the PDF document and extract text"""
        try:
            reader = PdfReader(path)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    return {
                        "success": False,
                        "error": "PDF is encrypted and cannot be read.",
                        "full_text": "",
                        "pages": [],
                        "total_pages": 0
                    }
            full_report = ""
            pages_data = []
            
            for i, page in enumerate(reader.pages, 1):
                try:
                    content = page.extract_text()
                except Exception:
                    content = None
                if content:
                    content = re.sub(r"\s{2,}", " ", content)
                    content = re.sub(r"\n{2,}", "\n", content)
                    full_report += content + "\n"
                    pages_data.append({
                        "page_number": i,
                        "content": content.strip()
                    })
            
            if not full_report.strip():
                return {
                    "success": True,
                    "error": "No extractable text found in the uploaded document.",
                    "full_text": "",
                    "pages": [],
                    "total_pages": len(reader.pages)
                }
            
            return {
                "success": True,
                "full_text": full_report.strip(),
                "pages": pages_data,
                "total_pages": len(reader.pages),
                "error": None
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF extraction failed: {str(e)}",
                "full_text": "",
                "pages": [],
                "total_pages": 0
            }
    
    async def _arun(self, path: str = "data/sample.pdf") -> Dict[str, Any]:
        return self._run(path)

## Creating Investment Analysis Tool
class AnalyzeInvestmentTool(BaseTool):
    name: str = "analyze_investment"
    description: str = "Analyzes financial document data for investment insights"
    
    def _extract_metrics(self, text: str) -> Dict[str, Any]:
        """Extract basic financial metrics using regex patterns"""
        metrics = {
            "revenue": None,
            "profit": None,
            "expenses": None,
            "growth": None
        }
        
        # Basic regex patterns for financial metrics
        patterns = {
            "revenue": r"revenue[s]?\s*(?:of|:)?\s*[\$£€]?([\d,]+(?:\.\d{2})?)\s*(?:million|billion)?",
            "profit": r"(?:net income|profit)[s]?\s*(?:of|:)?\s*[\$£€]?([\d,]+(?:\.\d{2})?)\s*(?:million|billion)?",
            "expenses": r"(?:expenses|costs)[s]?\s*(?:of|:)?\s*[\$£€]?([\d,]+(?:\.\d{2})?)\s*(?:million|billion)?",
            "growth": r"(?:growth|increase)[s]?\s*(?:of|:)?\s*([\d,]+(?:\.\d{2})?)\s*%"
        }
        
        for metric, pattern in patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                metrics[metric] = match.group(1)
        
        return metrics
    
    def _run(self, financial_document_data: str) -> Dict[str, Any]:
        if not financial_document_data:
            return {"error": "No financial data provided", "metrics": {}, "insights": []}
        
        processed_data = re.sub(r"\s{2,}", " ", financial_document_data)
        
        metrics = self._extract_metrics(processed_data)
        
        insights = []
        if metrics["revenue"]:
            insights.append(f"Detected revenue: ${metrics['revenue']}")
        if metrics["growth"]:
            insights.append(f"Growth rate: {metrics['growth']}%")
        
        return {
            "metrics": metrics,
            "insights": insights,
            "processed_text": processed_data.strip()
        }
    
    async def _arun(self, financial_document_data: str) -> Dict[str, Any]:
        return self._run(financial_document_data)

## Creating Risk Assessment Tool
class RiskAssessmentTool(BaseTool):
    name: str = "assess_risk"
    description: str = "Performs risk assessment on financial document data"
    
    def _identify_risk_factors(self, text: str) -> List[Dict[str, str]]:
        """Identify potential risk factors in the text"""
        risk_patterns = {
            "Litigation Risk": [r"litigation", r"lawsuit", r"legal proceeding"],
            "Financial Risk": [r"debt", r"default", r"bankruptcy", r"loss"],
            "Market Risk": [r"competition", r"market decline", r"market share"],
            "Operational Risk": [r"disruption", r"supply chain", r"operational"],
            "Regulatory Risk": [r"regulation", r"compliance", r"regulatory"]
        }
        
        risks = []
        for risk_type, patterns in risk_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text.lower())
                for match in matches:
                    risks.append({
                        "type": risk_type,
                        "factor": match.group(),
                        "context": text[max(0, match.start()-50):min(len(text), match.end()+50)].strip()
                    })
        
        return risks
    
    def _run(self, financial_document_data: str) -> Dict[str, Any]:
        if not financial_document_data:
            return {
                "error": "No data available for risk assessment",
                "risks": [],
                "risk_summary": {}
            }
        
        # Identify risks
        risks = self._identify_risk_factors(financial_document_data)
        
        # Summarize risks by type
        risk_summary = {}
        for risk in risks:
            risk_type = risk["type"]
            if risk_type not in risk_summary:
                risk_summary[risk_type] = 0
            risk_summary[risk_type] += 1
        
        return {
            "risks": risks,
            "risk_summary": risk_summary,
            "total_risks_identified": len(risks)
        }
    
    async def _arun(self, financial_document_data: str) -> Dict[str, Any]:
        return self._run(financial_document_data)

# tool instances
financial_document_tool = ReadFinancialDocumentTool()
investment_tool = AnalyzeInvestmentTool()
risk_tool = RiskAssessmentTool()