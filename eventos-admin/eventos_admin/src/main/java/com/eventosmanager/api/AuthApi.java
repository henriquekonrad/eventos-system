package com.eventosmanager.api;

import java.io.IOException;

import com.eventosmanager.api.api_utils.ServiceType;
import com.eventosmanager.config.AppConfig;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

/**
 * API responsável pela autenticação de usuários.
 * Faz login, guarda o token JWT e permite consultar o perfil.
 */
public class AuthApi {

    private static final Gson gson = new Gson();
    private static final ApiClient apiClient = new ApiClient(ServiceType.AUTH);
    private static final OkHttpClient client = apiClient.getClient();
    private static final String BASE_URL = AppConfig.getBaseUrl(ServiceType.AUTH);
    private static final MediaType JSON = MediaType.parse("application/json; charset=utf-8");

    /**
     * Realiza login com email e senha.
     * Retorna true se sucesso, false caso contrário.
     */
    public static boolean login(String email, String senha) {
        String url = BASE_URL + "/login";

        JsonObject json = new JsonObject();
        json.addProperty("email", email);
        json.addProperty("senha", senha);

        RequestBody body = RequestBody.create(JSON, json.toString());
        Request request = new Request.Builder()
                .url(url)
                .post(body)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                System.err.println("❌ Erro ao fazer login: HTTP " + response.code());
                String errorBody = response.body() != null ? response.body().string() : "(sem corpo)";
                System.err.println("Corpo da resposta: " + errorBody);
                return false;
            }

            String respBody = response.body() != null ? response.body().string() : "";
            JsonObject obj = gson.fromJson(respBody, JsonObject.class);

            if (obj != null && obj.has("access_token")) {
                String token = obj.get("access_token").getAsString();
                ApiClient.setUserAuthToken(token); // 🔥 guarda o token globalmente
                System.out.println("✅ Login bem-sucedido! Token armazenado.");
                return true;
            } else {
                System.err.println("⚠️ Resposta inesperada: " + respBody);
                return false;
            }

        } catch (IOException e) {
            System.err.println("💥 Erro de rede ou conexão: " + e.getMessage());
            return false;
        }
    }

    /**
     * Consulta o perfil do usuário autenticado (/auth/me).
     */
    public static void getProfile() {
        String token = ApiClient.getUserAuthToken(); // precisamos criar este getter
        String url = BASE_URL + "/me?token=" + token;

        System.out.println("🔗 Chamando URL: " + url);

        Request request = new Request.Builder()
                .url(url)
                .get()
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                System.err.println("❌ Erro ao obter perfil: HTTP " + response.code());
                String errorBody = response.body() != null ? response.body().string() : "(sem corpo)";
                System.err.println("Corpo da resposta: " + errorBody);
                return;
            }

            String respBody = response.body() != null ? response.body().string() : "";
            System.out.println("👤 Perfil do usuário: " + respBody);

        } catch (IOException e) {
            System.err.println("💥 Erro de rede ou conexão: " + e.getMessage());
        }
    }
}
