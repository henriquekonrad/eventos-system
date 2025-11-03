package com.eventosmanager;

import com.eventosmanager.api.UsuarioApi;
import com.eventosmanager.models.Usuario;

import java.io.IOException;
import java.util.List;

public class Main {
    public static void main(String[] args) {
        try {
            List<Usuario> usuarios = UsuarioApi.listarUsuarios();
            usuarios.forEach(u -> System.out.println(u.nome + " | " + u.email));
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
