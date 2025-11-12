# ui/checkin_frame.py
import customtkinter as ctk
from db import (get_inscrito_by_cpf, add_inscrito_local, add_checkin_local, 
                add_pending, list_pending_requests)
from api_client import inscricao_rapida, registrar_checkin, is_online
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
            text="➕ Inscrição Rápida + Check-in", 
            command=self.inscricao_rapida_prompt,
            height=40
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
            text="✓ Registrar Check-in", 
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
        """Busca participante por CPF no evento atual"""
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
            self.found_inscricao = inscr
            info = f"""✓ PARTICIPANTE ENCONTRADO

Nome: {inscr['nome']}
CPF: {inscr['cpf']}
Email: {inscr['email']}
ID Inscrição: {inscr['inscricao_id']}
Status: {'Sincronizado' if inscr['sincronizado'] else 'Pendente sync'}

Clique em "Registrar Check-in" para fazer o check-in."""
            self.update_info(info)
            self.checkin_btn.configure(state="normal")
        else:
            self.found_inscricao = None
            self.update_info(f"""✗ PARTICIPANTE NÃO ENCONTRADO

CPF: {cpf}
Evento: {self.current_evento_nome}

Este CPF não está inscrito neste evento (localmente).

Opções:
1. Use "Inscrição Rápida + Check-in" para cadastrar
2. Sincronize os inscritos do evento novamente
3. Verifique se o CPF está correto""")
            self.checkin_btn.configure(state="disabled")

    def inscricao_rapida_prompt(self):
        """Popup para inscrição rápida + check-in"""
        if not self.current_evento_id:
            self.update_info("⚠️ ERRO: Selecione um evento primeiro!")
            return
        
        popup = ctk.CTkToplevel(self)
        popup.title("Inscrição Rápida + Check-in")
        popup.geometry("450x300")
        popup.grab_set()  # Modal
        
        # Variáveis
        name_var = ctk.StringVar()
        cpf_var = ctk.StringVar(value=self.cpf_var.get())
        email_var = ctk.StringVar()

        # Campos
        ctk.CTkLabel(popup, text="Nome Completo:", font=("Arial", 12, "bold")).pack(pady=(15,2))
        ctk.CTkEntry(popup, textvariable=name_var, width=400).pack(padx=20)
        
        ctk.CTkLabel(popup, text="CPF:", font=("Arial", 12, "bold")).pack(pady=(10,2))
        ctk.CTkEntry(popup, textvariable=cpf_var, width=400).pack(padx=20)
        
        ctk.CTkLabel(popup, text="Email:", font=("Arial", 12, "bold")).pack(pady=(10,2))
        ctk.CTkEntry(popup, textvariable=email_var, width=400).pack(padx=20)

        def submit():
            nome = name_var.get().strip()
            cpf = cpf_var.get().strip()
            email = email_var.get().strip()
            
            if not nome or not cpf or not email:
                self.update_info("⚠️ Preencha todos os campos!")
                return
            
            evento_id = self.current_evento_id
            
            # Cria ID temporário local (será substituído na sync)
            local_id = str(uuid.uuid4())
            
            # Salva inscrito localmente (não sincronizado)
            add_inscrito_local(local_id, evento_id, nome, cpf, email, sincronizado=0)
            
            # Adiciona requisição de inscrição rápida à fila
            inscricao_body = {
                "evento_id": evento_id,
                "nome_rapido": nome,
                "cpf_rapido": cpf,
                "email_rapido": email
            }
            add_pending("POST", "http://177.44.248.122:8004/rapida", inscricao_body)
            
            # Registra check-in local imediato
            add_checkin_local(local_id, None, None, evento_id, tipo="rapida", sincronizado=0)
            
            # Adiciona requisição de check-in à fila (usando endpoint /rapido)
            checkin_params = f"evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
            checkin_url = f"http://177.44.248.122:8006/rapido?{checkin_params}"
            add_pending("POST", checkin_url, {})
            
            popup.destroy()
            
            info = f"""✓ INSCRIÇÃO RÁPIDA + CHECK-IN REGISTRADOS

Nome: {nome}
CPF: {cpf}
Email: {email}
ID Local: {local_id}

Status: {'Enviado ao servidor' if is_online() else 'Enfileirado para sincronização'}

{"Os dados foram salvos e enviados!" if is_online() else "Os dados serão enviados quando houver conexão."}"""
            
            self.update_info(info)
            
            # Atualiza estado
            self.found_inscricao = {
                "inscricao_id": local_id,
                "nome": nome,
                "cpf": cpf,
                "email": email,
                "evento_id": evento_id,
                "sincronizado": 0
            }
            self.checkin_btn.configure(state="disabled")  # Já fez check-in

        ok_btn = ctk.CTkButton(
            popup, 
            text="✓ Confirmar e Fazer Check-in", 
            command=submit,
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        ok_btn.pack(pady=20)

    def registrar_checkin_action(self):
        """Registra check-in para inscrição encontrada"""
        if not self.found_inscricao:
            self.update_info("⚠️ ERRO: Nenhuma inscrição selecionada.")
            return
        
        inscricao_id = self.found_inscricao.get("inscricao_id")
        evento_id = self.found_inscricao.get("evento_id") or self.current_evento_id
        
        # Tenta registrar check-in
        if is_online():
            try:
                # Usa endpoint de check-in normal
                # Parâmetros: inscricao_id, ingresso_id (opcional), usuario_id (opcional)
                params_url = f"http://177.44.248.122:8006/?inscricao_id={inscricao_id}"
                
                # Adiciona à fila (mesmo online, para ter histórico)
                add_pending("POST", params_url, {})
                
                # Registra localmente
                add_checkin_local(inscricao_id, None, None, evento_id, tipo="normal", sincronizado=0)
                
                self.update_info(f"""✓ CHECK-IN REGISTRADO

Nome: {self.found_inscricao.get('nome')}
CPF: {self.found_inscricao.get('cpf')}
Inscrição ID: {inscricao_id}

O check-in foi registrado e {'enviado ao servidor' if is_online() else 'será enviado quando houver conexão'}.""")
                
                self.checkin_btn.configure(state="disabled")
                
            except Exception as e:
                self.update_info(f"⚠️ Erro ao registrar: {e}\n\nCheck-in salvo localmente para sincronização.")
        else:
            # Offline: apenas enfileira
            params_url = f"http://177.44.248.122:8006/?inscricao_id={inscricao_id}"
            add_pending("POST", params_url, {})
            add_checkin_local(inscricao_id, None, None, evento_id, tipo="normal", sincronizado=0)
            
            self.update_info(f"""✓ CHECK-IN REGISTRADO (OFFLINE)

Nome: {self.found_inscricao.get('nome')}
CPF: {self.found_inscricao.get('cpf')}

⚠️ Modo offline - O check-in será enviado quando houver conexão.
Use "Sincronizar Pendentes" quando voltar online.""")
            
            self.checkin_btn.configure(state="disabled")

    def mostrar_pendentes(self):
        """Mostra lista de requisições pendentes"""
        pend = list_pending_requests()
        
        if not pend:
            text = "✓ Nenhuma requisição pendente!\n\nTodas as operações foram sincronizadas."
        else:
            text = f"📋 REQUISIÇÕES PENDENTES ({len(pend)})\n\n"
            for p in pend:
                text += f"ID: {p['id']}\n"
                text += f"Método: {p['method']}\n"
                text += f"URL: {p['url']}\n"
                text += f"Criado em: {p['created_at']}\n"
                text += "-" * 50 + "\n\n"
        
        popup = ctk.CTkToplevel(self)
        popup.title("Requisições Pendentes")
        popup.geometry("700x400")
        
        textbox = ctk.CTkTextbox(popup)
        textbox.pack(fill="both", expand=True, padx=10, pady=10)
        textbox.insert("0.0", text)
        textbox.configure(state="disabled")
        
        btn = ctk.CTkButton(popup, text="Fechar", command=popup.destroy)
        btn.pack(pady=10)

    def sync_now(self):
        """Executa sincronização de pendentes"""
        from sync_manager import process_pending
        
        self.update_info("🔄 Sincronizando requisições pendentes...\n\nAguarde...")
        self.update()  # Force UI update
        
        try:
            process_pending()
            
            # Verifica quantos ainda restam
            pend = list_pending_requests()
            
            if not pend:
                self.update_info("✓ SINCRONIZAÇÃO CONCLUÍDA!\n\nTodas as requisições foram processadas com sucesso.")
            else:
                self.update_info(f"⚠️ SINCRONIZAÇÃO PARCIAL\n\n{len(pend)} requisições ainda pendentes.\nVerifique os logs para mais detalhes.")
                
        except Exception as e:
            self.update_info(f"✗ ERRO NA SINCRONIZAÇÃO\n\n{str(e)}\n\nVerifique sua conexão e tente novamente.")