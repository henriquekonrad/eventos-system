# ui/checkin_frame.py
import customtkinter as ctk
from db import get_inscrito_by_cpf, add_inscrito_local, add_checkin_local, add_pending, list_pending_requests
from api_client import inscricao_rapida, registrar_checkin, is_online
import uuid

class CheckinFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.current_evento_id = None

        top = ctk.CTkFrame(self)
        top.pack(fill="x", padx=8, pady=8)

        self.event_label = ctk.CTkLabel(top, text="Nenhum evento selecionado", font=("Arial", 14))
        self.event_label.pack(side="left")

        btn_frame = ctk.CTkFrame(top)
        btn_frame.pack(side="right")
        self.sync_btn = ctk.CTkButton(btn_frame, text="Sincronizar pendentes", command=self.sync_now)
        self.sync_btn.pack(side="left", padx=4)

        search_frame = ctk.CTkFrame(self)
        search_frame.pack(fill="x", padx=8, pady=8)

        self.cpf_var = ctk.StringVar()
        cpf_entry = ctk.CTkEntry(search_frame, placeholder_text="CPF do participante", textvariable=self.cpf_var)
        cpf_entry.pack(side="left", padx=(0,8), fill="x", expand=True)

        buscar_btn = ctk.CTkButton(search_frame, text="Buscar", command=self.buscar_por_cpf)
        buscar_btn.pack(side="left", padx=4)

        rapida_btn = ctk.CTkButton(self, text="Inscrição Rápida + Check-in", command=self.inscricao_rapida_prompt)
        rapida_btn.pack(padx=8, pady=(4,8), anchor="w")

        self.info_label = ctk.CTkLabel(self, text="Resultado: —")
        self.info_label.pack(fill="x", padx=8, pady=8)

        # area de ações (check-in)
        actions = ctk.CTkFrame(self)
        actions.pack(fill="x", padx=8, pady=8)
        self.checkin_btn = ctk.CTkButton(actions, text="Registrar Check-in", command=self.registrar_checkin_action, state="disabled")
        self.checkin_btn.pack(side="left")
        self.show_pending_btn = ctk.CTkButton(actions, text="Ver pendentes", command=self.mostrar_pendentes)
        self.show_pending_btn.pack(side="left", padx=8)

        # store found inscricao
        self.found_inscricao = None

    def set_evento(self, evento_id):
        self.current_evento_id = evento_id
        self.event_label.configure(text=f"Evento: {evento_id}")

    def buscar_por_cpf(self):
        cpf = self.cpf_var.get().strip()
        if not cpf:
            self.info_label.configure(text="Digite um CPF válido")
            return
        inscr = get_inscrito_by_cpf(cpf, evento_id=self.current_evento_id) if self.current_evento_id else get_inscrito_by_cpf(cpf)
        if inscr:
            self.found_inscricao = inscr
            self.info_label.configure(text=f"Encontrado localmente: {inscr['nome']} (id: {inscr['inscricao_id']})")
            self.checkin_btn.configure(state="normal")
        else:
            self.found_inscricao = None
            self.info_label.configure(text="Não encontrado localmente.")
            self.checkin_btn.configure(state="disabled")
            # opcional: sugerir inscrição rápida
            self.info_label.configure(text="Não encontrado — use 'Inscrição Rápida + Check-in' se desejar.")

    def inscricao_rapida_prompt(self):
        # simples popup para inserir nome, cpf, email e já realizar check-in local/online
        popup = ctk.CTkToplevel(self)
        popup.title("Inscrição Rápida")
        popup.geometry("420x220")
        name_var = ctk.StringVar()
        cpf_var = ctk.StringVar(value=self.cpf_var.get())
        email_var = ctk.StringVar()

        ctk.CTkLabel(popup, text="Nome").pack(pady=(10,0))
        ctk.CTkEntry(popup, textvariable=name_var).pack(fill="x", padx=12)
        ctk.CTkLabel(popup, text="CPF").pack(pady=(8,0))
        ctk.CTkEntry(popup, textvariable=cpf_var).pack(fill="x", padx=12)
        ctk.CTkLabel(popup, text="Email").pack(pady=(8,0))
        ctk.CTkEntry(popup, textvariable=email_var).pack(fill="x", padx=12)

        def submit():
            nome = name_var.get().strip()
            cpf = cpf_var.get().strip()
            email = email_var.get().strip()
            if not nome or not cpf:
                return
            evento_id = self.current_evento_id
            # cria id temporário local
            local_id = str(uuid.uuid4())
            add_inscrito_local(local_id, evento_id, nome, cpf, email, sincronizado=0)
            # grava pending request para a inscrição rápida (quando online)
            body = {"evento_id": evento_id, "nome_rapido": nome, "cpf_rapido": cpf, "email_rapido": email}
            add_pending("POST", f"http://177.44.248.122:8004/rapida", body)
            # grava check-in local imediato (tipo rapida)
            add_checkin_local(local_id, None, None, evento_id, tipo="rapida", sincronizado=0)
            popup.destroy()
            self.info_label.configure(text=f"Inscrição rápida criada (local id {local_id}) e check-in registrado localmente.")
            self.checkin_btn.configure(state="normal")
            self.found_inscricao = {"inscricao_id": local_id, "nome":nome, "cpf":cpf, "evento_id":evento_id}

        ok = ctk.CTkButton(popup, text="Confirmar e check-in", command=submit)
        ok.pack(pady=12)

    def registrar_checkin_action(self):
        if not self.found_inscricao:
            self.info_label.configure(text="Nenhuma inscrição selecionada.")
            return
        inscricao_id = self.found_inscricao.get("inscricao_id")
        evento_id = self.found_inscricao.get("evento_id") or self.current_evento_id
        # se online, tenta registrar no servidor (usando endpoint de checkins)
        if is_online():
            try:
                # se tiver ingresso_id/usuario_id, poderia usar, mas vamos tentar chamada simples
                # chamamos registrar_checkin com params vazios se não tivermos ingresso_id/usuario_id
                resp = registrar_checkin(inscricao_id, None, None)
                # marca local como sincronizado (simplificado: re-add inscrito com sincronizado=1)
                add_inscrito_local(inscricao_id, evento_id, self.found_inscricao.get("nome","<>"), self.found_inscricao.get("cpf",""), self.found_inscricao.get("email",""), sincronizado=1)
                add_checkin_local(inscricao_id, None, None, evento_id, tipo="normal", sincronizado=1)
                self.info_label.configure(text=f"Check-in registrado online: {resp}")
            except Exception as e:
                # se falhar, grava pending e local
                add_checkin_local(inscricao_id, None, None, evento_id, tipo="normal", sincronizado=0)
                add_pending("POST", f"http://177.44.248.122:8006/", {"inscricao_id":inscricao_id, "ingresso_id": None, "usuario_id": None})
                self.info_label.configure(text=f"Não foi possível registrar online — gravado para sincronizar: {e}")
        else:
            # offline: grava local e pending
            add_checkin_local(inscricao_id, None, None, evento_id, tipo="normal", sincronizado=0)
            add_pending("POST", f"http://177.44.248.122:8006/", {"inscricao_id":inscricao_id, "ingresso_id": None, "usuario_id": None})
            self.info_label.configure(text="Modo offline — check-in gravado localmente e enfileirado para sincronizar.")

    def mostrar_pendentes(self):
        pend = list_pending_requests()
        text = "\n".join([f"{p['id']} {p['method']} {p['url']} {p['created_at']}" for p in pend]) or "(nenhum pendente)"
        popup = ctk.CTkToplevel(self)
        popup.title("Pendentes")
        popup.geometry("600x300")
        t = ctk.CTkTextbox(popup)
        t.pack(fill="both", expand=True, padx=8, pady=8)
        t.insert("0.0", text)
        t.configure(state="disabled")

    def sync_now(self):
        # roda o sync_manager.process_pending se existir; se não, tenta chamada direta simples
        try:
            from sync_manager import process_pending
            process_pending()
            self.info_label.configure(text="Sincronização: tentativa concluída (ver logs).")
        except Exception as e:
            self.info_label.configure(text=f"Erro ao sincronizar: {e}")
