import os
import streamlit as st
import streamlit.components.v1 as components
import json

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
    <div id="puter-container" style="font-family: sans-serif; padding: 10px; border-radius: 5px; background: #f0f2f6; border: 1px solid #ddd;">
        <div id="status" style="font-size: 0.85em; color: #555; margin-bottom: 5px;">
            <span class="spinner">⏳</span> AI Advisor is thinking...
        </div>
        <div id="response" style="font-size: 1em; color: #111; line-height: 1.4; white-space: pre-wrap;"></div>
    </div>

    <style>
        .spinner {{ display: inline-block; animation: rotate 2s linear infinite; }}
        @keyframes rotate {{ 100% {{ transform: rotate(360deg); }} }}
        #response:empty {{ display: none; }}
    </style>

    <script src="https://js.puter.com/v2/"></script>
    <script>
        (async function() {{
            const statusEl = document.getElementById('status');
            const responseEl = document.getElementById('response');
            
            try {{
                // Initialize Puter and call AI
                // Puter.js v2 handles guest sessions automatically in the browser
                const result = await puter.ai.chat({safe_prompt}, {{ model: 'gpt-4o' }});
                
                // Extract content safely
                let content = "";
                if (typeof result === 'string') {{
                    content = result;
                }} else if (result && result.message && result.message.content) {{
                    content = result.message.content;
                }} else {{
                    content = JSON.stringify(result);
                }}

                // Update UI
                statusEl.innerHTML = "✅ <b>LPU AI Synthesis Complete:</b>";
                statusEl.style.color = "#2e7d32";
                responseEl.innerText = content;
                
                // Streamlit component bridge (optional but good practice)
                window.parent.postMessage({{
                    type: 'streamlit:setComponentValue',
                    value: content,
                    key: '{component_key}'
                }}, '*');
                
            }} catch (err) {{
                console.error("Puter Error:", err);
                statusEl.innerHTML = "❌ <b>Synthesis Error</b>";
                statusEl.style.color = "#c62828";
                responseEl.innerHTML = "<span style='color: #d32f2f;'>Sorry, I couldn't connect to the LPU AI engine. Please check your internet connection or try again later.</span><br><small>" + err.message + "</small>";
            }}
        }})();
    </script>
    """
    
    # Render the component with enough height and scrolling
    return components.html(html_code, height=350, scrolling=True, key=component_key)

# --- Updated handle_query Fallback ---
# I will update chatbot.py to use this bridge when in UI mode.
