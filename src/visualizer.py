import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List
import base64
from io import BytesIO

class SentimentVisualizer:
    def __init__(self, config):
        self.config = config
        self.colors = config.DEFAULT_COLORS
        self.theme = config.CHART_THEME
    
    def create_sentiment_pie_chart(self, summary_stats: Dict) -> go.Figure:
        """Create sentiment distribution pie chart"""
        
        sentiment_dist = summary_stats.get('sentiment_distribution', {})
        
        labels = list(sentiment_dist.keys())
        values = list(sentiment_dist.values())
        colors = [self.colors.get(label, '#808080') for label in labels]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.4,
            textinfo='label+percent+value',
            textfont_size=12,
            textposition='auto'
        )])
        
        fig.update_layout(
            title={
                'text': 'Sentiment Distribution',
                'x': 0.5,
                'font': {'size': 20}
            },
            template=self.theme,
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    def create_sentiment_bar_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create sentiment counts bar chart"""
        
        sentiment_counts = df['final_sentiment'].value_counts()
        
        fig = go.Figure(data=[
            go.Bar(
                x=sentiment_counts.index,
                y=sentiment_counts.values,
                marker_color=[self.colors.get(x, '#808080') for x in sentiment_counts.index],
                text=sentiment_counts.values,
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title={
                'text': 'Sentiment Counts by Category',
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title="Sentiment",
            yaxis_title="Number of Posts",
            template=self.theme,
            height=400
        )
        
        return fig
    
    def create_sentiment_timeline(self, df: pd.DataFrame) -> go.Figure:
        """Create sentiment over time line chart"""
        
        if 'created_utc' not in df.columns:
            # Create dummy timeline
            fig = go.Figure()
            fig.add_annotation(
                text="Timeline data not available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16)
            )
            fig.update_layout(template=self.theme, height=400)
            return fig
        
        # Convert to datetime if string
        df['created_utc'] = pd.to_datetime(df['created_utc'])
        
        # Group by date and sentiment
        df['date'] = df['created_utc'].dt.date
        timeline_data = df.groupby(['date', 'final_sentiment']).size().reset_index(name='count')
        
        fig = go.Figure()
        
        for sentiment in ['positive', 'negative', 'neutral']:
            data = timeline_data[timeline_data['final_sentiment'] == sentiment]
            
            fig.add_trace(go.Scatter(
                x=data['date'],
                y=data['count'],
                mode='lines+markers',
                name=sentiment.capitalize(),
                line=dict(color=self.colors.get(sentiment, '#808080')),
                marker=dict(size=6)
            ))
        
        fig.update_layout(
            title={
                'text': 'Sentiment Over Time',
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title="Date",
            yaxis_title="Number of Posts",
            template=self.theme,
            height=400,
            hovermode='x unified'
        )
        
        return fig
    
    def create_source_analysis(self, df: pd.DataFrame) -> go.Figure:
        """Create source-wise sentiment analysis"""
        
        source_sentiment = df.groupby(['source', 'final_sentiment']).size().reset_index(name='count')
        
        fig = px.bar(
            source_sentiment,
            x='source',
            y='count',
            color='final_sentiment',
            color_discrete_map=self.colors,
            title='Sentiment Distribution by Source',
            labels={'count': 'Number of Posts', 'source': 'Source'}
        )
        
        fig.update_layout(
            template=self.theme,
            height=400,
            title_x=0.5
        )
        
        return fig
    
    def create_confidence_distribution(self, df: pd.DataFrame) -> go.Figure:
        """Create confidence score distribution"""
        
        fig = go.Figure()
        
        for sentiment in ['positive', 'negative', 'neutral']:
            data = df[df['final_sentiment'] == sentiment]['final_confidence']
            
            fig.add_trace(go.Histogram(
                x=data,
                name=sentiment.capitalize(),
                opacity=0.7,
                marker_color=self.colors.get(sentiment, '#808080'),
                nbinsx=20
            ))
        
        fig.update_layout(
            title={
                'text': 'Confidence Score Distribution',
                'x': 0.5,
                'font': {'size': 18}
            },
            xaxis_title="Confidence Score",
            yaxis_title="Frequency",
            template=self.theme,
            height=400,
            barmode='overlay'
        )
        
        return fig
    
    def create_wordcloud(self, df: pd.DataFrame, sentiment: str = 'all') -> str:
        """Create word cloud and return as base64 string"""
        
        try:
            if sentiment != 'all':
                text_data = df[df['final_sentiment'] == sentiment]['cleaned_text']
            else:
                text_data = df['cleaned_text']
            
            # Combine all text
            all_text = ' '.join(text_data.dropna().astype(str))
            
            if len(all_text.strip()) == 0:
                return None
            
            # Create word cloud
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white' if self.theme == 'plotly' else 'black',
                colormap='viridis',
                max_words=100,
                relative_scaling=0.5,
                random_state=42
            ).generate(all_text)
            
            # Convert to base64
            img = BytesIO()
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.tight_layout(pad=0)
            plt.savefig(img, format='png', bbox_inches='tight', 
                       facecolor='white' if self.theme == 'plotly' else 'black')
            plt.close()
            
            img.seek(0)
            img_b64 = base64.b64encode(img.read()).decode()
            
            return img_b64
            
        except Exception as e:
            print(f"Error creating wordcloud: {e}")
            return None
    
    def create_top_posts_table(self, df: pd.DataFrame, sentiment: str = 'all', top_n: int = 10) -> pd.DataFrame:
        """Create table of top posts by sentiment"""
        
        if sentiment != 'all':
            filtered_df = df[df['final_sentiment'] == sentiment]
        else:
            filtered_df = df
        
        if filtered_df.empty:
            return pd.DataFrame()
        
        # Sort by confidence and score
        top_posts = filtered_df.nlargest(top_n, ['final_confidence', 'score'])
        
        # Select relevant columns
        display_columns = [
            'original_text', 'final_sentiment', 'final_confidence', 
            'source', 'score', 'created_utc'
        ]
        
        result = top_posts[display_columns].copy()
        
        # Truncate long text
        result['original_text'] = result['original_text'].str[:200] + '...'
        
        # Round confidence
        result['final_confidence'] = result['final_confidence'].round(3)
        
        return result
    
    def create_dashboard_summary(self, summary_stats: Dict) -> Dict:
        """Create summary metrics for dashboard"""
        
        total_posts = summary_stats.get('total_posts', 0)
        sentiment_pct = summary_stats.get('sentiment_percentages', {})
        
        metrics = {
            'total_posts': f"{total_posts:,}",
            'positive_percentage': f"{sentiment_pct.get('positive', 0):.1f}%",
            'negative_percentage': f"{sentiment_pct.get('negative', 0):.1f}%",
            'neutral_percentage': f"{sentiment_pct.get('neutral', 0):.1f}%",
            'avg_confidence': f"{summary_stats.get('average_confidence', 0):.3f}",
            'top_source': list(summary_stats.get('top_sources', {}).keys())[0] if summary_stats.get('top_sources') else 'N/A'
        }
        
        return metrics
