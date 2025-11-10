package com.eventosmanager.models;

import java.time.LocalDateTime;

/**
 * Model que representa um Check-in.
 * Usado tanto para dados da API quanto do SQLite local.
 */
public class Checkin {
    
    private Integer id; // ID local (SQLite) - null se vier da API
    private String inscricaoId;
    private String ingressoId;
    private String usuarioId;
    private String eventoId;
    private LocalDateTime ocorridoEm;
    private boolean sincronizado;
    
    // Construtores
    public Checkin() {
        this.ocorridoEm = LocalDateTime.now();
        this.sincronizado = false;
    }
    
    public Checkin(String inscricaoId, String ingressoId, String usuarioId, String eventoId) {
        this();
        this.inscricaoId = inscricaoId;
        this.ingressoId = ingressoId;
        this.usuarioId = usuarioId;
        this.eventoId = eventoId;
    }
    
    // Getters e Setters
    public Integer getId() {
        return id;
    }
    
    public void setId(Integer id) {
        this.id = id;
    }
    
    public String getInscricaoId() {
        return inscricaoId;
    }
    
    public void setInscricaoId(String inscricaoId) {
        this.inscricaoId = inscricaoId;
    }
    
    public String getIngressoId() {
        return ingressoId;
    }
    
    public void setIngressoId(String ingressoId) {
        this.ingressoId = ingressoId;
    }
    
    public String getUsuarioId() {
        return usuarioId;
    }
    
    public void setUsuarioId(String usuarioId) {
        this.usuarioId = usuarioId;
    }
    
    public String getEventoId() {
        return eventoId;
    }
    
    public void setEventoId(String eventoId) {
        this.eventoId = eventoId;
    }
    
    public LocalDateTime getOcorridoEm() {
        return ocorridoEm;
    }
    
    public void setOcorridoEm(LocalDateTime ocorridoEm) {
        this.ocorridoEm = ocorridoEm;
    }
    
    public boolean isSincronizado() {
        return sincronizado;
    }
    
    public void setSincronizado(boolean sincronizado) {
        this.sincronizado = sincronizado;
    }
    
    @Override
    public String toString() {
        return "Checkin{" +
                "id=" + id +
                ", inscricaoId='" + inscricaoId + '\'' +
                ", eventoId='" + eventoId + '\'' +
                ", ocorridoEm=" + ocorridoEm +
                ", sincronizado=" + sincronizado +
                '}';
    }
}