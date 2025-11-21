"""
UI Components - Premium Tesla/Porsche/Apple-Style Dashboard

Premium dark-themed dashboard with sophisticated visualizations.
"""
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from typing import Dict, Any, List, Optional


# Premium Dark Theme Color Palette (Tesla/Porsche/Apple inspired)
THEME = {
    # Backgrounds
    'bg_primary': '#0A0E27',      # Deep dark blue-black
    'bg_secondary': '#141B2D',    # Slightly lighter dark
    'bg_card': '#1A2332',         # Card background
    'bg_hover': '#232B3E',        # Hover state
    
    # Accent Colors
    'accent_primary': '#00D4FF',   # Tesla cyan
    'accent_secondary': '#FF6B35', # Porsche orange
    'accent_success': '#00FF88',   # Bright green
    'accent_warning': '#FFB800',   # Amber
    'accent_danger': '#FF3366',    # Bright red
    
    # Status Colors
    'status_normal': '#00FF88',    # Success green
    'status_caution': '#FFB800',   # Warning amber
    'status_danger': '#FF3366',    # Danger red
    
    # Text
    'text_primary': '#FFFFFF',     # White
    'text_secondary': '#B0B8C4',   # Light gray
    'text_muted': '#6B7280',       # Muted gray
    
    # Chart Colors
    'chart_vibration': '#00D4FF',  # Cyan
    'chart_temperature': '#FF6B35', # Orange
    'chart_axis': '#2D3748',       # Dark grid
    'chart_grid': '#1A2332',       # Grid lines
}


def apply_premium_style():
    """
    Apply premium dark theme CSS (Tesla/Porsche/Apple style).
    """
    st.markdown(f"""
        <style>
        /* Import premium font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        /* Main app styling - Dark theme */
        .main {{
            background: {THEME['bg_primary']};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        /* Remove default Streamlit padding */
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
            padding-left: 2rem;
            padding-right: 2rem;
            max-width: 100%;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background: {THEME['bg_secondary']};
        }}
        
        [data-testid="stSidebar"] .css-1d391kg {{
            background: {THEME['bg_secondary']};
        }}
        
        /* Card styling - Premium dark cards */
        .premium-card {{
            background: {THEME['bg_card']};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .premium-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.12);
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
        }}
        
        /* Status card with accent border */
        .status-card {{
            background: {THEME['bg_card']};
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            border-left: 4px solid;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        }}
        
        /* Typography */
        .title {{
            font-size: 36px;
            font-weight: 800;
            color: {THEME['text_primary']};
            margin-bottom: 8px;
            letter-spacing: -1px;
            background: linear-gradient(135deg, {THEME['text_primary']} 0%, {THEME['text_secondary']} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .subtitle {{
            font-size: 18px;
            font-weight: 600;
            color: {THEME['text_secondary']};
            margin-bottom: 20px;
            letter-spacing: 0.3px;
        }}
        
        .section-title {{
            font-size: 14px;
            font-weight: 600;
            color: {THEME['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 16px;
        }}
        
        .metric-label {{
            font-size: 11px;
            font-weight: 600;
            color: {THEME['text_muted']};
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 12px;
        }}
        
        .metric-value {{
            font-size: 36px;
            font-weight: 700;
            color: {THEME['text_primary']};
            line-height: 1.1;
            font-variant-numeric: tabular-nums;
            margin-bottom: 4px;
        }}
        
        .metric-unit {{
            font-size: 18px;
            font-weight: 500;
            color: {THEME['text_muted']};
            margin-left: 6px;
        }}
        
        /* Status indicator */
        .status-indicator {{
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
            animation: pulse 2s ease-in-out infinite;
            box-shadow: 0 0 12px currentColor;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ 
                opacity: 1; 
                transform: scale(1);
            }}
            50% {{ 
                opacity: 0.7; 
                transform: scale(1.1);
            }}
        }}
        
        /* Message styling */
        .message {{
            font-size: 14px;
            color: {THEME['text_secondary']};
            line-height: 1.6;
            padding: 6px 0;
        }}
        
        /* Hide Streamlit branding */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Custom button styling */
        .stButton>button {{
            border-radius: 12px;
            font-weight: 600;
            border: none;
            padding: 12px 28px;
            font-size: 14px;
            transition: all 0.3s ease;
            background: linear-gradient(135deg, {THEME['accent_primary']} 0%, #0099CC 100%);
            color: {THEME['bg_primary']};
        }}
        
        .stButton>button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0, 212, 255, 0.4);
        }}
        
        /* Selectbox styling */
        .stSelectbox {{
            border-radius: 10px;
        }}
        
        /* Divider */
        .divider {{
            height: 1px;
            background: linear-gradient(90deg, transparent, {THEME['chart_axis']}, transparent);
            margin: 32px 0;
        }}
        
        /* Metric card */
        .metric-card {{
            background: {THEME['bg_card']};
            border-radius: 12px;
            padding: 24px 20px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            transition: all 0.3s ease;
            min-height: 120px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        
        .metric-card:hover {{
            border-color: rgba(255, 255, 255, 0.12);
            transform: translateY(-2px);
        }}
        
        /* Streamlit text color overrides */
        .stMarkdown {{
            color: {THEME['text_primary']};
        }}
        
        /* Info boxes */
        .stInfo {{
            background: {THEME['bg_card']};
            border-left: 4px solid {THEME['accent_primary']};
        }}
        
        /* Custom Tooltip */
        .premium-tooltip {{
            position: relative;
            display: inline-block;
            cursor: help;
            margin-left: 6px;
        }}
        
        .premium-tooltip .tooltip-content {{
            visibility: hidden;
            width: 220px;
            background-color: {THEME['bg_hover']};
            color: {THEME['text_primary']};
            text-align: left;
            border-radius: 8px;
            padding: 12px;
            position: absolute;
            z-index: 999;
            bottom: 140%;
            left: 50%;
            margin-left: -110px;
            opacity: 0;
            transition: opacity 0.2s, transform 0.2s;
            transform: translateY(10px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
            font-size: 12px;
            font-weight: 400;
            line-height: 1.4;
            pointer-events: none;
        }}
        
        .premium-tooltip .tooltip-content::after {{
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: {THEME['bg_hover']} transparent transparent transparent;
        }}
        
        .premium-tooltip:hover .tooltip-content {{
            visibility: visible;
            opacity: 1;
            transform: translateY(0);
        }}
        
        .tooltip-icon {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            border: 1px solid {THEME['text_muted']};
            color: {THEME['text_muted']};
            font-size: 10px;
            font-weight: 600;
            opacity: 0.6;
            transition: all 0.2s ease;
        }}
        
        .premium-tooltip:hover .tooltip-icon {{
            opacity: 1;
            color: {THEME['accent_primary']};
            border-color: {THEME['accent_primary']};
        }}
        </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = None):
    """
    Render premium header with gradient text.
    """
    st.markdown(f'<div class="title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_health_gauge(label: str, value: float, color: str, col=None, size: int = 200):
    """
    Render premium circular health gauge with dark theme.
    """
    # Determine gauge color based on value
    if value >= 70:
        gauge_color = THEME['status_normal']
    elif value >= 30:
        gauge_color = THEME['status_caution']
    else:
        gauge_color = THEME['status_danger']
    
    # Use provided color if specified
    if color:
        gauge_color = color
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        number={
            'suffix': "",
            'font': {'size': 36, 'family': 'Inter', 'weight': 700, 'color': gauge_color},
            'valueformat': '.1f'
        },
        delta={
            'reference': 100,
            'position': "bottom",
            'valueformat': '.1f',
            'font': {'size': 12, 'color': THEME['text_muted']}
        },
        gauge={
            'axis': {
                'range': [None, 100],
                'tickwidth': 0,
                'tickcolor': THEME['bg_card'],
                'showticklabels': False
            },
            'bar': {
                'color': gauge_color,
                'thickness': 0.15,
                'line': {'color': gauge_color, 'width': 2}
            },
            'bgcolor': THEME['bg_card'],
            'borderwidth': 0,
            'bordercolor': THEME['bg_card'],
            'steps': [
                {'range': [0, 100], 'color': THEME['chart_axis']}
            ],
            'threshold': {
                'line': {'color': gauge_color, 'width': 3},
                'thickness': 0.15,
                'value': value
            }
        }
    ))
    
    fig.update_layout(
        height=size,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': THEME['text_primary']},
        title={
            'text': label,
            'font': {'size': 14, 'family': 'Inter', 'weight': 600, 'color': THEME['text_secondary']},
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.95,
            'yanchor': 'top'
        }
    )
    
    if col:
        col.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    else:
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_status_card(state: str, color: str, messages: List[str], health_score: float):
    """
    Render premium status card with dark theme and Apple-style intelligence.
    Flattens HTML to prevent code block rendering.
    """
    # Get status emoji
    if health_score >= 70:
        emoji = "✓"
        status_desc = "All systems operating within normal parameters"
    elif health_score >= 30:
        emoji = "⚠"
        status_desc = "Some metrics show deviation from baseline"
    else:
        emoji = "✕"
        status_desc = "Critical deviations detected - inspection recommended"
    
    # Flattened HTML structure
    status_html = f'<div class="status-card" style="border-left-color: {color};"><div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;"><div style="display: flex; align-items: center;"><span class="status-indicator" style="color: {color}; background-color: {color};"></span><div><div style="font-size: 28px; font-weight: 700; color: {color}; letter-spacing: -0.5px;">{state}</div><div style="font-size: 13px; color: #6B7280; font-weight: 500; margin-top: 2px;">{status_desc}</div></div></div><div style="display: flex; align-items: center; gap: 16px;"><div style="text-align: right;"><div style="font-size: 13px; color: #6B7280; font-weight: 500; margin-bottom: 4px;">Health Score</div><div style="font-size: 32px; font-weight: 700; color: {color};">{health_score:.0f}%</div></div><div style="font-size: 48px; font-weight: 700; color: {color}; opacity: 0.2;">{emoji}</div></div></div><div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(255, 255, 255, 0.06);">'
    
    for message in messages[:4]:  # Limit to 4 messages
        status_html += f'<div class="message">{message}</div>'
    
    status_html += '</div></div>'
    
    st.markdown(status_html, unsafe_allow_html=True)


def render_time_series_plot(timestamps: np.ndarray, values: np.ndarray, 
                            title: str, ylabel: str, color: str = THEME['chart_vibration'],
                            threshold_bands: Dict[str, float] = None,
                            baseline_value: float = None):
    """
    Render premium dark-themed time series plot.
    """
    fig = go.Figure()
    
    # Add threshold bands if provided
    if threshold_bands:
        normal = threshold_bands.get('normal', 0)
        caution = threshold_bands.get('caution', 0)
        
        # Normal band
        fig.add_hrect(
            y0=0, y1=normal,
            fillcolor=THEME['status_normal'], opacity=0.08,
            layer="below", line_width=0,
            annotation_text="Normal", annotation_position="top left",
            annotation_font_size=10, annotation_font_color=THEME['text_muted']
        )
        # Caution band
        fig.add_hrect(
            y0=normal, y1=caution,
            fillcolor=THEME['status_caution'], opacity=0.08,
            layer="below", line_width=0,
            annotation_text="Caution", annotation_position="top left",
            annotation_font_size=10, annotation_font_color=THEME['text_muted']
        )
        # Danger band
        if len(values) > 0:
            max_val = max(values) * 1.2
        else:
            max_val = caution * 1.5
        fig.add_hrect(
            y0=caution, y1=max_val,
            fillcolor=THEME['status_danger'], opacity=0.08,
            layer="below", line_width=0,
            annotation_text="Danger", annotation_position="top left",
            annotation_font_size=10, annotation_font_color=THEME['text_muted']
        )
    
    # Add baseline line if provided
    if baseline_value is not None and len(timestamps) > 0:
        fig.add_hline(
            y=baseline_value,
            line_dash="dash",
            line_color=THEME['text_muted'],
            line_width=1,
            opacity=0.5,
            annotation_text=f"Baseline: {baseline_value:.3f}",
            annotation_position="right",
            annotation_font_size=10,
            annotation_font_color=THEME['text_muted']
        )
    
    # Convert hex to rgba for fill
    def hex_to_rgba(hex_color, alpha=0.2):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f'rgba({r}, {g}, {b}, {alpha})'
    
    # Add main trace with gradient fill
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=values,
        mode='lines',
        line=dict(color=color, width=2.5, shape='spline'),
        fill='tozeroy',
        fillcolor=hex_to_rgba(color, 0.15),
        name=ylabel,
        hovertemplate='<b>%{y:.4f}</b><br>Time: %{x:.1f}s<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 16, 'family': 'Inter', 'weight': 600, 'color': THEME['text_primary']},
            'x': 0,
            'xanchor': 'left',
            'y': 0.98
        },
        xaxis_title="Time (seconds ago)",
        yaxis_title=ylabel,
        height=280,
        margin=dict(l=50, r=20, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': THEME['text_secondary'], 'size': 12},
        hovermode='x unified',
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=THEME['chart_grid'],
            zeroline=False,
            showline=True,
            linecolor=THEME['chart_axis'],
            linewidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=THEME['chart_grid'],
            zeroline=False,
            showline=True,
            linecolor=THEME['chart_axis'],
            linewidth=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_metric_card(label: str, value: str, unit: str, trend: Optional[str] = None, color: str = None, help_text: str = None):
    """
    Render a single premium metric card.
    """
    trend_html = ""
    if trend:
        trend_color = THEME['status_normal'] if trend.startswith('+') else THEME['status_danger']
        trend_html = f'<div style="font-size: 13px; color: {trend_color}; margin-top: 8px; font-weight: 500;">{trend}</div>'
    
    color_style = f"color: {color};" if color else ""
    
    # flattened HTML
    card_html = f'<div class="metric-card"><div style="display: flex; align-items: center; margin-bottom: 8px;"><span class="metric-label" style="margin-bottom: 0;">{label}</span></div><div class="metric-value" style="{color_style}">{value}<span class="metric-unit">{unit}</span></div>{trend_html}</div>'
    
    return card_html


def render_metric_row(metrics: List[Dict[str, Any]]):
    """
    Render a row of premium metric cards.
    """
    cols = st.columns(len(metrics))
    
    for col, metric in zip(cols, metrics):
        with col:
            trend = metric.get('trend', None)
            color = metric.get('color', None)
            # help_text argument removed as icons were not rendering reliably
            card_html = render_metric_card(
                metric['label'],
                metric['value'],
                metric.get('unit', ''),
                trend,
                color
            )
            st.markdown(card_html, unsafe_allow_html=True)


def render_3d_vibration_plot(ax: np.ndarray, ay: np.ndarray, az: np.ndarray, color: str = THEME['chart_vibration']):
    """
    Render 3D vibration vector visualization.
    """
    if len(ax) == 0:
        return
    
    # Get latest values
    latest_ax = ax[-1] if len(ax) > 0 else 0
    latest_ay = ay[-1] if len(ay) > 0 else 0
    latest_az = az[-1] if len(az) > 0 else 0
    
    # Create 3D scatter plot
    fig = go.Figure(data=go.Scatter3d(
        x=[0, latest_ax],
        y=[0, latest_ay],
        z=[0, latest_az],
        mode='lines+markers',
        line=dict(color=color, width=8),
        marker=dict(size=8, color=color),
        hovertemplate='X: %{x:.3f}<br>Y: %{y:.3f}<br>Z: %{z:.3f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': '3D Vibration Vector',
            'font': {'size': 14, 'family': 'Inter', 'weight': 600, 'color': THEME['text_primary']}
        },
        scene=dict(
            xaxis=dict(
                title='X (g)',
                backgroundcolor=THEME['bg_card'],
                gridcolor=THEME['chart_grid'],
                showbackground=True,
                color=THEME['text_secondary']
            ),
            yaxis=dict(
                title='Y (g)',
                backgroundcolor=THEME['bg_card'],
                gridcolor=THEME['chart_grid'],
                showbackground=True,
                color=THEME['text_secondary']
            ),
            zaxis=dict(
                title='Z (g)',
                backgroundcolor=THEME['bg_card'],
                gridcolor=THEME['chart_grid'],
                showbackground=True,
                color=THEME['text_secondary']
            ),
            bgcolor=THEME['bg_primary']
        ),
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_diagnostics_panel(stats: Dict[str, Any]):
    """
    Render system diagnostics panel with dark theme.
    """
    st.markdown('<div class="section-title">System Diagnostics</div>', unsafe_allow_html=True)
    
    mode = stats.get('mode', 'serial')
    
    if mode == 'replay':
        metrics = [
            {'label': 'Mode', 'value': '📼 Replay', 'unit': '', 'color': THEME['accent_primary']},
            {'label': 'Packets', 'value': f"{stats.get('packet_count', 0):,}", 'unit': '', 'color': None},
            {'label': 'Buffer', 'value': f"{stats.get('buffer_size', 0):,}", 'unit': ' pts', 'color': None},
            {'label': 'Progress', 'value': f"{stats.get('progress', 0):.0f}", 'unit': '%', 'color': None}
        ]
    else:
        fps = stats.get('fps', 0.0)
        connected = stats.get('connected', False)
        status_emoji = '🟢' if connected else '🔴'
        status_color = THEME['status_normal'] if connected else THEME['status_danger']
        
        metrics = [
            {'label': 'Status', 'value': status_emoji, 'unit': '', 'color': status_color},
            {'label': 'Port', 'value': stats.get('port', 'N/A')[:8], 'unit': '', 'color': None},
            {'label': 'Packet Rate', 'value': f"{fps:.1f}", 'unit': ' Hz', 'color': None},
            {'label': 'Errors', 'value': f"{stats.get('error_count', 0)}", 'unit': '', 'color': THEME['status_danger'] if stats.get('error_count', 0) > 0 else None}
        ]
    
    render_metric_row(metrics)


def render_divider():
    """
    Render a subtle divider line.
    """
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def render_section_title(title: str, subtitle: str = None):
    """
    Render a section title with optional subtitle (Apple style).
    Flattened HTML to prevent code block rendering.
    """
    if subtitle:
        title_html = f'<div class="section-title">{title}</div><div style="font-size: 13px; color: #6B7280; font-weight: 400; margin-top: 4px; letter-spacing: 0; text-transform: none; margin-bottom: 16px;">{subtitle}</div>'
    else:
        title_html = f'<div class="section-title">{title}</div>'
    
    st.markdown(title_html, unsafe_allow_html=True)


def render_histogram_plot(values: np.ndarray, title: str, xlabel: str, 
                         color: str = THEME['chart_vibration'], 
                         baseline_value: float = None):
    """
    Render premium dark-themed histogram plot.
    """
    if len(values) == 0:
        st.info("No data available for histogram")
        return
    
    fig = go.Figure()
    
    # Create histogram
    fig.add_trace(go.Histogram(
        x=values,
        nbinsx=30,
        marker_color=color,
        marker_line_color=THEME['bg_card'],
        marker_line_width=1,
        opacity=0.8,
        name=xlabel,
        hovertemplate='<b>%{y}</b> samples<br>Value: %{x:.4f}<extra></extra>'
    ))
    
    # Add baseline line if provided
    if baseline_value is not None:
        fig.add_vline(
            x=baseline_value,
            line_dash="dash",
            line_color=THEME['text_muted'],
            line_width=2,
            opacity=0.7,
            annotation_text=f"Baseline: {baseline_value:.3f}",
            annotation_position="top",
            annotation_font_size=10,
            annotation_font_color=THEME['text_muted']
        )
    
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 16, 'family': 'Inter', 'weight': 600, 'color': THEME['text_primary']},
            'x': 0,
            'xanchor': 'left',
            'y': 0.98
        },
        xaxis_title=xlabel,
        yaxis_title="Frequency",
        height=280,
        margin=dict(l=50, r=20, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': THEME['text_secondary'], 'size': 12},
        showlegend=False,
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=THEME['chart_grid'],
            zeroline=False,
            showline=True,
            linecolor=THEME['chart_axis'],
            linewidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=THEME['chart_grid'],
            zeroline=False,
            showline=True,
            linecolor=THEME['chart_axis'],
            linewidth=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_box_plot(values: np.ndarray, title: str, ylabel: str,
                   color: str = THEME['chart_vibration'],
                   baseline_value: float = None):
    """
    Render premium dark-themed box plot.
    """
    if len(values) == 0:
        st.info("No data available for box plot")
        return
    
    fig = go.Figure()
    
    # Create box plot
    fig.add_trace(go.Box(
        y=values,
        name=ylabel,
        marker_color=color,
        line_color=color,
        fillcolor=color,
        opacity=0.6,
        boxmean='sd',  # Show mean and standard deviation
        hovertemplate='<b>%{y:.4f}</b><extra></extra>'
    ))
    
    # Add baseline line if provided
    if baseline_value is not None:
        fig.add_hline(
            y=baseline_value,
            line_dash="dash",
            line_color=THEME['text_muted'],
            line_width=2,
            opacity=0.7,
            annotation_text=f"Baseline: {baseline_value:.3f}",
            annotation_position="right",
            annotation_font_size=10,
            annotation_font_color=THEME['text_muted']
        )
    
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 16, 'family': 'Inter', 'weight': 600, 'color': THEME['text_primary']},
            'x': 0,
            'xanchor': 'left',
            'y': 0.98
        },
        yaxis_title=ylabel,
        height=280,
        margin=dict(l=50, r=20, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'family': 'Inter', 'color': THEME['text_secondary'], 'size': 12},
        showlegend=False,
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=THEME['chart_grid'],
            zeroline=False,
            showline=True,
            linecolor=THEME['chart_axis'],
            linewidth=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_icon_legend():
    """
    Render a minimalist Apple-style legend with contextual descriptions.
    Using Streamlit native markdown for maximum compatibility.
    """
    with st.expander("📖 System Guide - Icon & Metric Explanations", expanded=False):
        # Removed reference to hovering over icons since they were removed
        
        st.markdown("#### 🔍 How Health Scores Are Calculated")
        st.markdown("""
        The system uses a hybrid approach of statistical analysis and absolute safety limits:
        
        **1. Temperature Analysis (Absolute Limits):**
        *   **Safe Zone (15°C - 35°C):** Considered optimal operating range (100% Health).
        *   **Caution Zone:** 35-40°C or 10-15°C. Health score drops linearly.
        *   **Danger Zone:** >40°C or <10°C. Critical alert (0% Health).
        
        **2. Vibration Analysis (Statistical Sensitivity):**
        *   **Enhanced Sensitivity:** The system detects both sustained vibration (mean) and sudden impacts (max peaks).
        *   **Caution Threshold:** >1.2σ (Standard Deviations) from baseline.
        *   **Danger Threshold:** >2.0σ from baseline.
        
        The final **Health Score (0-100%)** reflects the worst-performing metric.
        """)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**HEALTH STATUS**")
            st.markdown("✓ Normal operation")
            st.markdown("⚠ Caution - deviation detected")
            st.markdown("✕ Critical - immediate action")
        
        with col2:
            st.markdown("**DIAGNOSTIC LEVELS**")
            st.markdown("💚 Excellent health (>90%)")
            st.markdown("⚠️ Minor deviation (30-70%)")
            st.markdown("🚨 Critical (<30%)")
        
        with col3:
            st.markdown("**CONNECTION STATUS**")
            st.markdown("🟢 Live data stream")
            st.markdown("🔴 Offline")
            st.markdown("📼 Playback mode")
        
        st.markdown("---")
        st.markdown("""
        **Statistical Terms:**
        *   **Z-Score:** Standard deviations from baseline mean.
        *   **CV:** Coefficient of Variation (variability).
        *   **RMS:** Root Mean Square (energy/power).
        """)
