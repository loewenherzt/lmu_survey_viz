"""
Survey Data Visualization - Streamlit App
Displays original data, computed statistics, and histograms.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


@st.cache_data
def load_survey_data():
    """Load the original survey data."""
    df = pd.read_csv('data/input/umfrage.csv', sep='§', encoding='utf-8', engine='python')
    return df


@st.cache_data
def load_results():
    """Load the computed results."""
    df = pd.read_csv('data/output/results.csv')
    return df


def main():
    st.set_page_config(
        page_title="Survey Data Analysis",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Survey Data Analysis")
    st.markdown("Visualization of survey data from `umfrage.csv`")
    
    # Load data
    df = load_survey_data()
    results = load_results()
    
    # Create tabs
    tab3, tab1, tab2 = st.tabs(["📋 Data Table", "📈 Computed Statistics", "📊 Histograms"])
    
    # ==================== TAB 1: Data Table ====================
    with tab3:
        st.header("Original Survey Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Filter by Participant ID
            participants = ['All'] + sorted(df['Participant ID'].unique().tolist())
            selected_participant = st.selectbox("Filter by Participant ID", participants)
        
        with col2:
            # Filter by Item Type
            item_types = ['All'] + sorted(df['Item Type'].unique().tolist())
            selected_item_type = st.selectbox("Filter by Item Type", item_types)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_participant != 'All':
            filtered_df = filtered_df[filtered_df['Participant ID'] == selected_participant]
        if selected_item_type != 'All':
            filtered_df = filtered_df[filtered_df['Item Type'] == selected_item_type]
        
        st.write(f"Showing **{len(filtered_df)}** of {len(df)} rows")
        st.dataframe(filtered_df, width='stretch', height=500)
    
    # ==================== TAB 2: Computed Statistics ====================
    with tab1:
        st.header("Computed Statistics")
        
        # Parse results into a more usable format
        stats_data = []
        for _, row in results.iterrows():
            metric = row['Metric']
            value = row['Value']
            
            if 'correlation' in metric or '_vs_' in metric:
                continue  # Handle correlations separately
            
            parts = metric.split('_')
            item_type = parts[0].capitalize()
            
            if 'emotional' in metric:
                column = 'Emotional'
            elif 'pos_neg' in metric:
                column = 'Pos / Neg'
            elif 'suitability_age' in metric:
                column = 'Suitability Age'
            elif 'recommended_age' in metric:
                column = 'Recommended Age'
            else:
                continue
            
            stat_type = 'Mean' if 'mean' in metric else 'Median'
            stats_data.append({
                'Item Type': item_type,
                'Column': column,
                'Statistic': stat_type,
                'Value': value
            })
        
        stats_df = pd.DataFrame(stats_data)
        
        # Mean/Median charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Mean Values")
            mean_df = stats_df[stats_df['Statistic'] == 'Mean']
            fig = px.bar(
                mean_df,
                x='Column',
                y='Value',
                color='Item Type',
                barmode='group',
                title='Mean by Column and Item Type',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
        
        with col2:
            st.subheader("Median Values")
            median_df = stats_df[stats_df['Statistic'] == 'Median']
            fig = px.bar(
                median_df,
                x='Column',
                y='Value',
                color='Item Type',
                barmode='group',
                title='Median by Column and Item Type',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig)
        
        # Correlations
        st.subheader("Correlations")
        
        corr_data = []
        for _, row in results.iterrows():
            if '_vs_' in row['Metric']:
                corr_data.append({
                    'Correlation': row['Metric'].replace('_', ' ').title(),
                    'Value': row['Value']
                })
        
        corr_df = pd.DataFrame(corr_data)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                corr_df,
                x='Correlation',
                y='Value',
                title='Pearson Correlations',
                color='Value',
                color_continuous_scale='RdBu_r',
                range_color=[-1, 1]
            )
            fig.update_layout(xaxis_tickangle=-45)
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            st.plotly_chart(fig)
        
        with col2:
            st.markdown("**Correlation Values:**")
            for _, row in corr_df.iterrows():
                val = row['Value']
                color = "🟢" if abs(val) > 0.5 else "🟡" if abs(val) > 0.3 else "⚪"
                st.write(f"{color} {row['Correlation']}: **{val:.3f}**")
    
    # ==================== TAB 3: Histograms ====================
    with tab2:
        st.header("Data Distributions")
        
        # Emotional histogram
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Emotional")
            fig = px.histogram(
                df,
                x='Emotional',
                color='Item Type',
                barmode='overlay',
                nbins=7,
                title='Distribution of Emotional Ratings',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig)
        
        with col2:
            st.subheader("Pos / Neg")
            fig = px.histogram(
                df,
                x='Pos / Neg',
                color='Item Type',
                barmode='overlay',
                nbins=7,
                title='Distribution of Pos/Neg Ratings',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig)
        
        # Age histograms - split by question type
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Suitability Age")
            suitability_df = df[df['Age Question Type'] == 'suitability']
            fig = px.histogram(
                suitability_df,
                x='Age Answer',
                color='Item Type',
                barmode='overlay',
                title='Distribution of Suitability Age',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig)
        
        with col2:
            st.subheader("Recommended Age")
            recommended_df = df[df['Age Question Type'] == 'age_recommendation']
            fig = px.histogram(
                recommended_df,
                x='Age Answer',
                color='Item Type',
                barmode='overlay',
                title='Distribution of Recommended Age',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig)
        
        # Additional: Box plots
        st.subheader("Box Plots by Item Type")
        st.caption("Solid line = median, dashed line = mean")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.box(
                df,
                x='Item Type',
                y='Emotional',
                color='Item Type',
                title='Emotional Ratings by Item Type',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_traces(boxmean=True)
            st.plotly_chart(fig)
        
        with col2:
            fig = px.box(
                df,
                x='Item Type',
                y='Pos / Neg',
                color='Item Type',
                title='Pos/Neg Ratings by Item Type',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_traces(boxmean=True)
            st.plotly_chart(fig)
        
        # Box plots for Age columns
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.box(
                suitability_df,
                x='Item Type',
                y='Age Answer',
                color='Item Type',
                title='Suitability Age by Item Type',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_traces(boxmean=True)
            st.plotly_chart(fig)
        
        with col2:
            fig = px.box(
                recommended_df,
                x='Item Type',
                y='Age Answer',
                color='Item Type',
                title='Recommended Age by Item Type',
                color_discrete_map={'Stimulus': '#636EFA', 'Distraktor': '#EF553B'}
            )
            fig.update_traces(boxmean=True)
            st.plotly_chart(fig)


if __name__ == '__main__':
    main()
