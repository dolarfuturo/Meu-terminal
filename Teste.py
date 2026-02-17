            for t, info in COINS_CONFIG.items():
                price = yf.Ticker(t).fast_info['last_price']
                mp, rv = st.session_state[f'mp_{t}'], st.session_state[f'rv_{t}']
                
                # Definição de Parâmetros de Volatilidade e Régua
                if t in ["BTC-USD", "ETH-USD"]:
                    g_ex, g_mov, g_dec, g_res, label_regua = 1.22, 1.0122, 1.0061, 1.0040, "1.22%"
                else:
                    g_ex, g_mov, g_dec, g_res, label_regua = 2.44, 1.0244, 1.0122, 1.0080, "2.44%"

                # Lógica de Escada (Update da Âncora)
                var_escada = ((price / mp) - 1) * 100
                if var_escada >= g_ex: 
                    st.session_state[f'mp_{t}'] = mp * g_mov
                elif var_escada <= -g_ex: 
                    st.session_state[f'mp_{t}'] = mp * (2 - g_mov)
                
                # Dados Visuais e Alertas (Blink)
                var_reset = ((price / rv) - 1) * 100
                cor_v, seta_v = ("#00FF00", "▲") if var_reset >= 0 else ("#FF4444", "▼")
                abs_v = abs(var_escada)
                
                # Destaque para Decisão de Amortização
                fundo_d = "background: rgba(255, 255, 0, 0.15);" if (g_ex*0.44 <= abs_v <= g_ex*0.48) else ""
                blink_t = "animation: blink 0.4s infinite;" if (g_ex*0.88 <= var_escada < g_ex) else ""
                blink_f = "animation: blink 0.4s infinite;" if (-g_ex < var_escada <= -g_ex*0.88) else ""

                st.markdown(f"""
                    <div class="row-container">
                        <div class="w-col" style="color:#D4AF37;">{info['label']}</div>
                        <div class="w-col">
                            <div style="font-weight: bold
