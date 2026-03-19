# --- LOOP INFINITO BLINDADO (SEM PISCAR) ---
placeholder = st.empty()

while True:
    try:
        tz_sp = pytz.timezone('America/Sao_Paulo')
        tz_ny = pytz.timezone('America/New_York')
        tz_ld = pytz.timezone('Europe/London')
        
        # 1. Busca os dados PRIMEIRO (O Streamlit não limpa a tela enquanto espera o Yahoo)
        ewz_live = fetch("EWZ")
        res = calcular_k97_total(a_ewz, ewz_live['at'], ewz_live['mx'], ewz_live['mn'], a_dol)

        if res:
            # 2. MONTANDO O HTML EM MEMÓRIA (Buffer)
            # Vamos criar blocos de texto para não dar erro de indentação
            
            header_html = f"""
            <div class="header-bair">
                <div class="title-box">
                    <span class="bair-text">BAIR</span><span class="sep-text">-</span><span class="terminal-text">TERMINAL DOLLAR</span>
                </div>
                <div class="clock-container">
                    <div class="clock-box"><span class="clock-label">BRASÍLIA</span><span class="clock-time">{datetime.now(tz_sp).strftime('%H:%M:%S')}</span></div>
                    <div class="clock-box"><span class="clock-label">NEW YORK</span><span class="clock-time">{datetime.now(tz_ny).strftime('%H:%M:%S')}</span></div>
                    <div class="clock-box"><span class="clock-label">LONDRES</span><span class="clock-time">{datetime.now(tz_ld).strftime('%H:%M:%S')}</span></div>
                </div>
            </div>"""

            # Lógica da Tabela
            v_v = ((res['vivo']/a_dol)-1)*100 if a_dol > 0 else 0
            cor_v = "#00ff00" if v_v >= 0 else "#ff4d4d"
            
            table_html = f"""
            <div class="main-grid">
                <table class="terminal-table">
                    <thead>
                        <tr><th>Ativo</th><th style='color: #d4a017;'>Price</th><th style='color: #d4a017;'>Close</th><th>Open</th><th>Max</th><th>Min</th><th>Var</th></tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class='asset-name'>DOLFUT</td>
                            <td class='price-col'>{(res['vivo']/1000):.4f}</td>
                            <td>{(a_dol/1000):.4f}</td>
                            <td>{(a_dol/1000):.4f}</td>
                            <td>{(res['max']/1000):.4f}</td>
                            <td>{(res['min']/1000):.4f}</td>
                            <td style='color:{cor_v}; font-weight:bold;'>{v_v:+.2f}%</td>
                        </tr>"""

            ticker_items = [f"<span style='color:#fff;'>DOLFUT:</span> <span style='color:{cor_v};'>{v_v:+.2f}%</span>"]
            
            outros = {"DOLSPOT": "USDBRL=X", "DXY": "DX-Y.NYB", "EWZ": "EWZ", "GBP/USD": "GBPUSD=X", "JPY/USD": "JPYUSD=X", "EUR/USD": "EURUSD=X", "XAU/USD": "GC=F", "PETROLEO BRENT": "BZ=F"}
            
            for lbl, sym in outros.items():
                d = fetch(sym)
                f = ".4f" if lbl in ["DOLSPOT", "DOLFUT"] or "USD" in lbl else ".2f"
                var = ((d['at'] / d['cl']) - 1) * 100 if d['cl'] > 0 else 0
                color = "#00ff00" if var >= 0 else "#ff4d4d"
                table_html += f"<tr><td class='asset-name'>{lbl}</td><td class='price-col'>{d['at']:{f}}</td><td>{d['cl']:{f}}</td><td>{d['op']:{f}}</td><td>{d['mx']:{f}}</td><td>{d['mn']:{f}}</td><td style='color:{color}; font-weight:bold;'>{var:+.2f}%</td></tr>"
                ticker_items.append(f"<span style='color:#fff;'>{lbl}:</span> <span style='color:{color};'>{var:+.2f}%</span>")
            
            table_html += "</tbody></table></div>"

            # Painéis Laterais
            side_html = f"""
            <div class="calc-panel">
                <div class="calc-row" style="color:#ff4d4d;"><span>MÁXIMA</span> <span>{res['max']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>75%</span> <span>{res['p75_up']:.2f}</span></div>
                <div class="calc-row" style="color:#ffa500;"><span>1ª MAX</span> <span>{res['p50_up']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>25%</span> <span>{res['p25_up']:.2f}</span></div>
                <div style="text-align:center; padding: 10px; color: #00f2ff; font-size: 18px; font-weight: bold; border-top:1.5px solid #444; border-bottom:1.5px solid #444; margin: 5px 0;">AXIS: {a_dol:.2f}</div>
                <div class="calc-row" style="color:#ffff00;"><span>-25%</span> <span>{res['p25_down']:.2f}</span></div>
                <div class="calc-row" style="color:#ffa500;"><span>1ª MIN</span> <span>{res['p50_down']:.2f}</span></div>
                <div class="calc-row" style="color:#ffff00;"><span>-75%</span> <span>{res['p75_down']:.2f}</span></div>
                <div class="calc-row" style="color:#00ff88; border-bottom: none;"><span>MÍNIMA</span> <span>{res['min']:.2f}</span></div>
            </div>
            <div class="calc-panel">
                <div class="calc-row" style="padding: 10px 8px;"><span style="color:#ffffff;">DOLFUT</span> <span style="color:#00f2ff; font-size: 16px; font-weight: 950;">{res['vivo']:.2f}</span></div>
                <div class="calc-row"><span style="color:#ffff00;">MÉDIA DOL</span> <span style="color:#00f2ff; font-size: 16px;">{res['medio']:.2f}</span></div>
                <div class="calc-row" style="border-bottom: none;"><span style="color:#d4a017;">P. JUSTO</span> <span style="color:#ffffff; font-size: 16px; font-weight: bold;">{res['fraja']:.2f}</span></div>
                <div class="ewz-mini-container">
                    <span class="ewz-mini-val" style="color:#00ff88;">{ewz_live['mx']:.2f}</span>
                    <span class="ewz-mini-val" style="color:#00f2ff;">{res['ewz_med']:.2f}</span>
                    <span class="ewz-mini-val" style="color:#ff4d4d;">{ewz_live['mn']:.2f}</span>
                </div>
            </div>"""

            ticker_html = f'<div class="ticker-wrapper"><div class="ticker-text">{" • ".join(ticker_items)} • {" • ".join(ticker_items)}</div></div>'

            # 3. ÚNICO MOMENTO EM QUE TOCAMOS NA TELA (Troca instantânea)
            with placeholder.container():
                st.markdown(header_html, unsafe_allow_html=True)
                col_left, col_right = st.columns([3, 1])
                col_left.markdown(table_html, unsafe_allow_html=True)
                col_right.markdown(side_html, unsafe_allow_html=True)
                st.markdown(ticker_html, unsafe_allow_html=True)

        time.sleep(1) 
    except Exception as e:
        time.sleep(2)
