package com.eventosmanager.models;

import java.util.UUID;
import java.time.LocalDateTime;

public class Inscricao {
    public UUID id;
    public UUID usuario_id;
    public UUID evento_id;
    public Boolean inscricao_rapida;
    public String nome_rapido;
    public String email_rapido;
    public String cpf_rapido;
    public String status;
    public LocalDateTime inscrito_em;
    public LocalDateTime cancelado_em;
    public Boolean sincronizado;
}
