import re

class QueryPlanner:
    """
    Classifies user questions and extracts parameters
    """
    
    def __init__(self):
        self.intent_patterns = {
            'revenue_vs_budget': [
                r'revenue.*budget',
                r'budget.*revenue',
                r'revenue.*vs',
                r'actual.*budget',
                r'compared to budget',
                r'vs\.?\s+budget',
                r'how did we do'
            ],
            'gross_margin_trend': [
                r'gross margin.*trend',
                r'margin.*trend',
                r'gross margin.*months',
                r'gm trend'
            ],
            'opex_breakdown': [
                r'opex.*breakdown',
                r'operating expense',
                r'break.*down.*opex',
                r'opex.*categor'
            ],
            'ebitda': [
                r'ebitda',
                r'profitability',
                r'earnings'
            ],
            'cash_runway': [
                r'cash runway',
                r'runway',
                r'how long.*cash',
                r'cash.*last'
            ]
        }
    
    def classify_intent(self, question):
       
        question_lower = question.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return intent
        
        return 'unknown'
    
    def extract_month(self, question):
        """
        Extracting month from question (e.g., 'June 2025' -> '2025-06')
        """
        # Month name to number mapping
        months = {
            'january': '01', 'jan': '01',
            'february': '02', 'feb': '02',
            'march': '03', 'mar': '03',
            'april': '04', 'apr': '04',
            'may': '05',
            'june': '06', 'jun': '06',
            'july': '07', 'jul': '07',
            'august': '08', 'aug': '08',
            'september': '09', 'sep': '09',
            'october': '10', 'oct': '10',
            'november': '11', 'nov': '11',
            'december': '12', 'dec': '12'
        }
        
        question_lower = question.lower()
        
       # "Month YYYY" pattern
        for month_name, month_num in months.items():
            pattern = rf'{month_name}\s+(\d{{4}})'
            match = re.search(pattern, question_lower)
            if match:
                year = match.group(1)
                return f'{year}-{month_num}'
        
        #  YYYY-MM pattern
        match = re.search(r'(\d{4})-(\d{2})', question)
        if match:
            return match.group(0)
        
        return None
    
    def extract_date_range(self, question):
        
        question_lower = question.lower()
        
     
        match = re.search(r'last\s+(\d+)\s+months?', question_lower)
        if match:
            num_months = int(match.group(1))
          
            return ('LAST_N_MONTHS', num_months)
        
   
        
        return None
    
    def parse_query(self, question):
      
        intent = self.classify_intent(question)
        month = self.extract_month(question)
        date_range = self.extract_date_range(question)
        
        return {
            'intent': intent,
            'month': month,
            'date_range': date_range,
            'original_question': question
        }