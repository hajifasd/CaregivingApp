"""
护工资源管理系统 - 数据可视化
====================================

创建交互式数据可视化仪表盘
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from bigdata_config import VISUALIZATION_CONFIG, DATA_PATHS

logger = logging.getLogger(__name__)

class DataVisualizer:
    """数据可视化类"""
    
    def __init__(self):
        self.color_palette = VISUALIZATION_CONFIG['COLOR_PALETTE']
        self.theme = VISUALIZATION_CONFIG['CHART_THEME']
    
    def create_caregiver_distribution_chart(self, data):
        """创建护工分布图表"""
        try:
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('年龄分布', '薪资分布', '评分分布', '地域分布'),
                specs=[[{"type": "histogram"}, {"type": "histogram"}],
                       [{"type": "histogram"}, {"type": "pie"}]]
            )
            
            # 年龄分布
            fig.add_trace(
                go.Histogram(x=data['age'], name='年龄分布', nbinsx=20),
                row=1, col=1
            )
            
            # 薪资分布
            fig.add_trace(
                go.Histogram(x=data['hourly_rate'], name='薪资分布', nbinsx=20),
                row=1, col=2
            )
            
            # 评分分布
            fig.add_trace(
                go.Histogram(x=data['rating'], name='评分分布', nbinsx=10),
                row=2, col=1
            )
            
            # 地域分布
            location_counts = data['location'].value_counts()
            fig.add_trace(
                go.Pie(labels=location_counts.index, values=location_counts.values, name='地域分布'),
                row=2, col=2
            )
            
            fig.update_layout(
                title_text="护工数据分布分析",
                showlegend=False,
                height=800,
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ 护工分布图表创建失败: {str(e)}")
            return None
    
    def create_market_trend_chart(self, data):
        """创建市场趋势图表"""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('薪资趋势', '需求趋势'),
                specs=[[{"secondary_y": True}], [{"secondary_y": False}]]
            )
            
            # 薪资趋势
            fig.add_trace(
                go.Scatter(
                    x=data['date'],
                    y=data['avg_salary'],
                    mode='lines+markers',
                    name='平均薪资',
                    line=dict(color=self.color_palette[0])
                ),
                row=1, col=1
            )
            
            # 需求趋势
            fig.add_trace(
                go.Bar(
                    x=data['date'],
                    y=data['job_count'],
                    name='职位数量',
                    marker_color=self.color_palette[1]
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                title_text="护工市场趋势分析",
                height=800,
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ 市场趋势图表创建失败: {str(e)}")
            return None
    
    def create_success_prediction_chart(self, predictions):
        """创建成功率预测图表"""
        try:
            fig = go.Figure()
            
            # 实际成功率
            fig.add_trace(go.Scatter(
                x=predictions['actual'],
                y=predictions['predicted'],
                mode='markers',
                name='预测结果',
                marker=dict(
                    color=predictions['predicted'],
                    colorscale='Viridis',
                    size=8,
                    opacity=0.7
                )
            ))
            
            # 理想线
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode='lines',
                name='理想预测线',
                line=dict(dash='dash', color='red')
            ))
            
            fig.update_layout(
                title="护工成功率预测结果",
                xaxis_title="实际成功率",
                yaxis_title="预测成功率",
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ 成功率预测图表创建失败: {str(e)}")
            return None
    
    def create_cluster_analysis_chart(self, cluster_data):
        """创建聚类分析图表"""
        try:
            fig = go.Figure()
            
            # 为每个聚类添加散点
            for cluster_id in cluster_data['cluster'].unique():
                cluster_points = cluster_data[cluster_data['cluster'] == cluster_id]
                
                fig.add_trace(go.Scatter(
                    x=cluster_points['hourly_rate'],
                    y=cluster_points['rating'],
                    mode='markers',
                    name=f'聚类 {cluster_id}',
                    marker=dict(
                        size=8,
                        opacity=0.7
                    ),
                    text=cluster_points['name'],
                    hovertemplate='<b>%{text}</b><br>' +
                                '时薪: %{x}<br>' +
                                '评分: %{y}<br>' +
                                '<extra></extra>'
                ))
            
            fig.update_layout(
                title="护工聚类分析",
                xaxis_title="时薪",
                yaxis_title="评分",
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ 聚类分析图表创建失败: {str(e)}")
            return None
    
    def create_recommendation_chart(self, recommendations):
        """创建推荐结果图表"""
        try:
            fig = go.Figure()
            
            # 推荐分数分布
            fig.add_trace(go.Histogram(
                x=recommendations['score'],
                nbinsx=20,
                name='推荐分数分布',
                marker_color=self.color_palette[2]
            ))
            
            fig.update_layout(
                title="护工推荐分数分布",
                xaxis_title="推荐分数",
                yaxis_title="频次",
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ 推荐结果图表创建失败: {str(e)}")
            return None
    
    def create_demand_forecast_chart(self, forecast_data):
        """创建需求预测图表"""
        try:
            fig = go.Figure()
            
            # 历史数据
            fig.add_trace(go.Scatter(
                x=forecast_data['date'],
                y=forecast_data['actual_demand'],
                mode='lines+markers',
                name='实际需求',
                line=dict(color=self.color_palette[0])
            ))
            
            # 预测数据
            fig.add_trace(go.Scatter(
                x=forecast_data['forecast_date'],
                y=forecast_data['predicted_demand'],
                mode='lines+markers',
                name='预测需求',
                line=dict(color=self.color_palette[1], dash='dash')
            ))
            
            # 置信区间
            fig.add_trace(go.Scatter(
                x=forecast_data['forecast_date'],
                y=forecast_data['upper_bound'],
                mode='lines',
                line=dict(width=0),
                showlegend=False
            ))
            
            fig.add_trace(go.Scatter(
                x=forecast_data['forecast_date'],
                y=forecast_data['lower_bound'],
                mode='lines',
                line=dict(width=0),
                fill='tonexty',
                fillcolor='rgba(0,100,80,0.2)',
                name='置信区间',
                showlegend=True
            ))
            
            fig.update_layout(
                title="护工需求预测",
                xaxis_title="日期",
                yaxis_title="需求数量",
                template=self.theme
            )
            
            return fig
            
        except Exception as e:
            logger.error(f"❌ 需求预测图表创建失败: {str(e)}")
            return None
    
    def create_dashboard_html(self, charts_data):
        """创建完整的仪表盘HTML"""
        try:
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>护工资源管理系统 - 数据分析仪表盘</title>
                <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .chart-container { margin: 20px 0; }
                    .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                    .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
                    .stat-value { font-size: 2em; font-weight: bold; color: #007bff; }
                    .stat-label { color: #6c757d; margin-top: 5px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>护工资源管理系统 - 数据分析仪表盘</h1>
                    <p>实时数据分析和预测</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">{total_caregivers}</div>
                        <div class="stat-label">总护工数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_users}</div>
                        <div class="stat-label">总用户数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{total_appointments}</div>
                        <div class="stat-label">总预约数</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{avg_rating}</div>
                        <div class="stat-label">平均评分</div>
                    </div>
                </div>
                
                <div class="chart-container">
                    <div id="distribution-chart"></div>
                </div>
                
                <div class="chart-container">
                    <div id="trend-chart"></div>
                </div>
                
                <div class="chart-container">
                    <div id="prediction-chart"></div>
                </div>
                
                <div class="chart-container">
                    <div id="cluster-chart"></div>
                </div>
                
                <script>
                    // 护工分布图表
                    var distributionData = {distribution_chart};
                    Plotly.newPlot('distribution-chart', distributionData.data, distributionData.layout);
                    
                    // 市场趋势图表
                    var trendData = {trend_chart};
                    Plotly.newPlot('trend-chart', trendData.data, trendData.layout);
                    
                    // 预测图表
                    var predictionData = {prediction_chart};
                    Plotly.newPlot('prediction-chart', predictionData.data, predictionData.layout);
                    
                    // 聚类图表
                    var clusterData = {cluster_chart};
                    Plotly.newPlot('cluster-chart', clusterData.data, clusterData.layout);
                </script>
            </body>
            </html>
            """
            
            # 填充模板数据
            html_content = html_template.format(
                total_caregivers=charts_data.get('total_caregivers', 0),
                total_users=charts_data.get('total_users', 0),
                total_appointments=charts_data.get('total_appointments', 0),
                avg_rating=charts_data.get('avg_rating', 0.0),
                distribution_chart=json.dumps(charts_data.get('distribution_chart', {}), cls=plotly.utils.PlotlyJSONEncoder),
                trend_chart=json.dumps(charts_data.get('trend_chart', {}), cls=plotly.utils.PlotlyJSONEncoder),
                prediction_chart=json.dumps(charts_data.get('prediction_chart', {}), cls=plotly.utils.PlotlyJSONEncoder),
                cluster_chart=json.dumps(charts_data.get('cluster_chart', {}), cls=plotly.utils.PlotlyJSONEncoder)
            )
            
            # 保存HTML文件
            with open(f"{DATA_PATHS['ANALYSIS_RESULTS']}/dashboard.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info("✅ 仪表盘HTML创建成功")
            
        except Exception as e:
            logger.error(f"❌ 仪表盘HTML创建失败: {str(e)}")
    
    def generate_all_charts(self, data):
        """生成所有图表"""
        try:
            logger.info("🚀 开始生成数据可视化图表")
            
            charts = {}
            
            # 1. 护工分布图表
            if 'caregiver_data' in data:
                charts['distribution_chart'] = self.create_caregiver_distribution_chart(data['caregiver_data'])
            
            # 2. 市场趋势图表
            if 'market_data' in data:
                charts['trend_chart'] = self.create_market_trend_chart(data['market_data'])
            
            # 3. 预测图表
            if 'prediction_data' in data:
                charts['prediction_chart'] = self.create_success_prediction_chart(data['prediction_data'])
            
            # 4. 聚类图表
            if 'cluster_data' in data:
                charts['cluster_chart'] = self.create_cluster_analysis_chart(data['cluster_data'])
            
            # 5. 推荐图表
            if 'recommendation_data' in data:
                charts['recommendation_chart'] = self.create_recommendation_chart(data['recommendation_data'])
            
            # 6. 需求预测图表
            if 'forecast_data' in data:
                charts['forecast_chart'] = self.create_demand_forecast_chart(data['forecast_data'])
            
            logger.info("✅ 数据可视化图表生成完成")
            return charts
            
        except Exception as e:
            logger.error(f"❌ 数据可视化图表生成失败: {str(e)}")
            return {}

def main():
    """主函数"""
    visualizer = DataVisualizer()
    
    # 示例数据
    sample_data = {
        'caregiver_data': pd.DataFrame({
            'age': np.random.normal(35, 10, 1000),
            'hourly_rate': np.random.normal(50, 15, 1000),
            'rating': np.random.normal(4.2, 0.8, 1000),
            'location': np.random.choice(['北京', '上海', '广州', '深圳'], 1000)
        }),
        'market_data': pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=12, freq='M'),
            'avg_salary': np.random.normal(50, 5, 12),
            'job_count': np.random.poisson(100, 12)
        })
    }
    
    charts = visualizer.generate_all_charts(sample_data)
    print(f"生成了 {len(charts)} 个图表")

if __name__ == "__main__":
    main()
