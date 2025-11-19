import customtkinter as ctk
from config.settings import UIConfig
from services.checkin_service import CheckinService
from services.sync_service import SyncService
from repositories.inscrito_repository import InscritoRepository
from views.components.inscricao_rapida_dialog import InscricaoRapidaDialog
from views.components.pending_dialog import PendingDialog

class CheckinView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.checkin_service = CheckinService()
        self.sync_service = SyncService()
        self.inscrito_repo = InscritoRepository()
        
        self.current_evento_id = None
        self.current_evento_nome = "Nenhum evento selecionado"
        self.found_inscricao = None

        self.cpf_entry = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        self._create_top_bar()
        self._create_search_frame()
        self._create_info_area()
        self._create_action_buttons()
    
    def _create_top_bar(self):
        """Barra superior"""
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
            text="Sincronizar Pendentes", 
            command=self._on_sync_click,
            width=180
        )
        self.sync_btn.pack(side="left", padx=4)
    
    def _create_search_frame(self):
        """Frame de busca"""
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=8, pady=8)

        ctk.CTkLabel(search_frame, text="CPF:").pack(side="left", padx=(0,4))
        
        self.cpf_entry = ctk.CTkEntry(
            search_frame, 
            placeholder_text="Digite o CPF (somente números)", 
            width=300
        )
        self.cpf_entry.pack(side="left", padx=(0,8))
        
        # Bind Enter key
        self.cpf_entry.bind("<Return>", lambda e: self._on_search_click())

        buscar_btn = ctk.CTkButton(
            search_frame, 
            text="Buscar", 
            command=self._on_search_click,
            width=100
        )
        buscar_btn.pack(side="left", padx=4)
    
    def _create_info_area(self):
        """Informações"""
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="both", expand=True, padx=8, pady=8)
        
        self.info_text = ctk.CTkTextbox(info_frame, height=200, font=("Arial", 12))
        self.info_text.pack(fill="both", expand=True, padx=8, pady=8)
        self.info_text.insert("0.0", "Selecione um evento e busque por CPF.")
        self.info_text.configure(state="disabled")
    
    def _create_action_buttons(self):
        """Botões de ação"""
        actions = ctk.CTkFrame(self)
        actions.pack(fill="x", padx=8, pady=8)
        
        # Botão CHECK-IN NORMAL (verde) - para quem JÁ TEM INSCRIÇÃO
        self.checkin_btn = ctk.CTkButton(
            actions, 
            text="✓ Check-in Normal (JÁ INSCRITO)", 
            command=self._on_checkin_click, 
            state="disabled",
            height=50,
            font=("Arial", 13, "bold"),
            fg_color=UIConfig.COLOR_SUCCESS,
            hover_color="darkgreen"
        )
        self.checkin_btn.pack(fill="x", padx=4, pady=(0, 8))
        
        # Separador visual
        separator = ctk.CTkFrame(actions, height=2, fg_color="gray")
        separator.pack(fill="x", padx=4, pady=8)
        
        # Botão INSCRIÇÃO RÁPIDA (laranja) - para quem NÃO TEM CADASTRO
        self.rapida_btn = ctk.CTkButton(
            actions, 
            text="⚡ Inscrição Rápida + Check-in (SEM CADASTRO)", 
            command=self._on_quick_registration_click,
            height=50,
            font=("Arial", 13, "bold"),
            fg_color=UIConfig.COLOR_RAPIDA,
            hover_color="darkorange"
        )
        self.rapida_btn.pack(fill="x", padx=4, pady=(0, 8))
        
        # Botão Ver Pendentes
        self.show_pending_btn = ctk.CTkButton(
            actions, 
            text="Ver Pendentes", 
            command=self._on_show_pending_click,
            height=35
        )
        self.show_pending_btn.pack(fill="x", padx=4)
    
    def _on_search_click(self):
        """Handler: Busca por CPF"""
        if not self.current_evento_id:
            self._update_info("❌ ERRO: Selecione um evento primeiro!")
            return
        
        cpf = self.cpf_entry.get().strip()
        if not cpf:
            self._update_info("⚠️ Digite um CPF válido")
            return
        
        print(f"[VIEW] Buscando CPF: {cpf}")
        
        # Busca inscrito
        inscrito = self.inscrito_repo.find_by_cpf(cpf, self.current_evento_id)
        
        if not inscrito:
            self._show_participante_nao_encontrado(cpf)
            return
        
        # Verifica check-in
        checkin_status = self.checkin_service.verificar_checkin_existente(inscrito['inscricao_id'])
        
        if checkin_status:
            self._show_checkin_ja_existe(inscrito, checkin_status['sincronizado'])
            return
        
        # Participante encontrado, pode fazer check-in
        self._show_participante_encontrado(inscrito)
    
    def _on_checkin_click(self):
        """Handler: Registra check-in normal (para quem JÁ TEM INSCRIÇÃO)"""
        if not self.found_inscricao:
            self._update_info("❌ ERRO: Nenhuma inscrição selecionada.")
            return
        
        print(f"[VIEW] Registrando check-in normal para: {self.found_inscricao['nome']}")
        
        sucesso, mensagem = self.checkin_service.registrar_checkin_normal(
            inscricao_id=self.found_inscricao['inscricao_id'],
            evento_id=self.current_evento_id,
            nome=self.found_inscricao['nome'],
            cpf=self.found_inscricao['cpf'],
            email=self.found_inscricao['email']
        )
        
        self._update_info(mensagem)
        
        if sucesso:
            self._limpar_estado()
    
    def _on_quick_registration_click(self):
        """Handler: Abre dialog de inscrição rápida (para quem NÃO TEM CADASTRO)"""
        if not self.current_evento_id:
            self._update_info("❌ ERRO: Selecione um evento primeiro!")
            return
        
        # Pega CPF digitado (se houver) para pré-preencher
        cpf_inicial = self.cpf_entry.get().strip()
        
        print(f"[VIEW] Abrindo dialog de inscrição rápida")
        
        dialog = InscricaoRapidaDialog(
            parent=self,
            evento_id=self.current_evento_id,
            cpf_inicial=cpf_inicial,
            on_success=self._on_quick_registration_success
        )
        dialog.show()
    
    def _on_sync_click(self):
        """Handler: Sincroniza pendentes"""
        self._update_info("🔄 Sincronizando requisições pendentes...\n\nAguarde...")
        self.update()
        
        resultado = self.sync_service.processar_pendentes()
        
        mensagem = self._formatar_resultado_sync(resultado)
        self._update_info(mensagem)
    
    def _on_show_pending_click(self):
        """Handler: Mostra pendentes"""
        dialog = PendingDialog(
            parent=self,
            on_remove=self._on_pending_removed
        )
        dialog.show()
    
    def _on_quick_registration_success(self, mensagem: str):
        """Inscrição rápida concluída"""
        self._update_info(mensagem)
        self._limpar_estado()
    
    def _on_pending_removed(self, request_id: int):
        """Pendência removida"""
        self._update_info("✓ Operação removida da fila.")
    
    
    def _show_participante_encontrado(self, inscrito: dict):
        """Exibe informações do participante encontrado"""
        self.found_inscricao = inscrito
        
        # Verifica se é cadastro completo ou temporário
        tipo_cadastro = "COMPLETO" if inscrito['sincronizado'] else "TEMPORÁRIO/LOCAL"
        
        info = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ PARTICIPANTE ENCONTRADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nome: {inscrito['nome']}
CPF: {inscrito['cpf']}
Email: {inscrito['email']}
Tipo: {tipo_cadastro}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTE PARTICIPANTE JÁ ESTÁ INSCRITO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Clique no botão VERDE para fazer 
  o check-in normal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        self._update_info(info)
        self.checkin_btn.configure(state="normal")
    
    def _show_participante_nao_encontrado(self, cpf: str):
        """Exibe mensagem quando participante não é encontrado"""
        self.found_inscricao = None
        
        info = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✗ PARTICIPANTE NÃO ENCONTRADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CPF: {cpf}
Evento: {self.current_evento_nome}

Este CPF NÃO está inscrito neste evento.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMO PROCEDER?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ NÃO use o botão verde
   (pessoa não tem inscrição)

✓ Use o botão LARANJA:
  "Inscrição Rápida + Check-in"
  
  → Isso vai criar um cadastro 
     temporário para a pessoa
  
  → Ela poderá completar o 
     cadastro depois no site

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ ATENÇÃO: Se a pessoa diz que
   já se inscreveu no site:
   
   • Verifique se o CPF está correto
   • Verifique se inscreveu neste evento
   • Sincronize os inscritos novamente

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        self._update_info(info)
        self.checkin_btn.configure(state="disabled")
    
    def _show_checkin_ja_existe(self, inscrito: dict, sincronizado: bool):
        """Exibe mensagem quando check-in já existe"""
        self.found_inscricao = None
        
        if sincronizado:
            status = "✓ CHECK-IN JÁ REGISTRADO NO SERVIDOR"
            substatus = "Confirmado no servidor"
        else:
            status = "⚠️ CHECK-IN JÁ REGISTRADO (LOCALMENTE)"
            substatus = "Aguardando sincronização"
        
        info = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{status}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nome: {inscrito['nome']}
CPF: {inscrito['cpf']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ ESTA PESSOA JÁ FEZ CHECK-IN
→ PODE ENTRAR NO EVENTO

{substatus}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        self._update_info(info)
        self.checkin_btn.configure(state="disabled")
    
    def _formatar_resultado_sync(self, resultado: dict) -> str:
        """Formata resultado da sincronização"""
        msg = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        msg += "RESULTADO DA SINCRONIZAÇÃO\n"
        msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        if resultado['sucesso'] > 0:
            msg += f"✓ {resultado['sucesso']} operação(ões) sincronizada(s)\n\n"
        
        if resultado['ja_feito'] > 0:
            msg += f"ℹ️ {resultado['ja_feito']} check-in(s) já realizado(s)\n"
            msg += "→ Essas pessoas podem entrar normalmente\n\n"
        
        if resultado['removidos'] > 0:
            msg += f"🗑️ {resultado['removidos']} erro(s) permanente(s) removido(s)\n\n"
        
        if resultado['falhas'] > 0:
            msg += f"⚠️ {resultado['falhas']} operação(ões) ainda pendente(s)\n\n"
        
        if resultado['total_pendentes'] == 0:
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            msg += "✓ Todas as operações foram processadas!\n"
            msg += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        else:
            msg += f"📊 Total ainda pendente: {resultado['total_pendentes']}"
        
        return msg
    
    
    def _update_info(self, text: str):
        """Atualiza área de informações"""
        self.info_text.configure(state="normal")
        self.info_text.delete("0.0", "end")
        self.info_text.insert("0.0", text)
        self.info_text.configure(state="disabled")
    
    def _limpar_estado(self):
        """Limpa estado da view"""
        self.found_inscricao = None
        self.checkin_btn.configure(state="disabled")
        self.cpf_entry.delete(0, "end")
    
    
    def set_evento(self, evento_id: str, evento_nome: str):
        """Define evento atual (chamado pela MainView)"""
        self.current_evento_id = evento_id
        self.current_evento_nome = evento_nome
        self.event_label.configure(text=f"📍 {evento_nome}")
        
        info_inicial = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EVENTO SELECIONADO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{evento_nome}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMO FAZER CHECK-IN?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Digite o CPF do participante
2. Clique em "Buscar"
3. O sistema mostrará as opções

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
        
        self._update_info(info_inicial)
        self._limpar_estado()