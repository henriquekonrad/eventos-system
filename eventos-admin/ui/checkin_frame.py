# ui/checkin_frame.py
import customtkinter as ctk
import os
from db import (get_inscrito_by_cpf, add_inscrito_local, add_checkin_local, 
                add_pending, list_pending_requests)
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
        popup.grab_set()  # Modal
        
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
            
            # Salva inscrito localmente como "rápido"
            add_inscrito_local(local_id, evento_id, nome, cpf, email, sincronizado=0)
            
            # Prepara headers
            from api_client import auth_header
            headers = auth_header()
            headers["x-api-key"] = os.getenv("CHECKINS_API_KEY", "")
            
            # USA ENDPOINT /rapido - Cria TUDO: usuário temporário + inscrição + ingresso + check-in
            checkin_params = f"evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
            checkin_url = f"http://177.44.248.122:8006/rapido?{checkin_params}"
            add_pending("POST", checkin_url, {}, headers)
            
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

⚠️ Esta é uma inscrição RÁPIDA (usuário temporário)
   A pessoa pode completar o cadastro depois no site.

Os dados serão enviados ao servidor na próxima sincronização."""
            
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
            # Isso pode acontecer se:
            # - Estiver offline
            # - Ingresso/usuário ainda não foram criados no servidor
            # - Endpoint de busca não existir
            params = f"evento_id={evento_id}&nome={nome}&cpf={cpf}&email={email}"
            url = f"http://177.44.248.122:8006/rapido?{params}"
            print(f"[CHECKIN] Usando endpoint /rapido como FALLBACK")
        
        # Adiciona à fila
        add_pending("POST", url, {}, headers)
        
        # Registra localmente
        add_checkin_local(inscricao_id, ingresso_id, usuario_id, evento_id, tipo="normal", sincronizado=0)
        
        if is_online():
            self.update_info(f"""✓ CHECK-IN REGISTRADO (NORMAL)

🟢 PARTICIPANTE JÁ INSCRITO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Nome: {nome}
CPF: {cpf}
Inscrição ID: {inscricao_id}
Ingresso ID: {ingresso_id or 'Será criado no servidor'}
Usuário ID: {usuario_id or 'Será buscado no servidor'}

O check-in foi registrado e será enviado ao servidor.""")
        else:
            self.update_info(f"""✓ CHECK-IN REGISTRADO (OFFLINE)

Nome: {nome}
CPF: {cpf}

⚠️ Modo offline - O check-in será enviado quando houver conexão.
Use "Sincronizar Pendentes" quando voltar online.""")
        
        # Limpa estado
        self.found_inscricao = None
        self.checkin_btn.configure(state="disabled")
        self.cpf_var.set("")

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