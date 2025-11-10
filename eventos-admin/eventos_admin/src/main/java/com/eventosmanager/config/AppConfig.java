package com.eventosmanager.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import com.eventosmanager.api.api_utils.ServiceType;

public class AppConfig {

    private static final Properties props = new Properties();

    static {
        try (InputStream input = AppConfig.class.getClassLoader().getResourceAsStream("application.properties")) {
            if (input == null) {
                throw new RuntimeException("Arquivo application.properties não encontrado!");
            }
            props.load(input);
        } catch (IOException ex) {
            throw new RuntimeException("Erro ao carregar application.properties", ex);
        }
    }

    public static String get(String key) {
        String value = props.getProperty(key);
        if (value == null || value.trim().isEmpty()) {
            throw new RuntimeException("Chave de configuração ausente ou vazia: " + key);
        }
        return value;
    }

    public static String getBaseUrl(ServiceType service) {
        return get("API_BASE_URL_" + service.name());
    }   

    public static String getApiKey(ServiceType service) {
        return get(service.name() + "_API_KEY");
    }
}