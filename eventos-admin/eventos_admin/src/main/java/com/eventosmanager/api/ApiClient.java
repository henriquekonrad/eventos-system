package com.eventosmanager.api;

import java.io.IOException;

import com.eventosmanager.api.api_utils.ServiceType;
import com.eventosmanager.config.AppConfig;

import okhttp3.Interceptor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

public class ApiClient {

    private final OkHttpClient client;
    private final String apiKey;
    private static String userAuthToken = null;

    public ApiClient(ServiceType service) {
        this.apiKey = AppConfig.getApiKey(service);

        this.client = new OkHttpClient.Builder()
                .addInterceptor(new Interceptor() {
                    @Override
                    public Response intercept(Chain chain) throws IOException {
                        Request original = chain.request();
                        Request.Builder builder = original.newBuilder()
                                .header("Accept", "application/json");

                        // adiciona a API key específica do serviço
                        if (apiKey != null && !apiKey.trim().isEmpty()) {
                            builder.header("x-api-key", apiKey);
                        }

                        // adiciona token JWT do usuário se existir
                        if (userAuthToken != null && !userAuthToken.trim().isEmpty()) {
                            builder.header("Authorization", "Bearer " + userAuthToken);
                        }

                        return chain.proceed(builder.build());
                    }
                })
                .build();
    }

    public OkHttpClient getClient() {
        return client;
    }

    public static void setUserAuthToken(String token) {
        userAuthToken = token;
    }

    public static void clearUserAuthToken() {
        userAuthToken = null;
    }

    public static String getUserAuthToken() {
        return userAuthToken;
    }
}
