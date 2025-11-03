package com.eventosmanager.api;

import com.eventosmanager.config.AppConfig;
import com.eventosmanager.models.Usuario;
import com.fasterxml.jackson.databind.ObjectMapper;
import okhttp3.*;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

public class UsuarioApi {
    private static final String BASE_URL = AppConfig.get("API_BASE_URL");
    private static final OkHttpClient client = new OkHttpClient();
    private static final ObjectMapper mapper = new ObjectMapper();

    public static List<Usuario> listarUsuarios() throws IOException {
        Request request = new Request.Builder()
                .url(BASE_URL + "/usuarios/")
                .get()
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erro ao listar usuários: " + response);
            }
            return Arrays.asList(mapper.readValue(response.body().string(), Usuario[].class));
        }
    }

    public static Usuario obterUsuario(String usuarioId) throws IOException {
        Request request = new Request.Builder()
                .url(BASE_URL + "/usuarios/" + usuarioId)
                .get()
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erro ao obter usuário: " + response);
            }
            return mapper.readValue(response.body().string(), Usuario.class);
        }
    }
}
