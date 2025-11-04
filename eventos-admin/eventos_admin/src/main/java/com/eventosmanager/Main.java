package com.eventosmanager;

import com.eventosmanager.api.AuthApi;

public class Main {
    public static void main(String[] args) {
        String email = "admin@empresa.com";
        String senha = "senha123";

        if (AuthApi.login(email, senha)) {
            AuthApi.getProfile();
        }
    }
}
