import json
from typing import Dict
from datetime import datetime
import os

class ReportFormatter:
    def __init__(self, report_data: Dict):
        self.data = report_data
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    def generate_html_report(self) -> str:
        """Generate an HTML report from the analysis data"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Website Analysis Report - {self.data['timestamp']}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
                .summary-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
                .score {{ font-size: 24px; font-weight: bold; margin: 10px 0; }}
                .good {{ color: #28a745; }}
                .average {{ color: #ffc107; }}
                .poor {{ color: #dc3545; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f8f9fa; }}
                .metric-details {{ margin-top: 10px; font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Website Analysis Report</h1>
                    <p>Generated on {self.data['timestamp']}</p>
                    <p>Analysis completed in {self.data['analysis_time']}</p>
                </div>

                <div class="summary">
                    <div class="summary-card">
                        <h3>Sites Analyzed</h3>
                        <div class="score">{self.data['successful_analyses']} / {self.data['total_sites']}</div>
                    </div>
                    {self._generate_score_cards()}
                </div>

                <h2>Detailed Results</h2>
                <table>
                    <tr>
                        <th>Website</th>
                        <th>Performance</th>
                        <th>Design</th>
                        <th>SEO</th>
                        <th>Accessibility</th>
                        <th>Overall</th>
                    </tr>
                    {self._generate_results_table()}
                </table>

                {self._generate_recommendations()}
            </div>
        </body>
        </html>
        """
        return html

    def _generate_score_cards(self) -> str:
        cards = ""
        for metric, score in self.data['average_scores'].items():
            score_class = self._get_score_class(score)
            metric_name = metric.replace('_', ' ').title()
            cards += f"""
                <div class="summary-card">
                    <h3>{metric_name}</h3>
                    <div class="score {score_class}">{score:.1f}/10</div>
                </div>
            """
        return cards

    def _generate_results_table(self) -> str:
        rows = ""
        for result in self.data['detailed_results']:
            if result['success']:
                scores = result['scores']
                rows += f"""
                    <tr>
                        <td>{result['url']}</td>
                        <td class="{self._get_score_class(scores['performance_score'])}">{scores['performance_score']:.1f}</td>
                        <td class="{self._get_score_class(scores['design_score'])}">{scores['design_score']:.1f}</td>
                        <td class="{self._get_score_class(scores['seo_score'])}">{scores['seo_score']:.1f}</td>
                        <td class="{self._get_score_class(scores['accessibility_score'])}">{scores['accessibility_score']:.1f}</td>
                        <td class="{self._get_score_class(scores['overall_score'])}">{scores['overall_score']:.1f}</td>
                    </tr>
                    <tr>
                        <td colspan="6" class="metric-details">
                            <strong>Performance Metrics:</strong> {self._format_metrics(result['metrics']['performance'])}<br>
                            <strong>Design Metrics:</strong> {self._format_metrics(result['metrics']['design'])}<br>
                            <strong>SEO Metrics:</strong> {self._format_metrics(result['metrics']['seo'])}<br>
                            <strong>Accessibility Metrics:</strong> {self._format_metrics(result['metrics']['accessibility'])}
                        </td>
                    </tr>
                """
        return rows

    def _generate_recommendations(self) -> str:
        if not self.data['needs_improvement']:
            return ""
        
        recommendations = "<h2>Recommendations</h2>"
        for site in self.data['needs_improvement']:
            scores = site['scores']
            metrics = site['metrics']
            recommendations += f"""
                <div style="margin-bottom: 20px;">
                    <h3>{site['url']}</h3>
                    <ul>
                    {self._generate_site_recommendations(scores, metrics)}
                    </ul>
                </div>
            """
        return recommendations

    def _generate_site_recommendations(self, scores: Dict, metrics: Dict) -> str:
        recommendations = ""
        if scores['performance_score'] < 7:
            recommendations += "<li>Improve performance by optimizing load times and resource compression</li>"
        if scores['design_score'] < 7:
            recommendations += "<li>Enhance design with better typography, layout structure, and visual hierarchy</li>"
        if scores['seo_score'] < 7:
            recommendations += "<li>Improve SEO by adding meta descriptions, proper headings, and canonical tags</li>"
        if scores['accessibility_score'] < 7:
            recommendations += "<li>Enhance accessibility with proper ARIA landmarks, form labels, and heading structure</li>"
        return recommendations

    def _get_score_class(self, score: float) -> str:
        if score >= 7:
            return "good"
        elif score >= 5:
            return "average"
        return "poor"

    def _format_metrics(self, metrics: Dict) -> str:
        return ", ".join([f"{k.replace('_', ' ').title()}: {v}" for k, v in metrics.items()])

    def save_report(self, output_dir: str = "reports"):
        """Save the HTML report to a file"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        filename = f"website_analysis_{self.timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.generate_html_report())
            
        return filepath