# ... (mantenha o restante do código igual até o loop)

    if d_m["last"] > 0:
        # --- LÓGICA DE ARREDONDAMENTO 0.5 PONTOS ---
        # Arredonda para o 0.5 mais próximo (Ex: 5.3953 -> 5.3955)
        spot_raw = s_m["last"]
        spot = round(spot_raw * 200) / 200 
        
        # Arredonda o Fechamento Anterior SEMPRE para baixo (Ex: 5.3957 -> 5.3955)
        prev_raw = s_m["prev"]
        prev_display = (prev_raw * 200 // 1) / 200
        
        # -------------------------------------------
        
        spr = d_m["var"] - e_m["var"]
        # Justo e Equilíbrio já seguem lógica de ticks no seu código original
        justo = round((spot + 0.0310) * 2000) / 2000
        equilibrio = round((v_global["ref"] + 0.0220) * 2000) / 2000
        
        diff = spot - justo
        if diff < -0.0015: clr, arr = "#00aa55", "▲ ▲ ▲ ▲ ▲"
        elif diff > 0.0015: clr, arr = "#aa3333", "▼ ▼ ▼ ▼ ▼"
        else: clr, arr = "#aaaa00", "◄ ◄ ◄ ► ► ►"
            
        with ui_area.container():
            # ... (parte do ADM ignorada para brevidade)

            st.markdown(f'<div class="t-header"><div class="t-title">TERMINAL <span class="t-bold">DOLAR</span></div></div>', unsafe_allow_html=True)
            
            # CABEÇALHO COM ARREDONDAMENTO DE 0.5 PONTOS
            st.markdown(f"""
            <div class="s-container" style="border-bottom: 2px solid {clr}77">
                <div class="s-text" style="color:#fff">
                    SPOT {spot:.4f} <span style="color:{clr}; margin-left:10px;">({s_m['var']:+.2f}%)</span>
                </div>
                <div class="s-subtext">FECH. ANTERIOR: {prev_display:.4f}</div>
            </div>
            """, unsafe_allow_html=True)
            
# ... (segue o restante do código igual)
