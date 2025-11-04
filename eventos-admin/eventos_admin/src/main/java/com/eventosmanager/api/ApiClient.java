package com.eventosmanager.api;

import java.io.IOException;

import com.eventosmanager.config.AppConfig;

import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * Cliente HTTP centralizado que injeta cabeçalhos comuns (API_KEY, Authorization)
 * e expõe o OkHttpClient para uso nas APIs.
 */
public class ApiClient {

    private static final String API_KEY = AppConfig.get("API_KEY");
    private static String userAuthToken = null;

    private static final OkHttpClient client = new OkHttpClient.Builder()
            .addInterceptor(new Interceptor() {
                @Override
                public Response intercept(Chain chain) throws IOException {
                    Request original = chain.request();
                    Request.Builder builder = original.newBuilder()
                            .header("Accept", "application/json");

                    // header para api key (nome acordado com a API backend)
                    if (API_KEY != null && !API_KEY.trim().isEmpty()) {
                        builder.header("x-api-key", API_KEY);
                    }

                    // se existir token de usuário (JWT), adiciona Authorization Bearer
                    if (userAuthToken != null && !userAuthToken.trim().isEmpty()) {
                        builder.header("Authorization", "Bearer " + userAuthToken);
                    }

                    Request requestWithHeaders = builder.build();
                    return chain.proceed(requestWithHeaders);
                }
            })
            .build();

    public static OkHttpClient getClient() {
        return client;
    }

    public static void setUserAuthToken(String token) {
        userAuthToken = token;
    }

    public static void clearUserAuthToken() {
        userAuthToken = null;
    }
}
