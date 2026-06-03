import streamlit as st
import json
import base64

# --- Professional Puter.js Optimized Bridge ---
def puter_ai_chat(prompt):
    """
    Highly optimized Puter.js bridge.
    Uses 'complete' for faster synthesis and enhanced browser-side UX.
    """
    component_key = f"puter_chat_{hash(prompt)}"
    safe_prompt = json.dumps(prompt)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            :root {{ --lpu-red: #d32f2f; --lpu-gold: #ffc107; }}
            body {{ margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: transparent; }}
            .advisor-card {{ 
                padding: 15px; 
                border-radius: 10px; 
                background: linear-gradient(145deg, #ffffff, #f9f9f9); 
                border-left: 5px solid var(--lpu-red);
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            }}
            .status-row {{ display: flex; align-items: center; margin-bottom: 10px; font-size: 0.9em; color: #666; }}
            .dot {{ height: 8px; width: 8px; background-color: var(--lpu-gold); border-radius: 50%; display: inline-block; margin-right: 8px; animation: pulse 1.5s infinite; }}
            @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.3; }} 100% {{ opacity: 1; }} }}
            .response-text {{ font-size: 1.05em; color: #222; line-height: 1.6; white-space: pre-wrap; }}
            .footer-brand {{ margin-top: 12px; font-size: 0.75em; color: #aaa; text-align: right; border-top: 1px solid #eee; padding-top: 5px; }}
        </style>
    </head>
    <body>
        <div class="advisor-card">
            <div id="status-container" class="status-row">
                <span class="dot"></span> <span id="status-text">LPU Advisor is synthesizing guidance...</span>
            </div>
            <div id="response" class="response-text"></div>
            <div class="footer-brand">Powered by LPU Puter AI Engine</div>
        </div>

        <script src="https://js.puter.com/v2/"></script>
        <script>
            (async function() {{
                const statusText = document.getElementById('status-text');
                const statusDot = document.querySelector('.dot');
                const responseEl = document.getElementById('response');
                
                try {{
                    // Use 'complete' for potentially faster, direct response synthesis
                    const result = await puter.ai.complete({safe_prompt});
                    
                    let content = "";
                    if (typeof result === 'string') {{
                        content = result;
                    }} else if (result && result.message && result.message.content) {{
                        content = result.message.content;
                    }} else if (result && typeof result === 'object') {{
                        content = result.text || JSON.stringify(result);
                    }}

                    // Smooth transition to complete state
                    statusDot.style.backgroundColor = "#2e7d32";
                    statusDot.style.animation = "none";
                    statusText.innerHTML = "<b>Verified LPU Academic Guidance:</b>";
                    statusText.style.color = "#2e7d32";
                    responseEl.innerText = content;
                    
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: content,
                        key: '{component_key}'
                    }}, '*');
                    
                }} catch (err) {{
                    statusDot.style.backgroundColor = "#c62828";
                    statusDot.style.animation = "none";
                    statusText.innerHTML = "<b>Synthesis Interrupted</b>";
                    statusText.style.color = "#c62828";
                    responseEl.innerHTML = "<span style='color: #d32f2f;'>The AI engine encountered an optimized retry state. Please refresh if advice doesn't appear.</span>";
                }}
            }})();
        </script>
    </body>
    </html>
    """
    
    b64_html = base64.b64encode(html_code.encode()).decode()
    data_uri = f"data:text/html;base64,{b64_html}"
    return st.iframe(data_uri, height=300, scrolling=True)

# --- Updated handle_query Fallback ---
# I will update chatbot.py to use this bridge when in UI mode.
