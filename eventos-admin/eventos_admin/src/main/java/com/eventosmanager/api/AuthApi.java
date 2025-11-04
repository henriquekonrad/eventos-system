package com.eventosmanager.api;

import java.io.IOException;

import com.eventosmanager.config.AppConfig;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

import okhttp3.MediaType;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * Responsável por autenticar o usuário (login) e armazenar o token JWT.
 */
public class AuthApi {

    private static final String BASE_URL = AppConfig.get("API_BASE_URL");
    private static final Gson gson = new Gson();

    /**
     * Faz login com email e senha. Retorna true se sucesso.
     */
    public static boolean login(String email, String senha) {
        String url = BASE_URL + "/auth/login";
        MediaType JSON = MediaType.parse("application/json; charset=utf-8");

        JsonObject json = new JsonObject();
        json.addProperty("email", email);
        json.addProperty("senha", senha);

        RequestBody body = RequestBody.create(JSON, json.toString());
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        try (Response response = ApiClient.getClient().newCall(request).execute()) {
            if (!response.isSuccessful()) {
                System.err.println("❌ Erro ao fazer login: " + response.code());
                System.err.println(response.body().string());
                return false;
            }

            String respBody = response.body().string();
            JsonObject obj = gson.fromJson(respBody, JsonObject.class);

            if (obj.has("access_token")) {
                String token = obj.get("access_token").getAsString();
                ApiClient.setUserAuthToken(token);
                System.out.println("✅ Login bem-sucedido!");
                return true;
            } else {
                System.err.println("⚠️ Resposta inesperada: " + respBody);
                return false;
            }

        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }

    /**
     * Consulta /auth/me usando o token atual.
     */
    public static void getProfile() {
        String url = BASE_URL + "/auth/me";
        Request request = new Request.Builder()
                .url(url)
                .get()
                .build();

        try (Response response = ApiClient.getClient().newCall(request).execute()) {
            if (!response.isSuccessful()) {
                System.err.println("❌ Erro ao obter perfil: " + response.code());
                System.err.println(response.body().string());
                return;
            }

            String respBody = response.body().string();
            System.out.println("👤 Perfil: " + respBody);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
