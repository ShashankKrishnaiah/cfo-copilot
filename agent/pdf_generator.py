import matplotlib
matplotlib.use('Agg')
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
import matplotlib.pyplot as plt
import io
from datetime import datetime

class PDFReportGenerator:
    def __init__(self, tools):
        self.tools = tools
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=12,
            spaceBefore=12
        )
    
    def generate_report(self, filename, month='2025-06'):
        """Generate a PDF report with key financial metrics"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("CFO Financial Report", self.title_style)
        story.append(title)
        
        subtitle = Paragraph(f"Report Date: {datetime.now().strftime('%B %d, %Y')}", self.styles['Normal'])
        story.append(subtitle)
        story.append(Spacer(1, 0.3*inch))
        
        # Page 1: Revenue vs Budget
        story.append(Paragraph("Revenue Performance", self.heading_style))
        revenue_data = self.tools.get_revenue_vs_budget(month)
        
        revenue_table_data = [
            ['Metric', 'Amount'],
            ['Actual Revenue', f"${revenue_data['actual']:,.0f}"],
            ['Budget', f"${revenue_data['budget']:,.0f}"],
            ['Variance', f"${revenue_data['variance']:,.0f}"],
            ['Variance %', f"{revenue_data['variance_pct']:.1f}%"]
        ]
        
        revenue_table = Table(revenue_table_data, colWidths=[3*inch, 2*inch])
        revenue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(revenue_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Add revenue chart
        rev_chart = self._create_revenue_chart(revenue_data, month)
        story.append(rev_chart)
        story.append(Spacer(1, 0.5*inch))
        
        # Page 2: Opex Breakdown
        story.append(PageBreak())
        story.append(Paragraph("Operating Expenses Breakdown", self.heading_style))
        
        opex_data = self.tools.get_opex_breakdown(month)
        
        opex_table_data = [['Category', 'Amount', '% of Total']]
        for _, row in opex_data.iterrows():
            opex_table_data.append([
                row['category'],
                f"${row['amount']:,.0f}",
                f"{row['pct_of_total']:.1f}%"
            ])
        
        opex_table_data.append([
            'Total Opex',
            f"${opex_data['amount'].sum():,.0f}",
            '100.0%'
        ])
        
        opex_table = Table(opex_table_data, colWidths=[2*inch, 2*inch, 1.5*inch])
        opex_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ca02c')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#d4edda')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(opex_table)
        story.append(Spacer(1, 0.3*inch))
        

        opex_chart = self._create_opex_chart(opex_data)
        story.append(opex_chart)
        
        
        story.append(PageBreak())
        story.append(Paragraph("Cash Position & Runway", self.heading_style))
        
        runway_data = self.tools.get_cash_runway()
        
        cash_table_data = [
            ['Metric', 'Value'],
            ['Current Cash', f"${runway_data['current_cash']:,.0f}"],
            ['As of Date', runway_data['latest_month']],
            ['Avg Monthly Burn', f"${runway_data['avg_monthly_burn']:,.0f}"],
        ]
        
        if runway_data['runway_months'] == float('inf'):
            cash_table_data.append(['Cash Runway', '∞ months (Profitable)'])
        else:
            cash_table_data.append(['Cash Runway', f"{runway_data['runway_months']:.1f} months"])
        
        cash_table = Table(cash_table_data, colWidths=[3*inch, 2*inch])
        cash_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f0e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(cash_table)
        
        
        doc.build(story)
        return filename
    
    def _create_revenue_chart(self, revenue_data, month):
        """Create revenue vs budget bar chart"""
        fig, ax = plt.subplots(figsize=(6, 4))
        
        categories = ['Actual', 'Budget']
        values = [revenue_data['actual'], revenue_data['budget']]
        colors_list = ['#1f77b4', '#ff7f0e']
        
        ax.bar(categories, values, color=colors_list)
        ax.set_ylabel('USD', fontsize=12)
        ax.set_title(f'Revenue vs Budget - {month}', fontsize=14, fontweight='bold')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x/1000:.0f}K'))
        
        plt.tight_layout()
        
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return Image(buf, width=5*inch, height=3.3*inch)
    
    def _create_opex_chart(self, opex_data):
        """Create opex breakdown pie chart"""
        fig, ax = plt.subplots(figsize=(6, 4))
        
        ax.pie(opex_data['amount'], labels=opex_data['category'], autopct='%1.1f%%',
               startangle=90, colors=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        ax.set_title('Operating Expenses Breakdown', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
      
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        return Image(buf, width=5*inch, height=3.3*inch)