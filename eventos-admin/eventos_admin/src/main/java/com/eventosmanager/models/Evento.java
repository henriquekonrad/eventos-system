package com.eventosmanager.models;

public class Evento {
    private String id;
    private String titulo;
    private String descricao;
    private String local;
    private String inicio_em; // use camelCase em Java
    private String fim_em;

    // Construtor vazio
    public Evento() {}

    // Construtor com todos os campos
    public Evento(String id, String titulo, String descricao, String local, String inicio_em, String fim_em) {
        this.id = id;
        this.titulo = titulo;
        this.descricao = descricao;
        this.local = local;
        this.inicio_em = inicio_em;
        this.fim_em = fim_em;
    }

    // Getters e Setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTitulo() { return titulo; }
    public void settitulo(String titulo) { this.titulo = titulo; }

    public String getDescricao() { return descricao; }
    public void setDescricao(String descricao) { this.descricao = descricao; }

    public String getLocal() { return local; }
    public void setLocal(String local) { this.local = local; }

    public String getinicio_em() { return inicio_em; }
    public void setinicio_em(String inicio_em) { this.inicio_em = inicio_em; }

    public String getfim_em() { return fim_em; }
    public void setfim_em(String fim_em) { this.fim_em = fim_em; }

    @Override
    public String toString() {
        return "Evento{" +
                "id='" + id + '\'' +
                ", titulo='" + titulo + '\'' +
                ", descricao='" + descricao + '\'' +
                ", local='" + local + '\'' +
                ", inicio_em='" + inicio_em + '\'' +
                ", fim_em='" + fim_em + '\'' +
                '}';
    }
}
