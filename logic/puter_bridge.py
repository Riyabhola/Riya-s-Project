import streamlit as st
import json
import base64

# --- Professional Puter.js Bridge ---
def puter_ai_chat(prompt):
    """
    Seamlessly calls Puter.js in the browser. 
    Bypasses API keys by leveraging Puter's anonymous guest sessions.
    Now with active UI feedback and robust error handling.
    """
    component_key = f"puter_chat_{hash(prompt)}"
    
    # Use json.dumps for safe JS string injection
    safe_prompt = json.dumps(prompt)
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .spinner {{ display: inline-block; animation: rotate 2s linear infinite; }}
            @keyframes rotate {{ 100% {{ transform: rotate(360deg); }} }}
            #response:empty {{ display: none; }}
        </style>
    </head>
    <body style="margin: 0; font-family: sans-serif;">
        <div id="puter-container" style="padding: 10px; border-radius: 5px; background: #f0f2f6; border: 1px solid #ddd;">
            <div id="status" style="font-size: 0.85em; color: #555; margin-bottom: 5px;">
                <span class="spinner">⏳</span> AI Advisor is thinking...
            </div>
            <div id="response" style="font-size: 1em; color: #111; line-height: 1.4; white-space: pre-wrap;"></div>
        </div>

        <script src="https://js.puter.com/v2/"></script>
        <script>
            (async function() {{
                const statusEl = document.getElementById('status');
                const responseEl = document.getElementById('response');
                
                try {{
                    const result = await puter.ai.chat({safe_prompt}, {{ model: 'gpt-4o' }});
                    
                    let content = "";
                    if (typeof result === 'string') {{
                        content = result;
                    }} else if (result && result.message && result.message.content) {{
                        content = result.message.content;
                    }} else {{
                        content = JSON.stringify(result);
                    }}

                    statusEl.innerHTML = "✅ <b>LPU AI Synthesis Complete:</b>";
                    statusEl.style.color = "#2e7d32";
                    responseEl.innerText = content;
                    
                    window.parent.postMessage({{
                        type: 'streamlit:setComponentValue',
                        value: content,
                        key: '{component_key}'
                    }}, '*');
                    
                }} catch (err) {{
                    console.error("Puter Error:", err);
                    statusEl.innerHTML = "❌ <b>Synthesis Error</b>";
                    statusEl.style.color = "#c62828";
                    responseEl.innerHTML = "<span style='color: #d32f2f;'>Sorry, I couldn't connect to the LPU AI engine.</span><br><small>" + err.message + "</small>";
                }}
            }})();
        </script>
    </body>
    </html>
    """
    
    # Encode HTML to base64 for st.iframe (Modern Streamlit approach)
    b64_html = base64.b64encode(html_code.encode()).decode()
    data_uri = f"data:text/html;base64,{b64_html}"
    
    # Render using the modern st.iframe to avoid deprecation warnings
    return st.iframe(data_uri, height=350, scrolling=True)

# --- Updated handle_query Fallback ---
# I will update chatbot.py to use this bridge when in UI mode.
