#!/usr/bin/env python3
"""
Generate an HTML dashboard from audit CSV files.
Shows summary stats, missing events by venue, and detailed breakdowns.
"""
import csv
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def read_csv(filepath):
    """Read CSV file and return list of dicts."""
    if not Path(filepath).exists():
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def generate_dashboard():
    """Generate HTML dashboard from audit results.
    Reads from the compare script's actual outputs so numbers update every run.
    """
    # Use compare script outputs (updated each run) instead of stale audit_* files
    only_in_site = read_csv('only_in_site_xml.csv')
    only_in_master = read_csv('only_in_master.csv')
    future_only_site = only_in_site
    future_only_master = only_in_master

    matched_fuzzy = read_csv('matched_fuzzy.csv')
    fuzzy_matches = matched_fuzzy  # Dashboard table shows auto-matched; use same data
    needs_review = read_csv('needs_review.csv')

    # Venue counts: derive from ready_to_import_from_audit.csv (has Event Venue Name)
    venue_counts = {}
    ready_path = Path('output/ready_to_import/ready_to_import_from_audit.csv')
    if ready_path.exists():
        for row in read_csv(str(ready_path)):
            venue = (row.get('Event Venue Name') or '').strip()
            if venue:
                venue_counts[venue] = venue_counts.get(venue, 0) + 1
    # Fallback: legacy audit file if present
    if not venue_counts:
        master_only_venue = read_csv('audit_master_only_by_venue.csv')
        for row in master_only_venue:
            venue_counts[row.get('Event Venue Name', '')] = int(row.get('missing_event_count', 0))

    # Totals from compare outputs
    total_missing = len(future_only_master)
    total_extra = len(future_only_site)
    total_fuzzy = len(fuzzy_matches)
    total_matched = len(matched_fuzzy)
    total_needs_review = len(needs_review)

    untitled_count = sum(1 for e in future_only_site if 'untitled' in e.get('title', '').lower())
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Halifax Now - Event Audit Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header .timestamp {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-card h3 {{
            font-size: 0.9em;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        
        .stat-card .number {{
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-card.warning .number {{
            color: #f59e0b;
        }}
        
        .stat-card.success .number {{
            color: #10b981;
        }}
        
        .stat-card.info .number {{
            color: #3b82f6;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            font-size: 1.8em;
        }}
        
        .venue-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .venue-item {{
            background: #f9fafb;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .venue-name {{
            font-weight: 500;
            color: #333;
        }}
        
        .venue-count {{
            background: #667eea;
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .event-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .event-table th {{
            background: #f3f4f6;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #374151;
            border-bottom: 2px solid #667eea;
        }}
        
        .event-table td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .event-table tr:hover {{
            background: #f9fafb;
        }}
        
        .date {{
            color: #667eea;
            font-weight: 600;
            white-space: nowrap;
        }}
        
        .similarity {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        
        .similarity.high {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .similarity.medium {{
            background: #fed7aa;
            color: #92400e;
        }}
        
        .alert {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .alert h4 {{
            color: #92400e;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        .alert p {{
            color: #78350f;
        }}
        
        .success-box {{
            background: #d1fae5;
            border-left: 4px solid #10b981;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }}
        
        .success-box h4 {{
            color: #065f46;
            margin-bottom: 8px;
            font-size: 1.1em;
        }}
        
        .action-buttons {{
            margin-top: 20px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.2s;
            display: inline-block;
        }}
        
        .btn:hover {{
            background: #5568d3;
        }}
        
        .show-more {{
            text-align: center;
            margin-top: 15px;
        }}
        
        .show-more a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }}
        
        .show-more a:hover {{
            text-decoration: underline;
        }}
        
        .expandable {{
            max-height: 400px;
            overflow-y: auto;
        }}
        
        .note {{
            background: #eff6ff;
            border-left: 4px solid #3b82f6;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 0.95em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎭 Halifax Now - Event Audit Dashboard</h1>
            <p class="timestamp">Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <!-- Summary Statistics -->
        <div class="stats-grid">
            <div class="stat-card warning">
                <h3>Missing from Site</h3>
                <div class="number">{total_missing}</div>
                <p>Events need importing</p>
            </div>
            
            <div class="stat-card success">
                <h3>Auto-Matched</h3>
                <div class="number">{total_matched}</div>
                <p>Fuzzy matches found</p>
            </div>
            
            <div class="stat-card info">
                <h3>Extra on Site</h3>
                <div class="number">{total_extra}</div>
                <p>Not in master list</p>
            </div>
            
            <div class="stat-card">
                <h3>Needs Review</h3>
                <div class="number">{total_needs_review}</div>
                <p>Manual review required</p>
            </div>
        </div>
"""

    # Missing Events by Venue Section
    if venue_counts:
        html += """
        <div class="section">
            <h2>📍 Missing Events by Venue</h2>
            <p>Events in your master list that haven't been imported to the site yet.</p>
"""
        
        # Show top 10 venues
        sorted_venues = sorted(venue_counts.items(), key=lambda x: x[1], reverse=True)
        top_venues = sorted_venues[:10]
        
        html += '<div class="venue-grid">'
        for venue, count in top_venues:
            html += f"""
            <div class="venue-item">
                <span class="venue-name">{venue}</span>
                <span class="venue-count">{count}</span>
            </div>
"""
        html += '</div>'
        
        if len(sorted_venues) > 10:
            remaining = len(sorted_venues) - 10
            total_remaining = sum(count for venue, count in sorted_venues[10:])
            html += f'<div class="show-more"><p>+ {remaining} more venues with {total_remaining} events</p></div>'
        
        html += """
            <div class="alert">
                <h4>⚡ Quick Action</h4>
                <p>You have <strong>ready_to_import_from_audit.csv</strong> ready with {0} events to import into WordPress!</p>
            </div>
        </div>
""".format(total_missing)
    
    # Sample Missing Events
    if future_only_master:
        html += """
        <div class="section">
            <h2>📋 Sample Missing Events</h2>
            <p>Preview of events that need to be added to your site (showing first 20):</p>
            <div class="expandable">
            <table class="event-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Event Title</th>
                    </tr>
                </thead>
                <tbody>
"""
        for event in future_only_master[:20]:
            date = event.get('start_date', '')
            title = event.get('title', '')
            html += f"""
                    <tr>
                        <td class="date">{date}</td>
                        <td>{title}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
            </div>
"""
        if len(future_only_master) > 20:
            html += f'<div class="show-more"><p>+ {len(future_only_master) - 20} more events</p></div>'
        
        html += '</div>'
    
    # Untitled Events Warning
    if untitled_count > 0:
        html += f"""
        <div class="section">
            <h2>⚠️ Cleanup Required</h2>
            <div class="alert">
                <h4>Untitled Events Found</h4>
                <p>Found <strong>{untitled_count}</strong> "Untitled event" entries on your site. These are likely placeholder events that should be deleted.</p>
            </div>
"""
        
        # Show sample of untitled events
        untitled_events = [e for e in future_only_site if 'untitled' in e.get('title', '').lower()]
        html += """
            <table class="event-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Title</th>
                    </tr>
                </thead>
                <tbody>
"""
        for event in untitled_events[:10]:
            html += f"""
                    <tr>
                        <td class="date">{event.get('start_date', '')}</td>
                        <td>{event.get('title', '')}</td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    # Fuzzy Matches Section
    if fuzzy_matches:
        html += """
        <div class="section">
            <h2>🔍 Auto-Matched Events (Fuzzy)</h2>
            <p>Events that were automatically matched despite minor differences in formatting:</p>
            <div class="expandable">
            <table class="event-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Site Title</th>
                        <th>Master Title</th>
                        <th>Match</th>
                    </tr>
                </thead>
                <tbody>
"""
        for match in fuzzy_matches[:15]:
            similarity = float(match.get('similarity', 0))
            sim_class = 'high' if similarity >= 0.90 else 'medium'
            sim_pct = f"{similarity * 100:.0f}%"
            
            html += f"""
                    <tr>
                        <td class="date">{match.get('date', '')}</td>
                        <td>{match.get('site_title', '')}</td>
                        <td>{match.get('master_title', '')}</td>
                        <td><span class="similarity {sim_class}">{sim_pct}</span></td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
            </div>
"""
        if len(fuzzy_matches) > 15:
            html += f'<div class="show-more"><p>+ {len(fuzzy_matches) - 15} more matches</p></div>'
        
        html += """
            <div class="note">
                <p><strong>Note:</strong> These events are considered duplicates and won't be imported again. The most common differences are HTML entities (&amp; vs &) and minor formatting variations.</p>
            </div>
        </div>
"""
    
    # Extra Events on Site
    if future_only_site and not all('untitled' in e.get('title', '').lower() for e in future_only_site):
        # Only show if there are non-untitled events
        non_untitled = [e for e in future_only_site if 'untitled' not in e.get('title', '').lower()]
        if non_untitled:
            html += """
        <div class="section">
            <h2>➕ Events Only on Site</h2>
            <p>Events found on your live site but not in your master list (excluding untitled events):</p>
            <div class="expandable">
            <table class="event-table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Event Title</th>
                    </tr>
                </thead>
                <tbody>
"""
            for event in non_untitled[:15]:
                html += f"""
                    <tr>
                        <td class="date">{event.get('start_date', '')}</td>
                        <td>{event.get('title', '')}</td>
                    </tr>
"""
            
            html += """
                </tbody>
            </table>
            </div>
"""
            if len(non_untitled) > 15:
                html += f'<div class="show-more"><p>+ {len(non_untitled) - 15} more events</p></div>'
            
            html += """
            <div class="note">
                <p><strong>Note:</strong> These might be manual entries, Instagram events, or events from sources not yet in your master scraper system.</p>
            </div>
        </div>
"""
    
    # Summary and Next Steps
    html += """
        <div class="section">
            <h2>✅ Next Steps</h2>
"""
    
    if total_missing > 0:
        html += f"""
            <div class="success-box">
                <h4>Ready to Import</h4>
                <p><strong>{total_missing} events</strong> are ready to import from <code>ready_to_import_from_audit.csv</code></p>
            </div>
"""
    
    if untitled_count > 0:
        html += f"""
            <div class="alert" style="margin-top: 15px;">
                <h4>Cleanup Recommended</h4>
                <p>Consider deleting the <strong>{untitled_count} untitled events</strong> from your site to keep your database clean.</p>
            </div>
"""
    
    html += """
            <div class="note" style="margin-top: 15px;">
                <h4>How to Use This Audit:</h4>
                <ol style="margin-left: 20px; margin-top: 10px;">
                    <li>Import missing events using <code>ready_to_import_from_audit.csv</code> in WordPress</li>
                    <li>Clean up "Untitled event" placeholders from your site</li>
                    <li>Review any events "Only on Site" to see if they should be added to scrapers</li>
                    <li>Run the audit again after imports to verify everything is in sync</li>
                </ol>
            </div>
        </div>
    </body>
</html>
"""
    
    # Write HTML file
    output_path = 'audit_dashboard.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {output_path}")
    print(f"\n📊 Summary:")
    print(f"   Missing from site: {total_missing}")
    print(f"   Auto-matched: {total_matched}")
    print(f"   Extra on site: {total_extra}")
    print(f"   Needs review: {total_needs_review}")
    if untitled_count > 0:
        print(f"   ⚠️  Untitled events: {untitled_count}")
    print(f"\n🌐 Open {output_path} in your browser to view the dashboard")

if __name__ == '__main__':
    generate_dashboard()
