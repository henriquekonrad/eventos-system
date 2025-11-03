package com.eventosmanager;

import java.io.IOException;
import java.util.List;

import com.eventosmanager.api.EventoApi;
import com.eventosmanager.models.Evento;

public class Main {
    public static void main(String[] args) {
        try {
            List<Evento> usuarios = EventoApi.listarEventos();
            usuarios.forEach(u -> System.out.println(u.getTitulo() + " | " + u.getDescricao()));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
