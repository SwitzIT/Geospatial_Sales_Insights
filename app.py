import os
import pandas as pd
import folium
from folium.plugins import Fullscreen, MiniMap
from flask import Flask, request, render_template, send_from_directory, jsonify

app = Flask(__name__)
# Vercel/Render don't guarantee writable filesystems, so ideally, we only process files in-memory
# However, if an upload folder is strictly necessary, many cloud services allow writing to '/tmp'
app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('templates', exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                elif filename.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(filepath)
                else:
                    return jsonify({'error': 'Invalid file format. Please upload CSV or Excel.'})
                
                # Check required columns
                required_cols = ['Customer No.', 'LAT', 'LONG', 'Customer Name', 'Location', 'Sales']
                missing_cols = [col for col in required_cols if col not in df.columns]
                if missing_cols:
                    return jsonify({'error': f'Missing columns: {", ".join(missing_cols)}'})
                
                # Clean and convert data
                df['Sales'] = pd.to_numeric(df['Sales'], errors='coerce').fillna(0)
                df['LAT'] = pd.to_numeric(df['LAT'], errors='coerce')
                df['LONG'] = pd.to_numeric(df['LONG'], errors='coerce')
                
                # Drop rows with invalid coordinates
                df.dropna(subset=['LAT', 'LONG'], inplace=True)
                
                if df.empty:
                    return jsonify({'error': 'No valid geographic data found in the file.'})
                
                avg_sales = df['Sales'].mean()
                
                center_lat = df['LAT'].mean()
                center_lon = df['LONG'].mean()
                    
                m = folium.Map(location=[center_lat, center_lon], zoom_start=5, tiles='CartoDB Positron', control_scale=True)
                
                # Add enhanced map plugins
                Fullscreen(position='topright', title='Expand me', title_cancel='Exit me', force_separate_button=True).add_to(m)
                MiniMap(tile_layer='CartoDB Positron', position='bottomleft', toggle_display=True, minimized=True).add_to(m)
                
                for _, row in df.iterrows():
                    color_hex = '#10b981' if row['Sales'] >= avg_sales else '#ef4444'
                    status_bg = '#d1fae5' if row['Sales'] >= avg_sales else '#fee2e2'
                    status_text = '#065f46' if row['Sales'] >= avg_sales else '#991b1b'
                    status_label = 'Above Average' if row['Sales'] >= avg_sales else 'Below Average'
                    
                    # Premium Modern Popup
                    popup_html = f"""
                    <div style="font-family: 'Inter', -apple-system, sans-serif; min-width: 200px; padding: 4px;">
                        <h4 style="margin: 0 0 12px 0; color: #0f172a; font-size: 16px; font-weight: 700; border-bottom: 2px solid #f1f5f9; padding-bottom: 8px;">{row['Customer Name']}</h4>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                            <span style="color: #64748b; font-size: 12px; font-weight: 500;">Customer No.</span>
                            <span style="font-weight: 600; color: #334155; font-size: 12px;">{row['Customer No.']}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
                            <span style="color: #64748b; font-size: 12px; font-weight: 500;">Location</span>
                            <span style="font-weight: 600; color: #334155; font-size: 12px;">{row['Location']}</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 12px;">
                            <span style="color: #64748b; font-size: 12px; font-weight: 500;">Sales</span>
                            <span style="font-weight: 800; color: #4f46e5; font-size: 13px;">₹{row['Sales']:,.2f}</span>
                        </div>
                        <div style="background-color: {status_bg}; color: {status_text}; padding: 6px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; text-align: center; letter-spacing: 0.02em;">
                            {status_label}
                        </div>
                    </div>
                    """
                    
                    tooltip_html = f"<div style='font-family: Inter, sans-serif; font-weight: 600; color: #1e293b; padding: 2px;'>{row['Customer Name']} <span style='color: #cbd5e1; margin: 0 4px;'>|</span> <span style='color: #4f46e5;'>₹{row['Sales']:,.2f}</span></div>"
                    
                    # Outer layer (Glowing effect)
                    folium.CircleMarker(
                        location=[row['LAT'], row['LONG']],
                        radius=14,
                        color=color_hex,
                        weight=0,
                        fill=True,
                        fill_opacity=0.25,
                        tooltip=tooltip_html
                    ).add_to(m)
                    
                    # Core Layer (Solid center with white border)
                    folium.CircleMarker(
                        location=[row['LAT'], row['LONG']],
                        radius=6,
                        color='#ffffff',
                        weight=2,
                        fill=True,
                        fill_color=color_hex,
                        fill_opacity=1,
                        popup=folium.Popup(popup_html, max_width=320)
                    ).add_to(m)
                
                # Fit map bounds to all points
                sw = df[['LAT', 'LONG']].min().values.tolist()
                ne = df[['LAT', 'LONG']].max().values.tolist()
                m.fit_bounds([sw, ne])
                
                # Get map HTML structure in-memory instead of writing to file
                # This prevents caching issues & allows seamless cloud deployment on read-only systems
                map_html = m.get_root().render()
                
                # Clean up uploaded file
                if os.path.exists(filepath):
                    os.remove(filepath)
                
                return jsonify({'success': True, 'avg_sales': avg_sales, 'map_html': map_html})
                
            except Exception as e:
                # Clean up uploaded file if process fails
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': str(e)})
                
    return render_template('index.html')

if __name__ == '__main__':
    # Cloud-ready port binding
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
