package com.eventosmanager.api;

import java.io.IOException;
import java.util.Arrays;
import java.util.List;

import com.eventosmanager.config.AppConfig;
import com.eventosmanager.models.Evento;
import com.fasterxml.jackson.databind.ObjectMapper;

import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class EventoApi {
    private static final String BASE_URL = AppConfig.get("API_BASE_URL");
    private static final OkHttpClient client = ApiClient.getClient();
    private static final ObjectMapper mapper = new ObjectMapper();

    public static List<Evento> listarEventos() throws IOException {
        Request request = new Request.Builder()
                .url(BASE_URL + "/eventos/")
                .get()
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erro ao listar eventos: " + response.code() + " - " + response.message());
            }
            return Arrays.asList(mapper.readValue(response.body().string(), Evento[].class));
        }
    }

    public static Evento obterEvento(String eventoId) throws IOException {
        Request request = new Request.Builder()
                .url(BASE_URL + "/eventos/" + eventoId)
                .get()
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new IOException("Erro ao obter evento: " + response);
            }
            return mapper.readValue(response.body().string(), Evento.class);
        }
    }
}
