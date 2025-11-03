package com.eventosmanager.models;

import java.util.UUID;
import java.time.LocalDateTime;

public class Usuario {
    public UUID id;
    public String nome;
    public String email;
    public String cpf;
    public Boolean email_verificado;
    public String papel;
    public LocalDateTime criado_em;
    public LocalDateTime atualizado_em;
}
