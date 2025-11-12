# ui/checkin_frame.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
from db import (get_inscrito_by_cpf, add_inscrito_local, add_checkin_local, 
                add_pending, list_pending_requests, delete_pending_request,
                checkin_ja_existe_local, checkin_ja_existe_por_cpf)
from api_client import is_online
import uuid

class CheckinFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.current_evento_id = None
        self.current_evento_nome = "Nenhum evento selecionado"

        # ========== TOP BAR ==========
        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=8, pady=8)

        self.event_label = ctk.CTkLabel(
            top, 
            text=self.current_evento_nome, 
            font=("Arial", 14, "bold")
        )
        self.event_label.pack(side="left", padx=8)

        btn_frame = ctk.CTkFrame(top)
        btn_frame.pack(side="right")
        
        self.sync_btn = ctk.CTkButton(
            btn_frame, 
            text="🔄 Sincronizar Pendentes", 
            command=self.sync_now,
            width=180
        )
        self.sync_btn.pack(side="left", padx=4)

        # ========== SEARCH FRAME ==========
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(search_frame, text="CPF:").pack(side="left", padx=(0,4))
        
        self.cpf_var = ctk.StringVar()
        cpf_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Digite o CPF (somente números)", 
            textvariable=self.cpf_var,
            width=300
        )
        cpf_entry.pack(side="left", padx=(0,8))

        buscar_btn = ctk.CTkButton(
            search_frame, 
            text="🔍 Buscar", 
            command=self.buscar_por_cpf,
            width=100
        )
        buscar_btn.pack(side="left", padx=4)

        # ========== QUICK REGISTRATION ==========
        rapida_btn = ctk.CTkButton(
            self, 
            text="➕ Inscrição Rápida + Check-in (sem cadastro)", 
            command=self.inscricao_rapida_prompt,
            height=40,
            fg_color="orange",
            hover_color="darkorange"
        )
        rapida_btn.pack(padx=8, pady=(4,8), fill="x")

        # ========== INFO AREA ==========
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.info_text = ctk.CTkTextbox(info_frame, height=200)
        self.info_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.info_text.insert("0.0", "Selecione um evento e busque por CPF ou faça inscrição rápida.")
        self.info_text.configure(state="disabled")

        # ========== ACTIONS ==========
        actions = ctk.CTkFrame(self)
        actions.pack(fill="x", padx=8, pady=8)
        
        self.checkin_btn = ctk.CTkButton(
            actions, 
            text="✓ Registrar Check-in (já tem inscrição)", 
            command=self.registrar_checkin_action, 
            state="disabled",
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.checkin_btn.pack(side="left", fill="x", expand=True, padx=(0,4))
        
        self.show_pending_btn = ctk.CTkButton(
            actions, 
            text="📋 Ver Pendentes", 
            command=self.mostrar_pendentes,
            height=40
        )
        self.show_pending_btn.pack(side="left", padx=4)

        # Store found inscricao
        self.found_inscricao = None

    def set_evento(self, evento_id, evento_nome="Evento"):
        """Define o evento atual para check-in"""
        self.current_evento_id = evento_id
        self.current_evento_nome = evento_nome
        self.event_label.configure(text=f"📅 {evento_nome}")
        self.update_info(f"Evento selecionado: {evento_nome}\nID: {evento_id}\n\nBusque por CPF ou faça inscrição rápida.")
        
        # Limpa busca anterior
        self.found_inscricao = None
        self.checkin_btn.configure(state="disabled")
        self.cpf_var.set("")

    def update_info(self, text):
        """Atualiza área de informações"""
        self.info_text.configure(state="normal")
        self.info_text.delete("0.0", "end")
        self.info_text.insert("0.0", text)
        self.info_text.configure(state="disabled")

    def buscar_por_cpf(self):
        """
        CENÁRIO 1: Busca participante JÁ INSCRITO no evento
        Para fazer check-in de quem já tem inscrição/conta
        """
        if not self.current_evento_id:
            self.update_info("⚠️ ERRO: Selecione um evento primeiro!")
            return
        
        cpf = self.cpf_var.get().strip()
        if not cpf:
            self.update_info("⚠️ Digite um CPF válido")
            return
        
        # Busca no banco local
        inscr = get_inscrito_by_cpf(cpf, evento_id=self.current_evento_id)
        
        if inscr:
            # VERIFICA SE JÁ TEM CHECK-IN LOCAL
            checkin_status = checkin_ja_existe_local(inscr['inscricao_id'])
            if checkin_status:
                if checkin_status['sincronizado']:
                    info = f"""✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR

Nome: {inscr['nome']}
CPF: {inscr['cpf']}
Email: {inscr['email']}

✓ Esta pessoa JÁ FEZ CHECK-IN (confirmado no servidor)
→ PODE ENTRAR NO EVENTO"""
                else:
                    info = f"""⚠️ CHECK-IN JÁ REGISTRADO (LOCALMENTE)

Nome: {inscr['nome']}
CPF: {inscr['cpf']}
Email: {inscr['email']}

✓ Esta pessoa JÁ FEZ CHECK-IN (aguardando sincronização)
→ PODE ENTRAR NO EVENTO

Sincronize as pendências para enviar ao servidor."""
                self.update_info(info)
                self.checkin_btn.configure(state="disabled")
                self.found_inscricao = None
                return
            
            self.found_inscricao = inscr
            info = f"""✓ PARTICIPANTE ENCONTRADO (JÁ TEM INSCRIÇÃO)

Nome: {inscr['nome']}
CPF: {inscr['cpf']}
Email: {inscr['email']}
ID Inscrição: {inscr['inscricao_id']}
Status: {'Sincronizado' if inscr['sincronizado'] else 'Pendente sync'}

Este participante JÁ ESTÁ INSCRITO no evento.
Clique em "Registrar Check-in" para fazer o check-in normal."""
            self.update_info(info)
            self.checkin_btn.configure(state="normal")
        else:
            self.found_inscricao = None
            self.update_info(f"""✗ PARTICIPANTE NÃO ENCONTRADO

CPF: {cpf}
Evento: {self.current_evento_nome}

Este CPF NÃO está inscrito neste evento.

OPÇÕES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 🟠 Se a pessoa NÃO TEM CADASTRO:
   → Use "Inscrição Rápida" (botão laranja)
   → Criará usuário temporário que ela pode completar depois
   
2. 🔵 Se a pessoa JÁ TEM CADASTRO no sistema:
   → Peça para ela se inscrever no evento primeiro
   → Depois sincronize os inscritos novamente
   
3. ⚙️ Verifique se o CPF está correto""")
            self.checkin_btn.configure(state="disabled")

    def inscricao_rapida_prompt(self):
        """
        CENÁRIO 2: Inscrição Rápida + Check-in
        Para pessoas que chegam SEM CADASTRO/INSCRIÇÃO
        Cria usuário temporário que pode ser completado depois
        """
        if not self.current_evento_id:
            self.update_info("⚠️ ERRO: Selecione um evento primeiro!")
            return
        
        popup = ctk.CTkToplevel(self)
        popup.title("Inscrição Rápida - Pessoa SEM cadastro")
        popup.geometry("500x380")
        
        # Aguarda a janela ser criada antes de configurar topmost e grab
        popup.update_idletasks()
        popup.attributes('-topmost', True)
        popup.focus_force()
        
        # Aguarda mais um pouco antes do grab_set
        popup.after(100, lambda: popup.grab_set())
        
        # Título explicativo
        titulo = ctk.CTkLabel(
            popup, 
            text="🟠 Inscrição Rápida\nPara pessoas que NÃO TEM cadastro no sistema",
            font=("Arial", 12, "bold"),
            text_color="orange"
        )
        titulo.pack(pady=(10,15))
        
        # Variáveis
        name_var = ctk.StringVar()
        cpf_var = ctk.StringVar(value=self.cpf_var.get())
        email_var = ctk.StringVar()

        # Campos
        ctk.CTkLabel(popup, text="Nome Completo:", font=("Arial", 11, "bold")).pack(pady=(5,2))
        ctk.CTkEntry(popup, textvariable=name_var, width=450).pack(padx=20)
        
        ctk.CTkLabel(popup, text="CPF:", font=("Arial", 11, "bold")).pack(pady=(8,2))
        ctk.CTkEntry(popup, textvariable=cpf_var, width=450).pack(padx=20)
        
        ctk.CTkLabel(popup, text="Email:", font=("Arial", 11, "bold")).pack(pady=(8,2))
        ctk.CTkEntry(popup, textvariable=email_var, width=450).pack(padx=20)
        
        # Aviso
        aviso = ctk.CTkLabel(
            popup,
            text="ℹ️ Será criado um usuário temporário.\nA pessoa poderá completar o cadastro depois no site.",
            font=("Arial", 9),
            text_color="gray"
        )
        aviso.pack(pady=(10,5))

        def submit():
            nome = name_var.get().strip()
            cpf = cpf_var.get().strip()
            email = email_var.get().strip()
            
            if not nome or not cpf or not email:
                self.update_info("⚠️ Preencha todos os campos!")
                return
            
            evento_id = self.current_evento_id
            
            # Cria ID temporário local
            local_id = str(uuid.uuid4())
            
            # VERIFICA SE JÁ EXISTE CHECK-IN LOCAL PARA ESTE CPF
            checkin_status = checkin_ja_existe_por_cpf(cpf, evento_id)
            if checkin_status:
                popup.destroy()
                if checkin_status['sincronizado']:
                    self.update_info(f"""✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR

CPF: {cpf}

✓ Esta pessoa JÁ FEZ CHECK-IN (confirmado no servidor)
→ PODE ENTRAR NO EVENTO""")
                else:
                    self.update_info(f"""⚠️ CHECK-IN JÁ REGISTRADO (LOCALMENTE)

CPF: {cpf}

✓ Esta pessoa JÁ FEZ CHECK-IN (aguardando sincronização)
→ PODE ENTRAR NO EVENTO

Sincronize as pendências para enviar ao servidor.""")
                return
            
            # Salva inscrito localmente como "rápido"
            add_inscrito_local(local_id, evento_id, nome, cpf, email, sincronizado=0)
            
            # Prepara headers
            from api_client import auth_header
            headers = auth_header()
            headers["x-api-key"] = os.getenv("CHECKINS_API_KEY", "")
            
            # USA ENDPOINT /rapido - Cria TUDO: usuário temporário + inscrição + ingresso + check-in
            checkin_params = f"evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
            checkin_url = f"http://177.44.248.122:8006/rapido?{checkin_params}"
            add_pending("POST", checkin_url, {}, headers, related_inscricao_id=local_id, related_cpf=cpf)
            
            # Registra check-in local
            add_checkin_local(local_id, None, None, evento_id, tipo="rapida", sincronizado=0)
            
            popup.destroy()
            
            info = f"""✓ INSCRIÇÃO RÁPIDA + CHECK-IN REGISTRADOS

🟠 USUÁRIO TEMPORÁRIO CRIADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nome: {nome}
CPF: {cpf}
Email: {email}
ID Local: {local_id}

Status: {'Enfileirado para sincronização' if not is_online() else 'Será sincronizado em breve'}

→ PESSOA PODE ENTRAR NO EVENTO

⚠️ Esta é uma inscrição RÁPIDA (usuário temporário)
   A pessoa pode completar o cadastro depois no site."""
            
            self.update_info(info)
            
            # Limpa estado
            self.found_inscricao = None
            self.checkin_btn.configure(state="disabled")
            self.cpf_var.set("")

        ok_btn = ctk.CTkButton(
            popup, 
            text="✓ Criar Usuário Temporário e Fazer Check-in", 
            command=submit,
            height=40,
            fg_color="orange",
            hover_color="darkorange"
        )
        ok_btn.pack(pady=15)

    def registrar_checkin_action(self):
        """
        CENÁRIO 3: Check-in Normal
        Para inscrição que JÁ EXISTE (pessoa já tinha conta/inscrição)
        """
        if not self.found_inscricao:
            self.update_info("⚠️ ERRO: Nenhuma inscrição selecionada.")
            return
        
        inscricao_id = self.found_inscricao.get("inscricao_id")
        
        # VERIFICA SE JÁ TEM CHECK-IN LOCAL
        checkin_status = checkin_ja_existe_local(inscricao_id)
        if checkin_status:
            nome = self.found_inscricao.get('nome')
            cpf = self.found_inscricao.get('cpf')
            
            if checkin_status['sincronizado']:
                self.update_info(f"""✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR

Nome: {nome}
CPF: {cpf}

✓ Esta pessoa JÁ FEZ CHECK-IN (confirmado no servidor)
→ PODE ENTRAR NO EVENTO""")
            else:
                self.update_info(f"""⚠️ CHECK-IN JÁ REGISTRADO (LOCALMENTE)

Nome: {nome}
CPF: {cpf}

✓ Esta pessoa JÁ FEZ CHECK-IN (aguardando sincronização)
→ PODE ENTRAR NO EVENTO

Sincronize as pendências para enviar ao servidor.""")
            
            self.checkin_btn.configure(state="disabled")
            return
        
        evento_id = self.found_inscricao.get("evento_id") or self.current_evento_id
        nome = self.found_inscricao.get("nome")
        cpf = self.found_inscricao.get("cpf")
        email = self.found_inscricao.get("email")
        
        # Prepara headers
        from api_client import auth_header
        headers = auth_header()
        headers["x-api-key"] = os.getenv("CHECKINS_API_KEY", "")
        
        # Tenta buscar ingresso_id e usuario_id reais SE ESTIVER ONLINE
        ingresso_id = None
        usuario_id = None
        
        if is_online():
            try:
                from api_client import buscar_ingresso_por_inscricao, buscar_usuario_por_email
                
                # Busca ingresso
                ingresso_data = buscar_ingresso_por_inscricao(inscricao_id)
                if ingresso_data:
                    ingresso_id = ingresso_data.get("id") or ingresso_data.get("ingresso_id")
                    print(f"[CHECKIN] Ingresso encontrado: {ingresso_id}")
                
                # Busca usuário
                usuario_data = buscar_usuario_por_email(email)
                if usuario_data:
                    usuario_id = usuario_data.get("id") or usuario_data.get("usuario_id")
                    print(f"[CHECKIN] Usuário encontrado: {usuario_id}")
                    
            except Exception as e:
                print(f"[CHECKIN] Erro ao buscar dados: {e}")
        
        # Monta a URL baseado nos dados disponíveis
        if ingresso_id and usuario_id:
            # TEM TODOS OS DADOS REAIS - Usa endpoint NORMAL
            params = f"inscricao_id={inscricao_id}&ingresso_id={ingresso_id}&usuario_id={usuario_id}"
            url = f"http://177.44.248.122:8006/?{params}"
            print(f"[CHECKIN] Usando endpoint NORMAL com IDs reais")
        else:
            # NÃO TEM DADOS COMPLETOS - Usa endpoint /rapido como fallback
            params = f"evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
            url = f"http://177.44.248.122:8006/rapido?{params}"
            print(f"[CHECKIN] Usando endpoint /rapido como FALLBACK")
        
        # Adiciona à fila
        add_pending("POST", url, {}, headers, related_inscricao_id=inscricao_id, related_cpf=cpf)
        
        # Registra localmente
        add_checkin_local(inscricao_id, ingresso_id, usuario_id, evento_id, tipo="normal", sincronizado=0)
        
        if is_online():
            self.update_info(f"""✓ CHECK-IN REGISTRADO (NORMAL)

🟢 PARTICIPANTE JÁ INSCRITO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nome: {nome}
CPF: {cpf}
Inscrição ID: {inscricao_id}

→ PESSOA PODE ENTRAR NO EVENTO

O check-in foi registrado e será enviado ao servidor.""")
        else:
            self.update_info(f"""✓ CHECK-IN REGISTRADO (OFFLINE)

Nome: {nome}
CPF: {cpf}

→ PESSOA PODE ENTRAR NO EVENTO

⚠️ Modo offline - O check-in será enviado quando houver conexão.""")
        
        # Limpa estado
        self.found_inscricao = None
        self.checkin_btn.configure(state="disabled")
        self.cpf_var.set("")

    def mostrar_pendentes(self):
        """Mostra lista de requisições pendentes com interface amigável"""
        pend = list_pending_requests()
        
        popup = ctk.CTkToplevel(self)
        popup.title("Requisições Aguardando Sincronização")
        popup.geometry("900x550")
        popup.attributes('-topmost', True)  # Traz janela pra frente
        popup.focus_force()
        
        # Frame principal
        main_frame = ctk.CTkFrame(popup)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        if not pend:
            # Sem pendências
            icon_label = ctk.CTkLabel(
                main_frame, 
                text="✓", 
                font=("Arial", 80),
                text_color="green"
            )
            icon_label.pack(pady=50)
            
            msg_label = ctk.CTkLabel(
                main_frame,
                text="Nenhuma operação pendente!",
                font=("Arial", 18, "bold")
            )
            msg_label.pack()
            
            desc_label = ctk.CTkLabel(
                main_frame,
                text="Todas as operações foram sincronizadas com sucesso.",
                font=("Arial", 12),
                text_color="gray"
            )
            desc_label.pack(pady=10)
        else:
            # Com pendências
            header = ctk.CTkLabel(
                main_frame,
                text=f"📋 {len(pend)} operação(ões) aguardando envio ao servidor",
                font=("Arial", 16, "bold")
            )
            header.pack(pady=(10, 15))
            
            # Frame com scroll para lista
            scroll_frame = ctk.CTkScrollableFrame(main_frame, height=350)
            scroll_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            
            for i, p in enumerate(pend, 1):
                # Card para cada requisição
                card = ctk.CTkFrame(scroll_frame)
                card.pack(fill="x", padx=5, pady=5)
                
                # Header do card
                card_header = ctk.CTkFrame(card)
                card_header.pack(fill="x", padx=10, pady=8)
                
                # Determinar tipo de operação
                url = p['url']
                if '/rapido' in url:
                    tipo = "🟠 Check-in Rápido"
                    cor = "orange"
                elif '/8006/' in url:
                    tipo = "🟢 Check-in Normal"
                    cor = "green"
                elif '/8004/' in url:
                    tipo = "📝 Inscrição"
                    cor = "blue"
                else:
                    tipo = "📤 Operação"
                    cor = "gray"
                
                tipo_label = ctk.CTkLabel(
                    card_header,
                    text=f"#{i} - {tipo}",
                    font=("Arial", 13, "bold"),
                    text_color=cor
                )
                tipo_label.pack(side="left")
                
                # Botão remover
                remove_btn = ctk.CTkButton(
                    card_header,
                    text="🗑️ Remover",
                    width=100,
                    height=28,
                    fg_color="red",
                    hover_color="darkred",
                    command=lambda pid=p['id']: self.remover_pendente(pid, popup)
                )
                remove_btn.pack(side="right")
                
                # Detalhes do card
                details_frame = ctk.CTkFrame(card, fg_color="transparent")
                details_frame.pack(fill="x", padx=15, pady=(0, 10))
                
                # Extrair informações da URL
                info_text = self._extrair_info_url(url)
                
                info_label = ctk.CTkLabel(
                    details_frame,
                    text=info_text,
                    font=("Arial", 11),
                    justify="left",
                    anchor="w"
                )
                info_label.pack(fill="x", pady=2)
                
                # Data
                data_label = ctk.CTkLabel(
                    details_frame,
                    text=f"⏰ Criado em: {p['created_at'][:19]}",
                    font=("Arial", 9),
                    text_color="gray"
                )
                data_label.pack(anchor="w", pady=(5, 0))
        
        # Botão fechar
        close_btn = ctk.CTkButton(
            popup,
            text="Fechar",
            command=popup.destroy,
            height=40
        )
        close_btn.pack(pady=(0, 15))
    
    def _extrair_info_url(self, url):
        """Extrai informações legíveis da URL para o atendente"""
        import urllib.parse
        
        # Parse da URL
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        info_parts = []
        
        if 'nome' in params:
            info_parts.append(f"👤 Nome: {params['nome'][0]}")
        if 'cpf' in params:
            info_parts.append(f"📄 CPF: {params['cpf'][0]}")
        if 'email' in params:
            info_parts.append(f"📧 Email: {params['email'][0]}")
        if 'inscricao_id' in params:
            info_parts.append(f"🎫 Inscrição: {params['inscricao_id'][0][:8]}...")
        
        return "\n".join(info_parts) if info_parts else "Detalhes da operação"
    
    def remover_pendente(self, request_id, popup_window):
        """Remove uma requisição pendente após confirmação E LIMPA DADOS RELACIONADOS"""
        resposta = messagebox.askyesno(
            "Confirmar Remoção",
            "Tem certeza que deseja remover esta operação?\n\n"
            "⚠️ Ela não será enviada ao servidor!\n"
            "Os dados locais relacionados também serão removidos.\n\n"
            "Use apenas se foi registrada por engano.",
            parent=popup_window
        )
        
        if resposta:
            from db import delete_checkin_local, delete_inscrito_local, get_inscrito_by_id
            
            # Remove a pendência e obtém informações relacionadas
            info = delete_pending_request(request_id)
            
            # LIMPA DADOS LOCAIS RELACIONADOS
            if info and info['inscricao_id']:
                # Remove check-in local
                delete_checkin_local(info['inscricao_id'])
                
                # Verifica se é inscrição LOCAL (não sincronizada)
                inscrito = get_inscrito_by_id(info['inscricao_id'])
                if inscrito and inscrito['sincronizado'] == 0:
                    # É inscrição local/rápida - pode remover
                    delete_inscrito_local(info['inscricao_id'])
                    print(f"[UI] Inscrito local {info['inscricao_id']} também removido")
                else:
                    # É inscrição do servidor - NÃO remove!
                    print(f"[UI] Inscrito {info['inscricao_id']} é do servidor, mantendo")
            
            popup_window.destroy()
            self.mostrar_pendentes()  # Reabre com lista atualizada
            self.update_info("✓ Operação removida da fila de sincronização.\n\n✓ Dados locais relacionados também foram limpos.\n\nAgora você pode registrar o check-in novamente.")

    def sync_now(self):
        """Executa sincronização de pendentes com tratamento inteligente de erros"""
        from sync_manager import process_pending_smart
        
        self.update_info("🔄 Sincronizando requisições pendentes...\n\nAguarde...")
        self.update()  # Force UI update
        
        try:
            resultado = process_pending_smart()
            
            # Monta mensagem baseada no resultado
            mensagem = "🔄 RESULTADO DA SINCRONIZAÇÃO\n\n"
            
            if resultado['sucesso'] > 0:
                mensagem += f"✓ {resultado['sucesso']} operação(ões) sincronizada(s)\n\n"
            
            if resultado['ja_feito'] > 0:
                mensagem += f"ℹ️ {resultado['ja_feito']} check-in(s) já realizado(s)\n"
                mensagem += "→ Essas pessoas podem entrar normalmente\n\n"
            
            if resultado['removidos'] > 0:
                mensagem += f"🗑️ {resultado['removidos']} erro(s) permanente(s) removido(s)\n\n"
            
            if resultado['falhas'] > 0:
                mensagem += f"⚠️ {resultado['falhas']} operação(ões) ainda pendente(s)\n"
                mensagem += "→ Serão reenviadas na próxima sincronização\n\n"
            
            # Verifica se ainda tem pendentes
            pend = list_pending_requests()
            if not pend:
                mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                mensagem += "✓ Todas as operações foram processadas!"
            else:
                mensagem += "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                mensagem += f"📋 {len(pend)} operação(ões) ainda na fila"
            
            self.update_info(mensagem)
                
        except Exception as e:
            self.update_info(f"✗ ERRO NA SINCRONIZAÇÃO\n\n{str(e)}\n\nVerifique sua conexão e tente novamente.")